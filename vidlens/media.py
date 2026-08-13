# -*- coding: utf-8 -*-
"""Unified media loader: turns any image or video into JPEG bytes."""
from __future__ import annotations

import enum
import math
import os

class MediaKind(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


_STATIC_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}
_VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".m4v"}


# All supported extensions (used by file search).
_ALL_EXTS = _STATIC_EXTS | _VIDEO_EXTS


def detect_kind(path: str) -> MediaKind:
    """Guess media type from file extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext in _VIDEO_EXTS:
        return MediaKind.VIDEO
    return MediaKind.IMAGE


def find_media_files(directory, keyword=None, max_results=20):
    """Recursively search *directory* for image/video files.

    If *keyword* is given, match it case-insensitively against the filename
    (with or without extension).  Returns a list of absolute paths, sorted
    images-first, then by modification time (newest first).
    """
    hits = []
    if not os.path.isdir(directory):
        return hits
    kw = keyword.lower().strip() if keyword else None
    for root, _dirs, files in os.walk(directory):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in _ALL_EXTS:
                continue
            stem = os.path.splitext(fname)[0]
            if kw and kw not in fname.lower() and kw not in stem.lower():
                continue
            full = os.path.join(root, fname)
            try:
                mtime = os.path.getmtime(full)
            except OSError:
                mtime = 0
            hits.append((ext in _STATIC_EXTS, mtime, full))
    hits.sort(key=lambda t: (not t[0], -t[1]))
    return [h[2] for h in hits[:max_results]]


def load_image(path: str, max_side: int = 0) -> bytes:
    """Load a single image, optionally downscale, return JPEG bytes."""
    import cv2
    import numpy as np
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise IOError("Cannot read image: " + path)
    if max_side > 0:
        h, w = img.shape[:2]
        longest = max(h, w)
        if longest > max_side:
            ratio = max_side / longest
            img = cv2.resize(img, (int(w * ratio), int(h * ratio)))
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return buf.tobytes() if ok else b""


def grab_frames(path: str, count: int = 9) -> list:
    """Sample 'count' frames spread across a video timeline.

    Skips the first/last 5 percent to avoid fade-to-black edges.
    """
    import cv2
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise IOError("Cannot open video: " + path)
    try:
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            return []
        count = min(count, total)
        if count <= 1:
            picks = [total // 2]
        else:
            lo = max(1, int(total * 0.05))
            hi = min(total - 1, int(total * 0.95))
            span = hi - lo
            picks = [int(lo + span * i / (count - 1)) for i in range(count)]
        grabbed = []
        for idx in picks:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if ok and frame is not None:
                grabbed.append(frame)
        return grabbed
    finally:
        cap.release()


def stitch_sheet(frames, columns=3, cell_scale=1.0, jpeg_quality=95,
                 show_index=True, max_width=2400):
    """Stitch frame list into a single labeled JPEG contact sheet."""
    import cv2
    import numpy as np
    if not frames:
        return b""
    n = len(frames)
    rows = math.ceil(n / columns)
    src_h, src_w = frames[0].shape[:2]
    cell_w = max(1, int(src_w * cell_scale))
    cell_h = max(1, int(src_h * cell_scale))
    bar_h = 26 if show_index and cell_scale > 0.25 else 0
    sheet_w = columns * cell_w
    sheet_h = rows * (cell_h + bar_h)
    if max_width > 0 and sheet_w > max_width:
        ratio = max_width / sheet_w
        cell_w = max(1, int(cell_w * ratio))
        cell_h = max(1, int(cell_h * ratio))
        sheet_w = columns * cell_w
        sheet_h = rows * (cell_h + bar_h)
    canvas = np.full((sheet_h, sheet_w, 3), 245, dtype=np.uint8)
    for i, raw in enumerate(frames):
        r, c = divmod(i, columns)
        resized = cv2.resize(raw, (cell_w, cell_h))
        y0 = r * (cell_h + bar_h)
        x0 = c * cell_w
        if bar_h > 0:
            cv2.rectangle(canvas, (x0, y0), (x0 + cell_w, y0 + bar_h), (35, 35, 35), -1)
            cv2.putText(canvas, "#{}".format(i + 1),
                        (x0 + 6, y0 + bar_h - 7),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 240, 240), 1, cv2.LINE_AA)
        canvas[y0 + bar_h:y0 + bar_h + cell_h, x0:x0 + cell_w] = resized
    ok, buf = cv2.imencode(".jpg", canvas,
                           [int(cv2.IMWRITE_JPEG_QUALITY), int(jpeg_quality)])
    return buf.tobytes() if ok else b""


def load_media(path, frame_count=9, columns=3, cell_scale=1.0,
               jpeg_quality=95, max_sheet_width=2400, label_frames=True):
    """Unified entry point. Returns (jpeg_bytes, MediaKind).

    Image path: returns the image as JPEG.
    Video path: returns a contact sheet of sampled frames as JPEG.
    """
    kind = detect_kind(path)
    if kind == MediaKind.IMAGE:
        return load_image(path), kind
    frames = grab_frames(path, frame_count)
    sheet = stitch_sheet(frames, columns=columns, cell_scale=cell_scale,
                         jpeg_quality=jpeg_quality, show_index=label_frames,
                         max_width=max_sheet_width)
    return sheet, kind
