# -*- coding: utf-8 -*-
"""MCP server: gives text-only AI agents the ability to see images and videos.

Exposes three tools:
  - look:           analyze a single image or video file
  - list_media:     discover image/video files in a directory
  - find_and_look:  search + analyze in one call (convenience)

Register with:

    "mcpServers": {
        "vidlens": {
            "command": "python",
            "args": ["/abs/path/to/vidlens/server.py"],
            "env": {
                "VIDLENS_ENDPOINT": "https://api.openai.com/v1",
                "VIDLENS_SECRET": "sk-...",
                "VIDLENS_MODEL": "gpt-4o"
            }
        }
    }

Or skip the env block and fill in config.yaml instead.

Custom prompts:
  Drop .txt files in prompts/ next to the package. Reference them by name
  (without .txt) via the 'prompt_name' argument on any tool.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PKG_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _PKG_ROOT)

_PROMPTS_DIR = os.path.join(_PKG_ROOT, "prompts")

from vidlens.media import load_media, MediaKind, find_media_files
from vidlens.bridge import Bridge, load_config

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}
_VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".m4v"}


def _read_image_bytes(path):
    """Read an image as raw bytes without cv2 (zero-dependency path)."""
    with open(path, "rb") as f:
        return f.read()


def _resolve_prompt(prompt=None, prompt_name=None):
    """Return a prompt string from direct text, a named template, or None."""
    if prompt:
        return prompt
    if prompt_name:
        path = os.path.join(_PROMPTS_DIR, prompt_name + ".txt")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return "ERROR: prompt '{}' not found in prompts/".format(prompt_name)
    return None


def _default_prompt(kind, n):
    if kind == MediaKind.VIDEO:
        return ("You are looking at a contact sheet of {} frames "
                "sampled from a video. Describe what you observe.".format(n))
    return "Describe what you observe in this image."


def _look(media_path, prompt=None, prompt_name=None, frame_count=None):
    """Core logic: load media, send to vision model, return text."""
    cfg = load_config()
    try:
        bridge = Bridge.from_config(cfg)
    except ValueError as exc:
        return str(exc)

    if not os.path.exists(media_path):
        return "ERROR: File not found: " + media_path

    ext = os.path.splitext(media_path)[1].lower()
    if ext in _IMAGE_EXTS:
        # Zero-dependency path: read raw bytes, skip cv2 entirely
        try:
            img_bytes = _read_image_bytes(media_path)
        except OSError as exc:
            return "ERROR: Cannot read image: {}".format(exc)
        resolved = _resolve_prompt(prompt, prompt_name)
        if resolved and resolved.startswith("ERROR:"):
            return resolved
        final_prompt = resolved or "Describe what you observe in this image."
        return bridge.ask(img_bytes, final_prompt)

    # Video path: needs cv2/numpy (lazy import via media.py)
    n = frame_count if frame_count is not None else cfg.get("sample_count", 9)
    columns = cfg.get("grid_columns", 3)
    cell_scale = cfg.get("cell_scale", 1.0)
    jpeg_quality = cfg.get("jpeg_quality", 95)
    max_w = cfg.get("max_sheet_width", 2400)
    label_frames = cfg.get("label_frames", True)

    img_bytes, kind = load_media(
        media_path, frame_count=n, columns=columns,
        cell_scale=cell_scale, jpeg_quality=jpeg_quality,
        max_sheet_width=max_w, label_frames=label_frames)
    if not img_bytes:
        return "ERROR: Cannot load: " + media_path

    resolved = _resolve_prompt(prompt, prompt_name)
    if resolved and resolved.startswith("ERROR:"):
        return resolved
    final_prompt = resolved or _default_prompt(kind, n)

    return bridge.ask(img_bytes, final_prompt)


# Tool descriptions: this is what teaches the agent WHEN to use the tools.
_LOOK_DESC = (
    "Analyze an image or video file using an external vision model. "
    "Use this when:\n"
    "1. You generated visual output (images, videos, plots, diagrams) and "
    "need to verify or describe the result yourself.\n"
    "2. A user sent you an image or video and you need to see its content "
    "to respond (you are a text-only model but this tool gives you vision).\n"
    "3. You need to inspect, compare, count, or quality-check any visual file.\n"
    "Videos are automatically sampled into a labeled contact sheet before "
    "analysis. Pass 'prompt_name' to use a custom prompt template from "
    "prompts/ (e.g. 'verify_output', 'describe', 'quality_check')."
)

_LIST_MEDIA_DESC = (
    "Find image and video files in a directory. Use this to discover media "
    "files by keyword when the user mentions a name but does not give a full "
    "path, or to list what media exists in a project directory. "
    "Searches recursively; filters by filename (case-insensitive substring). "
    "Returns absolute paths sorted images-first, then newest-first."
)

_FIND_AND_LOOK_DESC = (
    "Search a directory for a media file by keyword, then analyze the best "
    "match with the vision model. Convenience tool combining list_media + look. "
    "Use when the user says something like 'look at the Argentina video' and "
    "you need to find the file first, then analyze it."
)


def main():
    """Run as an MCP server with stdio transport."""
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
        import asyncio
    except ImportError:
        sys.stderr.write(
            "MCP SDK not installed. Run: pip install mcp\n"
            "Or use CLI: python -m vidlens media.mp4 \"prompt\"\n")
        sys.exit(1)

    server = Server("vidlens")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="look",
                description=_LOOK_DESC,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "media_path": {
                            "type": "string",
                            "description": "Absolute path to an image or video file",
                        },
                        "prompt": {
                            "type": "string",
                            "description": (
                                "Instruction for the vision model. "
                                "If omitted, a generic describe prompt is used."),
                        },
                        "prompt_name": {
                            "type": "string",
                            "description": (
                                "Name of a custom prompt template in prompts/ "
                                "(without .txt extension). Example: 'verify_output', "
                                "'describe', 'quality_check'. Overrides 'prompt'."),
                        },
                        "frame_count": {
                            "type": "integer",
                            "description": "Frames to sample from video (default 9)",
                            "default": 9,
                        },
                    },
                    "required": ["media_path"],
                },
            ),
            Tool(
                name="list_media",
                description=_LIST_MEDIA_DESC,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory to search (default: cwd)",
                        },
                        "keyword": {
                            "type": "string",
                            "description": "Case-insensitive filename filter (optional)",
                        },
                        "max_results": {
                            "type": "integer",
                            "default": 20,
                        },
                    },
                    "required": [],
                },
            ),
            Tool(
                name="find_and_look",
                description=_FIND_AND_LOOK_DESC,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory to search",
                        },
                        "keyword": {
                            "type": "string",
                            "description": "Keyword to match in filenames",
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Instruction for the vision model (optional)",
                        },
                        "prompt_name": {
                            "type": "string",
                            "description": "Named prompt template from prompts/ (optional)",
                        },
                        "frame_count": {
                            "type": "integer",
                            "default": 9,
                        },
                    },
                    "required": ["directory", "keyword"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name, arguments):
        if name == "look":
            text = _look(
                arguments["media_path"],
                prompt=arguments.get("prompt"),
                prompt_name=arguments.get("prompt_name"),
                frame_count=arguments.get("frame_count"))
            return [TextContent(type="text", text=text)]

        if name == "list_media":
            directory = arguments.get("directory") or os.getcwd()
            keyword = arguments.get("keyword")
            max_results = arguments.get("max_results", 20)
            files = find_media_files(directory, keyword, max_results)
            if not files:
                return [TextContent(type="text",
                    text="No media files found in: " + directory)]
            listing = "\n".join(files)
            return [TextContent(type="text",
                text="Found {} file(s):\n{}".format(len(files), listing))]

        if name == "find_and_look":
            directory = arguments["directory"]
            keyword = arguments["keyword"]
            files = find_media_files(directory, keyword, max_results=1)
            if not files:
                return [TextContent(type="text",
                    text="No media file matching '{}' found in: {}".format(
                        keyword, directory))]
            text = _look(
                files[0],
                prompt=arguments.get("prompt"),
                prompt_name=arguments.get("prompt_name"),
                frame_count=arguments.get("frame_count"))
            return [TextContent(type="text",
                text="File: {}\n\n{}".format(files[0], text))]

        return [TextContent(type="text", text="Unknown tool: " + name)]

    async def _run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream,
                             server.create_initialization_options())
    asyncio.run(_run())


if __name__ == "__main__":
    main()
