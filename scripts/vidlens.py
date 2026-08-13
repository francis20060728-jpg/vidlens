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
MAX_DOWNLOAD_BYTES = 50 * 1024 * 1024  # 50 MB cap for URL downloads

TRIGGER_SCENARIOS = """<!-- vidlens:start -->
## VidLens vision bridge (auto)

VidLens lets you SEE images, videos, and web pages by routing them through an
external vision model. Use it whenever you encounter visual content you cannot
natively inspect.

## When to trigger VidLens

TRIGGER when ANY of these happen:
1. User sends an image, screenshot, or video file.
2. User sends a URL to a web page, image, or video -- download or screenshot it
   first, then analyze with VidLens to check if the page renders correctly,
   looks broken, or has the expected content.
3. User discusses UI layout, design, charts, graphs, plots, or anything visual.
4. You generated visual output (build screenshots, rendered pages, plots) and
   need to self-verify it looks right.
5. User asks "does this look right?" or "is this broken?" about anything visual.
6. User mentions a color, layout, alignment, or visual element.

## How to run
   python {skill_root}/scripts/vidlens.py <path-or-url> --task "<question>"

## Rules
- CHECK FIRST: can you see it natively? If yes, skip VidLens.
- If you cannot see it: do NOT silently ignore the image/URL. Run VidLens.
- After it prints output_path=, READ that file for the description.
- Be transparent: tell the user you used an external vision model.
- For web page URLs: use your browser tool to screenshot, then pass the
  screenshot to VidLens. Or pass the URL directly if it links to an image/video.
<!-- vidlens:end -->"""

AGENTS_START = "<!-- vidlens:start -->"
AGENTS_END = "<!-- vidlens:end -->"
AGENTS_RULE = TRIGGER_SCENARIOS


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
            key = key.strip().lstrip("\ufeff").rstrip("\ufeff")
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


def _is_url(arg):
    """True if the arg looks like an http(s) URL."""
    return arg.startswith("http://") or arg.startswith("https://")


def _download_url(url, tmp_dir, index):
    """Download a media file from a URL to tmp_dir. Returns (path, kind)."""
    print("[url {}] downloading {} ...".format(index, url[:120]), file=sys.stderr)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VidLens/1.0"})
        resp = urllib.request.urlopen(req, timeout=60)
        content_type = resp.headers.get("Content-Type", "")
        data = resp.read(MAX_DOWNLOAD_BYTES + 1)
        if len(data) > MAX_DOWNLOAD_BYTES:
            raise RuntimeError("Download too large ({} > {} MB)".format(
                len(data) // (1024 * 1024), MAX_DOWNLOAD_BYTES // (1024 * 1024)))
    except Exception as exc:
        raise RuntimeError("Download failed: {}".format(exc))
    # Determine extension from content-type or URL
    ext_map = {
        "image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp",
        "image/gif": ".gif", "image/bmp": ".bmp", "image/tiff": ".tiff",
        "video/mp4": ".mp4", "video/webm": ".webm", "video/quicktime": ".mov",
        "video/x-msvideo": ".avi",
    }
    ext = ext_map.get(content_type.split(";")[0].strip(), "")
    if not ext:
        url_ext = Path(url.split("?")[0]).suffix.lower()
        if url_ext in IMAGE_EXTS or url_ext in VIDEO_EXTS:
            ext = url_ext
        else:
            ext = ".png"  # assume image
    kind = "video" if ext in VIDEO_EXTS else "image"
    safe_name = "download-{}{}".format(index, ext)
    out = tmp_dir / safe_name
    out.write_bytes(data)
    print("[url {}] saved {} ({} bytes, {})".format(
        index, safe_name, len(data), content_type), file=sys.stderr)
    return out, kind


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
        if _is_url(arg) or Path(arg).exists() or _looks_like_media(arg):
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

REASONING_MODEL_HINTS = (
    "o1", "o3", "o4",          # OpenAI o-series
    "mimo",                     # Xiaomi MiMo
    "deepseek-r1", "deepseek-reasoner",  # DeepSeek
    "qwq",                      # Qwen QwQ
    "thinking",                 # generic suffix
)


def _is_reasoning_model(model_name, cfg):
    """True if the model is a reasoning/thinking model.

    Checks explicit config override first, then matches known model names.
    """
    if cfg.get("is_reasoning_model"):
        return True
    name = (model_name or "").lower()
    return any(hint in name for hint in REASONING_MODEL_HINTS)


def _call_one_provider(api_url, api_key, model, media_path, kind, prompt, cfg,
                     ):
    """Send one media file to one specific provider. Returns text or raises.

    Handles reasoning/thinking models (o1, mimo-v2.5, etc.) that output
    ``reasoning_content`` before actual ``content``. Reasoning models get a
    tripled token budget from the start so they have room to finish thinking
    and produce a real answer -- no wasteful retry.
    """
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
    base_tokens = int(cfg.get("response_tokens", 4000))
    # Reasoning models need more room from the start (no wasteful retry)
    if _is_reasoning_model(model, cfg):
        base_tokens *= 3
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": base_tokens,
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
        msg_obj = choices[0].get("message", {})
        content_val = msg_obj.get("content")
        reasoning_val = msg_obj.get("reasoning_content", "")
        if isinstance(content_val, list):
            content_val = "\n".join(
                p.get("text", "") for p in content_val
                if isinstance(p, dict) and p.get("type") == "text")
        text = (content_val or "").strip()
        # If content is empty but reasoning_content exists, use it as fallback
        if not text and reasoning_val:
            print("[reasoning] content empty, using reasoning_content "
                  "as fallback result", file=sys.stderr)
            text = reasoning_val.strip()
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
    """Return the Codex AGENTS.md path."""
    return Path.home() / ".codex" / "AGENTS.md"


# Known agent config files. New agents are discovered by SKILL.md
# self-install instructions -- the agent itself knows its config path.
AGENT_CONFIGS = {
    "codex": Path.home() / ".codex" / "AGENTS.md",
    "claude_code": Path.home() / ".claude" / "CLAUDE.md",
    "cursor": Path.home() / ".cursor" / "rules" / "vidlens.mdc",
}


def detect_agents():
    """Return list of (name, path) for agents whose directory exists."""
    found = []
    for name, path in AGENT_CONFIGS.items():
        if path.parent.exists() or path.exists():
            found.append((name, path))
    return found


def _write_rule_to_file(path, rule_text):
    """Insert or update the vidlens rule block in a config file. Returns True if changed."""
    existing = ""
    if path.exists():
        existing = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(AGENTS_START) + r".*?" + re.escape(AGENTS_END),
                         re.DOTALL)
    if pattern.search(existing):
        updated = pattern.sub(rule_text, existing)
    else:
        updated = existing.rstrip()
        if updated:
            updated += "\n\n"
        updated += rule_text + "\n"
    if updated != existing:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(".{}.tmp".format(path.name))
        tmp.write_text(updated, encoding="utf-8")
        os.replace(str(tmp), str(path))
        return True
    return False


def install_agents_rule():
    """Write the rule into all detected agent config files. Returns (results, rule_text)."""
    # Use forward slashes so the path works in any shell on any OS
    skill_root = str(_SKILL_ROOT).replace("\\", "/")
    rule_text = AGENTS_RULE.strip().replace("{skill_root}", skill_root)
    agents = detect_agents()
    results = []
    for name, path in agents:
        changed = _write_rule_to_file(path, rule_text)
        results.append((name, path, changed))
    return results, rule_text


def install_to_path(custom_path):
    """Write the rule to a user-specified config file path."""
    skill_root = str(_SKILL_ROOT).replace("\\", "/")
    rule_text = AGENTS_RULE.strip().replace("{skill_root}", skill_root)
    path = Path(custom_path).expanduser()
    changed = _write_rule_to_file(path, rule_text)
    return path, changed, rule_text

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
    """Remove the vidlens block from all detected agent config files."""
    agents = detect_agents()
    results = []
    for name, path in agents:
        if not path.exists():
            results.append((name, path, False))
            continue
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
            results.append((name, path, True))
        else:
            results.append((name, path, False))
    return results
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


def agents_rule_status():
    """Return list of (name, path, installed) for all detected agents."""
    agents = detect_agents()
    status = []
    for name, path in agents:
        if path.exists():
            installed = bool(re.search(re.escape(AGENTS_START),
                             path.read_text(encoding="utf-8")))
        else:
            installed = False
        status.append((name, path, installed))
    return status


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
    print("")
    print("Agent rules:")
    status = agents_rule_status()
    if status:
        for name, path, installed in status:
            tag = "INSTALLED" if installed else "NOT INSTALLED"
            print("  {} ({}): {}".format(name, path, tag))
    else:
        print("  (no agent config dirs detected)")
    print("  Install with: python scripts/vidlens.py --install-agents")
    if not config_complete(cfg):
        print("")
        print_setup_guide()
    return 0 if config_complete(cfg) else 1


# ---------------------------------------------------------------------------
# Setup / first-run guidance
# ---------------------------------------------------------------------------

def print_setup_guide():
    """Print a clear, actionable setup guide with the full config path."""
    print("=" * 60)
    print("  VidLens Setup Guide")
    print("=" * 60)
    print("")

    config_exists = _CONFIG_PATH.exists()
    example_path = _SKILL_ROOT / "config.example.yaml"
    step = 1

    if not config_exists:
        if example_path.exists():
            print("Step {}: Create config.yaml from the template".format(step))
            step += 1
            print("")
            if os.name == "nt":
                print('  copy "{}" "{}"'.format(example_path, _CONFIG_PATH))
            else:
                print('  cp "{}" "{}"'.format(example_path, _CONFIG_PATH))
            print("")
        else:
            print("Step {}: Create config.yaml at this path".format(step))
            step += 1
            print("")

    print("Step {}: Edit this file".format(step))
    step += 1
    print("")
    print("  " + str(_CONFIG_PATH))
    print("")
    print("Step {}: Fill in these three fields".format(step))
    step += 1
    print("")
    print('  api_url:     "https://api.openai.com/v1"   # any OpenAI-compatible URL')
    print('  api_key:     "sk-your-key-here"            # your API key')
    print('  model_name:  "gpt-4o"                      # vision model name')
    print("")
    print("Works with gpt-4o, qwen-vl-max, gemini, mimo-v2.5, or any")
    print("other OpenAI-compatible vision model.")
    print("")
    print("After editing, run this again to verify:")
    print("  python scripts/vidlens.py --status")
    print("=" * 60)


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
                        help="Write vision rule to detected agent config files.")
    parser.add_argument("--path", default="",
                        help="Custom config file path for --install-agents.")
    parser.add_argument("--remove-agents", action="store_true",
                        help="Remove the vidlens rule from detected agent configs.")
    parser.add_argument("--status", action="store_true",
                        help="Show configuration status.")
    parser.add_argument("--init", action="store_true",
                        help="Create config.yaml from template and show setup guide.")
    parser.add_argument("--frames", type=int, default=9,
                        help="Frames for contact-sheet fallback (default 9).")
    args = parser.parse_args()

    if args.status:
        return print_status()
    if args.init:
        example = _SKILL_ROOT / "config.example.yaml"
        if _CONFIG_PATH.exists():
            print("config.yaml already exists: " + str(_CONFIG_PATH))
        elif example.exists():
            import shutil as _sh
            _sh.copy2(str(example), str(_CONFIG_PATH))
            print("Created config.yaml from template: " + str(_CONFIG_PATH))
        else:
            _CONFIG_PATH.write_text(
                'api_url: ""\napi_key: ""\nmodel_name: ""\n',
                encoding="utf-8")
            print("Created config.yaml: " + str(_CONFIG_PATH))
        print("")
        print_setup_guide()
        return 0
    if args.install_agents:
        if args.path:
            path, changed, rule_text = install_to_path(args.path)
            label = "updated" if changed else "already current"
            print("  custom: {} -> {}".format(label, path))
            print("Restart your agent for the rule to take effect.")
            return 0
        results, rule_text = install_agents_rule()
        if not results:
            print("No agent config directories detected (checked ~/.codex, ~/.claude, ~/.cursor).")
            print("")
            print("If you use a different agent (opencode, zcode, mimocode, etc.),")
            print("add this rule to your agent's config file manually:")
            print("")
            print(rule_text)
        else:
            for name, path, changed in results:
                label = "updated" if changed else "already current"
                print("  {}: {} -> {}".format(name, label, path))
            print("")
            if any(c for _, _, c in results):
                print("Restart your agent(s) for the rule to take effect.")
            print("Note: Using an agent not listed above? The rule is agent-agnostic.")
            print("Paste it into your agent's own config file -- see SKILL.md.")
        return 0
    if args.remove_agents:
        results = remove_agents_rule()
        if not results:
            print("No agent config directories detected.")
        else:
            for name, path, changed in results:
                label = "cleaned" if changed else "nothing to remove"
                print("  {}: {} -> {}".format(name, label, path))
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
        print("ERROR: Config incomplete.", file=sys.stderr)
        print("", file=sys.stderr)
        print_setup_guide()
        return 1

    prompt = resolve_prompt(args.task, args.prompt_name)

    with tempfile.TemporaryDirectory(prefix="vidlens-") as tmp:
        tmp_dir = Path(tmp)
        results = []
        for index, raw_path in enumerate(args.media, start=1):
            # Handle URLs: download first, then process as local file
            if _is_url(raw_path):
                try:
                    media_path, kind = _download_url(raw_path, tmp_dir, index)
                except RuntimeError as exc:
                    print("ERROR: {}".format(exc), file=sys.stderr)
                    return 1
            else:
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

    first = args.media[0]
    source = Path(first.split("?")[0].split("/")[-1]).stem if _is_url(first) \
        else Path(first).stem
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
