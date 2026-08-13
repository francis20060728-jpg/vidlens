#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VidLens: give text-only AI agents the ability to see.

Routes images and videos through an external vision model so that agents
without native image support can inspect, verify, and respond to visual
content. Returns plain text; writes a Markdown report and prints
output_path=<file> so the calling agent can read the result.

Zero third-party dependencies for images (Python stdlib only).
Videos use ffmpeg (system binary) when available -- no pip packages needed.
If ffmpeg is absent but opencv is installed, falls back to a contact sheet.

Usage:
    python scripts/vidlens.py image.png "What is in this image?"
    python scripts/vidlens.py image.png --task "What is in this image?"
    python scripts/vidlens.py video.mp4 --prompt-name describe
    python scripts/vidlens.py image.png --output result.md
    python scripts/vidlens.py --install-agents
    python scripts/vidlens.py --status
"""
from __future__ import annotations

import argparse
import base64
import datetime
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Force UTF-8 on Windows to prevent GBK encoding crashes in subprocess calls
# ---------------------------------------------------------------------------

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent
_SKILL_ROOT = _HERE.parent
_CONFIG_PATH = _SKILL_ROOT / "config.yaml"
_PROMPTS_DIR = _SKILL_ROOT / "prompts"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff", ".tif"}
VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".m4v", ".webm"}
MAX_INLINE_BYTES = 72 * 1024 * 1024  # 72 MB upper bound for base64 data URLs

AGENTS_START = "<!-- vidlens:start -->"
AGENTS_END = "<!-- vidlens:end -->"
AGENTS_RULE = """<!-- vidlens:start -->
If the user sends an image, screenshot, video, file path, or URL -- or you would
say "this model does not support image input" / "I cannot see images" -- do NOT
refuse or tell the user you cannot see. Instead, invoke `$vidlens` and run:
  python scripts/vidlens.py <path> --task "<question>"
(or equivalently: python scripts/vidlens.py <path> "<question>")
If an attachment was rejected, ask the user for a local path or URL, then run
the script. After it prints `output_path=...`, read that file for the description.
<!-- vidlens:end -->"""


# ---------------------------------------------------------------------------
# Config loading (stdlib only -- no pyyaml needed)
# ---------------------------------------------------------------------------

def _parse_flat_yaml(path):
    """Minimal YAML reader for flat key:value files."""
    result = {}
    if not Path(path).is_file():
        return result
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ":" not in stripped:
                continue
            key, _, raw = stripped.partition(":")
            key = key.strip()
            raw = raw.strip()
            hash_pos = raw.find(" #")
            if hash_pos > 0:
                raw = raw[:hash_pos].strip()
            if raw.startswith('"'):
                end = raw.find('"', 1)
                raw = raw[1:end] if end > 0 else raw[1:]
            elif raw.startswith("'"):
                end = raw.find("'", 1)
                raw = raw[1:end] if end > 0 else raw[1:]
            if raw == "":
                result[key] = ""
                continue
            low = raw.lower()
            if low in ("true", "yes", "on"):
                result[key] = True
                continue
            if low in ("false", "no", "off"):
                result[key] = False
                continue
            try:
                result[key] = int(raw)
            except ValueError:
                try:
                    result[key] = float(raw)
                except ValueError:
                    result[key] = raw
    return result


def load_config():
    """Load config.yaml, then apply VIDLENS_* env-var overrides."""
    cfg = _parse_flat_yaml(_CONFIG_PATH)
    if os.environ.get("VIDLENS_API_URL"):
        cfg["api_url"] = os.environ["VIDLENS_API_URL"]
    if os.environ.get("VIDLENS_API_KEY"):
        cfg["api_key"] = os.environ["VIDLENS_API_KEY"]
    if os.environ.get("VIDLENS_MODEL"):
        cfg["model_name"] = os.environ["VIDLENS_MODEL"]
    return cfg


def build_provider_chain(cfg):
    """Build an ordered list of (url, key, model) provider tuples.

    Primary provider comes from api_url/api_key/model_name.
    Additional fallbacks come from fallback_N_url/key/model keys.
    Supports up to 9 fallback providers (fallback_1 through fallback_9).
    """
    chain = []
    # Primary
    url = _get(cfg, "api_url", "endpoint")
    key = _get(cfg, "api_key", "secret")
    model = _get(cfg, "model_name", "vision_model", "model")
    if url and model:
        chain.append((url, key, model))
    # Fallbacks
    for i in range(1, 10):
        f_url = cfg.get("fallback_{}_url".format(i), "")
        f_key = cfg.get("fallback_{}_key".format(i), "")
        f_model = cfg.get("fallback_{}_model".format(i), "")
        # Also check env var overrides
        f_url = os.environ.get("VIDLENS_FALLBACK{}_URL".format(i), f_url)
        f_key = os.environ.get("VIDLENS_FALLBACK{}_KEY".format(i), f_key)
        f_model = os.environ.get("VIDLENS_FALLBACK{}_MODEL".format(i), f_model)
        if f_url and f_model:
            chain.append((f_url, f_key, f_model))
    return chain


def _get(cfg, *keys):
    for k in keys:
        val = cfg.get(k)
        if val:
            return val
    return ""


def config_complete(cfg):
    url = _get(cfg, "api_url", "endpoint")
    model = _get(cfg, "model_name", "vision_model", "model")
    return bool(url and model)


# ---------------------------------------------------------------------------
# Positional argument separation (media files vs. question text)
# ---------------------------------------------------------------------------

def _looks_like_media(arg):
    """True if the arg has a recognized image/video extension."""
    ext = Path(arg).suffix.lower()
    return ext in IMAGE_EXTS or ext in VIDEO_EXTS


def separate_media_and_task(raw_media, explicit_task):
    """Split nargs='*' positional args into (media_files, task).

    Since ``media`` uses ``nargs='*'``, every positional argument is swallowed
    as a media path -- including a trailing question string like
    ``"What is in this image?"``.  This function pulls trailing args that are
    neither existing files nor media-extension paths and treats them as the
    task/question text.

    Supports both natural syntaxes:
        vidlens.py image.png "What is this?"        # question as last arg
        vidlens.py image.png --task "What is this?" # explicit --task
    """
    media = []
    task_parts = []
    for arg in reversed(raw_media):
        if Path(arg).exists() or _looks_like_media(arg):
            media.insert(0, arg)
        else:
            task_parts.insert(0, arg)
    inferred = " ".join(task_parts).strip()
    final_task = explicit_task if explicit_task else inferred
    return media, final_task


# ---------------------------------------------------------------------------
# Prompt resolution
# ---------------------------------------------------------------------------

def resolve_prompt(prompt=None, prompt_name=None, kind="image", count=1):
    """Return the text prompt to send to the vision model."""
    if prompt and prompt.strip():
        return prompt.strip()
    if prompt_name:
        path = _PROMPTS_DIR / (prompt_name + ".txt")
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
        print("ERROR: prompt '{}' not found in prompts/".format(prompt_name),
              file=sys.stderr)
        sys.exit(1)
    if kind == "video":
        return (
            "Please fully interpret this video. Summarize the main topic and "
            "describe the key scenes, visible text, and actions in chronological "
            "order. Use timestamps (MM:SS) for important moments. "
            "If you cannot see clearly, say so explicitly."
        )
    if count > 1:
        return (
            "Please examine all of these images together. Describe their key "
            "content, visible text, relationships, and notable differences."
        )
    return (
        "Describe what you observe in this image in detail: objects, people, "
        "text, visual layout, and anything notable."
    )


# ---------------------------------------------------------------------------
# Media type detection and data URL construction
# ---------------------------------------------------------------------------

def media_kind(path):
    ext = Path(path).suffix.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    raise RuntimeError("Unsupported media format: {}".format(ext or "(none)"))


def mime_for(path, kind):
    mime, _ = mimetypes.guess_type(str(path))
    if not mime or not mime.startswith(kind + "/"):
        mime = "image/png" if kind == "image" else "video/mp4"
    return mime


def data_url(path, kind):
    """Read a file and return a base64 data URL."""
    raw = Path(path).read_bytes()
    if len(raw) > MAX_INLINE_BYTES:
        raise RuntimeError(
            "File is too large to encode ({} MB > {} MB limit)".format(
                len(raw) // (1024 * 1024), MAX_INLINE_BYTES // (1024 * 1024)))
    mime = mime_for(path, kind)
    encoded = base64.b64encode(raw).decode("ascii")
    return "data:{};base64,{}".format(mime, encoded)


# ---------------------------------------------------------------------------
# Video preparation via ffmpeg (zero Python deps -- system binary only)
# ---------------------------------------------------------------------------

def probe_video(path):
    """Return basic video metadata via ffprobe, or None if unavailable."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        result = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries",
             "format=duration,size:stream=codec_type,codec_name,width,height",
             "-of", "json", str(path)],
            capture_output=True, text=True, timeout=30, check=True)
        data = json.loads(result.stdout)
        streams = data.get("streams", [])
        video = next((s for s in streams if s.get("codec_type") == "video"), {})
        fmt = data.get("format", {})
        return {
            "duration": float(fmt.get("duration") or 0),
            "size": int(fmt.get("size") or 0),
            "width": int(video.get("width") or 0),
            "height": int(video.get("height") or 0),
            "video_codec": video.get("codec_name", ""),
        }
    except Exception:
        return None


def compress_video(source, destination):
    """Compress video to a reasonable size for API upload via ffmpeg."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found")
    subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
         "-i", str(source),
         "-map", "0:v:0", "-map", "0:a?",
         "-vf", "fps=2,scale='min(1280,iw)':-2:flags=lanczos",
         "-c:v", "libx264", "-preset", "fast", "-crf", "24",
         "-pix_fmt", "yuv420p", "-g", "4",
         "-c:a", "aac", "-b:a", "64k", "-ac", "1",
         "-movflags", "+faststart",
         str(destination)],
        check=True, capture_output=True, text=True, timeout=600)


def prepare_video(path, tmp_dir, index):
    """Compress video if needed. Returns (prepared_path, info_dict)."""
    info = probe_video(path) or {}
    file_size = Path(path).stat().st_size
    needs_compress = (
        file_size > MAX_INLINE_BYTES
        or max(info.get("width", 0), info.get("height", 0)) > 1280
        or info.get("video_codec", "") not in ("", "h264")
        or Path(path).suffix.lower() != ".mp4"
    )
    if not needs_compress:
        return path, {**info, "size": file_size, "prepared": "original"}
    prepared = tmp_dir / "prepared-video-{}.mp4".format(index)
    compress_video(path, prepared)
    new_info = probe_video(prepared) or {}
    return prepared, {**new_info, "size": prepared.stat().st_size,
                       "prepared": "compressed"}


# ---------------------------------------------------------------------------
# Video fallback: contact sheet via opencv (optional, requires pip install)
# ---------------------------------------------------------------------------

def contact_sheet(path, tmp_dir, index, frames=9, columns=3):
    """Build a contact sheet JPEG from sampled frames. Requires opencv."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return None
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return None
    try:
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            return None
        count = min(frames, total)
        if count <= 1:
            picks = [total // 2]
        else:
            lo = max(1, int(total * 0.05))
            hi = min(total - 1, int(total * 0.95))
            picks = [int(lo + (hi - lo) * i / (count - 1)) for i in range(count)]
        grabbed = []
        for idx in picks:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if ok and frame is not None:
                grabbed.append(frame)
        if not grabbed:
            return None
        import math
        n = len(grabbed)
        rows = math.ceil(n / columns)
        h, w = grabbed[0].shape[:2]
        bar_h = 28
        sheet = np.full((rows * (h + bar_h), columns * w, 3), 245, dtype=np.uint8)
        for i, raw_f in enumerate(grabbed):
            r, c = divmod(i, columns)
            y0 = r * (h + bar_h)
            x0 = c * w
            cv2.rectangle(sheet, (x0, y0), (x0 + w, y0 + bar_h), (35, 35, 35), -1)
            cv2.putText(sheet, "#{}".format(i + 1), (x0 + 8, y0 + bar_h - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 240, 240), 1, cv2.LINE_AA)
            sheet[y0 + bar_h:y0 + bar_h + h, x0:x0 + w] = raw_f
        ok, buf = cv2.imencode(".jpg", sheet, [cv2.IMWRITE_JPEG_QUALITY, 90])
        out = tmp_dir / "contact-sheet-{}.jpg".format(index)
        out.write_bytes(buf.tobytes())
        return out
    finally:
        cap.release()


# ---------------------------------------------------------------------------
# Vision API: single-provider call + provider-chain failover
# ---------------------------------------------------------------------------

def _call_one_provider(api_url, api_key, model, media_path, kind, prompt, cfg):
    """Send one media file to one specific provider. Returns text or raises."""
    url_data = data_url(media_path, kind)
    if kind == "video":
        content = [
            {"type": "text", "text": prompt},
            {"type": "video_url", "video_url": {"url": url_data}},
            {"type": "file", "file": {
                "filename": Path(media_path).name, "file_data": url_data}},
        ]
    else:
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": url_data}},
        ]
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": int(cfg.get("response_tokens", 4000)),
        "temperature": float(cfg.get("sampling_temp", 0.1)),
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    endpoint = api_url.rstrip("/") + "/chat/completions"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
    timeout = int(cfg.get("http_timeout", 120))
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        result = json.loads(resp.read().decode("utf-8"))
        choices = result.get("choices", [])
        if not choices:
            err = result.get("error", {})
            msg = err.get("message", str(result))[:500] if isinstance(err, dict) else str(result)[:500]
            raise RuntimeError("API returned no choices: " + msg)
        content_val = choices[0].get("message", {}).get("content")
        if isinstance(content_val, list):
            content_val = "\n".join(
                p.get("text", "") for p in content_val
                if isinstance(p, dict) and p.get("type") == "text")
        text = (content_val or "").strip()
        if not text:
            raise RuntimeError("API returned empty content: " + str(result)[:300])
        return text
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError("HTTP {}: {}".format(exc.code, detail))
    except urllib.error.URLError as exc:
        raise RuntimeError("Connection error: {}".format(exc.reason))


def analyze_image(cfg, media_path, kind, prompt):
    """Full fallback chain: provider chain, then local OCR for images.

    Tries each configured provider in order. If all fail and the media
    is an image, falls back to local OCR (Windows OCR / Tesseract).
    """
    chain = build_provider_chain(cfg)
    if not chain:
        raise ValueError(
            "Config incomplete. Set api_url, api_key, and model_name in: "
            + str(_CONFIG_PATH))
    errors = []
    for i, (url, key, model) in enumerate(chain):
        label = "provider {}".format(i + 1) if i > 0 else "primary"
        print("[{}] {} / {}".format(label, url, model), file=sys.stderr)
        try:
            return _call_one_provider(url, key, model, media_path, kind,
                                      prompt, cfg)
        except Exception as exc:
            errors.append("{}: {}".format(label, exc))
            print("[{}] failed: {}".format(label, exc), file=sys.stderr)
    if kind == "image":
        print("[fallback] trying local OCR ...", file=sys.stderr)
        text = _try_local_ocr(str(media_path))
        if text:
            return text
    raise RuntimeError(
        "All providers failed and no local OCR available.\n"
        "Errors:\n" + "\n".join(errors))


def _try_local_ocr(image_path):
    """Attempt local OCR via Windows OCR or Tesseract. Returns text or None."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "local_ocr", _HERE / "local_ocr.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.local_ocr(image_path)
    except Exception:
        return None


def call_vision(cfg, media_path, kind, prompt, media_count=1):
    """Send media + prompt through the full provider chain."""
    return analyze_image(cfg, media_path, kind, prompt)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def output_file(output_arg, source_name, kind):
    """Determine output path, create dirs."""
    if output_arg:
        p = Path(output_arg).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    root = Path(os.environ.get("VIDLENS_OUTPUT_DIR",
                                str(Path.home() / ".vidlens" / "outputs")))
    day = root / datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        day.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError):
        # Fall back to system temp if home dir is not writable
        root = Path(tempfile.gettempdir()) / "vidlens" / "outputs"
        day = root / datetime.datetime.now().strftime("%Y-%m-%d")
        day.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%H%M%S")
    safe = re.sub(r"[^0-9a-zA-Z._-]+", "-", source_name or kind).strip("-.")[:60]
    return day / "{}__{}__{}.md".format(ts, kind, safe or "media")


# ---------------------------------------------------------------------------
# AGENTS.md injection
# ---------------------------------------------------------------------------

def agents_path():
    return Path.home() / ".codex" / "AGENTS.md"


def install_agents_rule():
    """Write anti-rejection rule into ~/.codex/AGENTS.md (idempotent)."""
    path = agents_path()
    existing = ""
    if path.exists():
        existing = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(AGENTS_START) + r".*?" + re.escape(AGENTS_END),
                         re.DOTALL)
    rule = AGENTS_RULE.strip()
    if pattern.search(existing):
        updated = pattern.sub(rule, existing)
    else:
        updated = existing.rstrip()
        if updated:
            updated += "\n\n"
        updated += rule + "\n"
    if updated != existing:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(".{}.tmp".format(path.name))
        tmp.write_text(updated, encoding="utf-8")
        os.replace(str(tmp), str(path))
        return path, True
    return path, False


def remove_agents_rule():
    """Remove the vidlens block from AGENTS.md."""
    path = agents_path()
    if not path.exists():
        return path, False
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(AGENTS_START) + r".*?" + re.escape(AGENTS_END)
                         + r"\n?", re.DOTALL)
    updated = pattern.sub("", text).rstrip()
    if updated != text.rstrip():
        if updated:
            updated += "\n"
        tmp = path.with_name(".{}.tmp".format(path.name))
        tmp.write_text(updated, encoding="utf-8")
        os.replace(str(tmp), str(path))
        return path, True
    return path, False


def agents_rule_installed():
    path = agents_path()
    if not path.exists():
        return False
    return bool(re.search(re.escape(AGENTS_START),
                           path.read_text(encoding="utf-8")))


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def print_status():
    cfg = load_config()
    print("Config file: " + str(_CONFIG_PATH))
    print("  api_url:    " + (_get(cfg, "api_url", "endpoint") or "(not set)"))
    print("  api_key:    " + ("(set)" if _get(cfg, "api_key", "secret") else "(not set)"))
    print("  model_name: " + (_get(cfg, "model_name", "vision_model", "model") or "(not set)"))
    chain = build_provider_chain(cfg)
    print("  providers:  {} configured".format(len(chain)))
    print("")
    print("Status: " + ("READY" if config_complete(cfg) else "NEEDS CONFIG"))
    print("")
    ffmpeg = shutil.which("ffmpeg")
    print("ffmpeg: " + (ffmpeg or "(not found -- images still work, video needs ffmpeg or opencv)"))
    # Check local OCR availability
    ocr_backends = []
    if os.name == "nt" and shutil.which("powershell"):
        ocr_backends.append("Windows OCR")
    if shutil.which("tesseract"):
        ocr_backends.append("Tesseract")
    ocr_label = ", ".join(ocr_backends) if ocr_backends else "(not found)"
    print("local_ocr: " + ocr_label)
    print("AGENTS.md anti-rejection: " + str(agents_path()))
    print("  " + ("INSTALLED" if agents_rule_installed() else "NOT INSTALLED (run with --install-agents)"))
    return 0 if config_complete(cfg) else 1


# ---------------------------------------------------------------------------
# Video analysis with fallback chain
# ---------------------------------------------------------------------------

def analyze_video(cfg, media_path, tmp_dir, index, prompt, frames):
    """Analyze a video: try ffmpeg path, then opencv contact sheet, then error."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        try:
            prepared, info = prepare_video(media_path, tmp_dir, index)
            size_mb = info.get("size", 0) // (1024 * 1024)
            print("[video {}] sending via ffmpeg ({} MB, {})".format(
                index, size_mb, info.get("prepared", "?")), file=sys.stderr)
            return call_vision(cfg, prepared, "video", prompt)
        except Exception as exc:
            print("[video {}] ffmpeg path failed: {}".format(index, exc),
                  file=sys.stderr)
    print("[video {}] trying contact sheet fallback...".format(index),
          file=sys.stderr)
    sheet = contact_sheet(media_path, tmp_dir, index, frames=frames)
    if sheet:
        return call_vision(cfg, sheet, "image", prompt)
    raise RuntimeError(
        "Cannot process video without ffmpeg or opencv.\n"
        "Install one of:\n"
        "  ffmpeg:  https://ffmpeg.org/download.html (system binary)\n"
        "  opencv:  pip install opencv-python numpy")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="vidlens",
        description="Look at any image or video through an external vision model.")
    parser.add_argument("media", nargs="*", help="Image or video file path(s).")
    parser.add_argument("--task", default="",
                        help="Question or instruction for the vision model.")
    parser.add_argument("--prompt-name", default=None,
                        help="Use a named prompt from prompts/ (e.g. verify_output).")
    parser.add_argument("-o", "--output", default="",
                        help="Output Markdown path. Default: ~/.vidlens/outputs/")
    parser.add_argument("--install-agents", action="store_true",
                        help="Write anti-rejection rule into ~/.codex/AGENTS.md.")
    parser.add_argument("--remove-agents", action="store_true",
                        help="Remove the vidlens rule from ~/.codex/AGENTS.md.")
    parser.add_argument("--status", action="store_true",
                        help="Show configuration status.")
    parser.add_argument("--frames", type=int, default=9,
                        help="Frames for contact-sheet fallback (default 9).")
    args = parser.parse_args()

    if args.status:
        return print_status()
    if args.install_agents:
        path, changed = install_agents_rule()
        print("AGENTS.md: {} {}".format(
            "updated" if changed else "already current", path))
        if changed:
            print("Restart Codex for the rule to take effect.")
        return 0
    if args.remove_agents:
        path, changed = remove_agents_rule()
        print("AGENTS.md: {} {}".format(
            "cleaned" if changed else "nothing to remove", path))
        return 0

    # nargs='*' swallows everything positional including question text.
    # Separate media files from trailing question strings.
    args.media, inferred_task = separate_media_and_task(args.media, args.task)
    if inferred_task and not args.task:
        args.task = inferred_task

    if not args.media:
        parser.error("Provide at least one image or video path, "
                     "or use --status / --install-agents.")

    cfg = load_config()
    if not config_complete(cfg):
        print("ERROR: Config incomplete. Edit:\n  " + str(_CONFIG_PATH)
              + "\nSet api_url, api_key, and model_name.", file=sys.stderr)
        return 1

    prompt = resolve_prompt(args.task, args.prompt_name)

    with tempfile.TemporaryDirectory(prefix="vidlens-") as tmp:
        tmp_dir = Path(tmp)
        results = []
        for index, raw_path in enumerate(args.media, start=1):
            media_path = Path(raw_path).resolve()
            if not media_path.exists():
                print("ERROR: File not found: {}".format(raw_path), file=sys.stderr)
                return 1
            kind = media_kind(media_path)
            if kind == "video":
                text = analyze_video(cfg, media_path, tmp_dir, index, prompt,
                                     args.frames)
            else:
                text = call_vision(cfg, media_path, kind, prompt)
            results.append((media_path, kind, text))

    if len(results) == 1:
        _, kind, text = results[0]
        report = text.strip()
    else:
        sections = ["# VidLens Multi-Media Analysis"]
        for idx, (path, k, text) in enumerate(results, start=1):
            label = "Video" if k == "video" else "Image"
            sections.append("\n## {} {}: {}\n".format(label, idx, path.name))
            sections.append(text.strip())
        report = "\n".join(sections)

    source = Path(args.media[0]).stem
    kind_all = "video" if all(k == "video" for _, k, _ in results) else \
               "image" if all(k == "image" for _, k, _ in results) else "media"
    out = output_file(args.output, source, kind_all)
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    content = (
        "---\ncreated_at: {}\nmedia: {}\n---\n\n".format(
            ts, json.dumps([str(p) for p, _, _ in results], ensure_ascii=False))
        + report + "\n"
    )
    out.write_text(content, encoding="utf-8")
    print("output_path={}".format(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
