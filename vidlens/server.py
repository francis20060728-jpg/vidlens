# -*- coding: utf-8 -*-
"""MCP server for fast, text-only visual inspection.

The server reuses the canonical CLI runtime so MCP receives the same provider
failover, local-OCR fallback, URL handling, media preparation, and timeout
behavior as command-line users.
"""
from __future__ import annotations

import asyncio
import importlib.util
import os
from pathlib import Path
import sys
import tempfile

_HERE = Path(__file__).resolve().parent
_PKG_ROOT = _HERE.parent
_RUNTIME_PATH = _PKG_ROOT / "scripts" / "vidlens.py"
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from vidlens.media import find_media_files


def _load_runtime():
    spec = importlib.util.spec_from_file_location("vidlens_runtime", _RUNTIME_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load VidLens runtime: " + str(_RUNTIME_PATH))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_RUNTIME = _load_runtime()


def _look(media_path, prompt=None, prompt_name=None, frame_count=None):
    """Analyze one local/remote image or video through the shared runtime."""
    cfg = _RUNTIME.load_config()
    if not _RUNTIME.config_complete(cfg):
        return "ERROR: Config incomplete. Set api_url, api_key, and model_name."

    with tempfile.TemporaryDirectory(prefix="vidlens-mcp-") as temporary:
        temporary_dir = Path(temporary)
        try:
            if _RUNTIME._is_url(media_path):
                media_file, kind = _RUNTIME._download_url(
                    media_path, temporary_dir, 1)
            else:
                media_file = Path(media_path).expanduser().resolve()
                if not media_file.is_file():
                    return "ERROR: File not found: " + str(media_file)
                kind = _RUNTIME.media_kind(media_file)

            final_prompt = _RUNTIME.resolve_prompt(
                prompt=prompt,
                prompt_name=prompt_name,
                kind=kind,
                count=frame_count or 1,
            )

            if kind == "video":
                return _RUNTIME.analyze_video(
                    cfg, media_file, temporary_dir, 1, final_prompt,
                    frame_count or int(cfg.get("sample_count", 9)))
            prepared = _RUNTIME.prepare_image(media_file, cfg, temporary_dir)
            return _RUNTIME.call_vision(cfg, prepared, "image", final_prompt)
        except Exception as exc:
            return "ERROR: {}".format(exc)


_LOOK_DESC = (
    "SEE and verify one image, screenshot, chart, plot, or video when native "
    "vision is unavailable. If actual image pixels are already in model input, "
    "or the current model/provider is explicitly multimodal, do not call this "
    "tool. For text-only or unknown capability, call it after generating or "
    "changing frontend UI or other visual output. It keeps image bytes outside "
    "the main conversation and returns text only. "
    "Videos become a labeled contact "
    "sheet. Supports local paths and direct media URLs. For fast verification "
    "use prompt_name='verify_page' or 'verify_output', and put the intended "
    "behavior or acceptance criteria in prompt. Ask for a concise PASS/FAIL "
    "verdict and only visible blocking issues; avoid open-ended description "
    "prompts."
)

_LIST_MEDIA_DESC = (
    "List image/video files recursively. Use only when the user wants a media "
    "inventory or you need candidate paths. If you already intend to analyze a "
    "file and know its path, call look instead; if you know only a vague name, "
    "call find_and_look to avoid list_media followed by look. Skips common "
    "dependency/build/VCS directories; returns absolute paths images-first, "
    "then newest-first."
)

_FIND_AND_LOOK_DESC = (
    "Find a media file by name, then visually inspect the best match in one "
    "call. Prefer this over list_media + look when the user says only "
    "'check the dashboard screenshot' or 'look at the demo video'. Use "
    "prompt_name='verify_page'/'verify_output' and a concrete prompt for fast "
    "PASS/FAIL verification. Skip it when native image pixels are already in "
    "the model input."
)


def _tool_definitions():
    try:
        from mcp.types import Tool
    except ImportError:
        sys.stderr.write(
            "MCP SDK not installed. Run: pip install 'mcp>=1.0,<2.0'\n"
            "Or use CLI: python scripts/vidlens.py <media> --task <question>\n")
        sys.exit(1)

    return [
        Tool(
            name="look",
            description=_LOOK_DESC,
            inputSchema={
                "type": "object",
                "properties": {
                    "media_path": {
                        "type": "string",
                        "description": "Absolute local media path or direct media URL",
                    },
                    "prompt": {
                        "type": "string",
                        "description": (
                            "Concrete question or intended result. Combined with "
                            "prompt_name; used alone for a custom question."),
                    },
                    "prompt_name": {
                        "type": "string",
                        "description": (
                            "Review template: verify_page, verify_output, "
                            "describe, quality_check, object_inventory, or "
                            "compare_frames."),
                    },
                    "frame_count": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 24,
                        "description": "Frames sampled from video (default 9)",
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
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20,
                    },
                },
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
                        "description": "Keyword matched against filenames",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Concrete question or intended result (optional)",
                    },
                    "prompt_name": {
                        "type": "string",
                        "description": "Review template (optional)",
                    },
                    "frame_count": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 24,
                        "default": 9,
                    },
                },
                "required": ["directory", "keyword"],
            },
        ),
    ]


def main():
    """Run as an MCP stdio server without blocking the event loop."""
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import TextContent
    except ImportError:
        sys.stderr.write(
            "MCP SDK not installed. Run: pip install 'mcp>=1.0,<2.0'\n"
            "Or use CLI: python scripts/vidlens.py <media> --task <question>\n")
        sys.exit(1)

    server = Server("vidlens")

    @server.list_tools()
    async def list_tools():
        return _tool_definitions()

    @server.call_tool()
    async def call_tool(name, arguments):
        arguments = arguments or {}
        if name == "look":
            text = await asyncio.to_thread(
                _look,
                arguments["media_path"],
                prompt=arguments.get("prompt"),
                prompt_name=arguments.get("prompt_name"),
                frame_count=arguments.get("frame_count"),
            )
            return [TextContent(type="text", text=text)]

        if name == "list_media":
            directory = arguments.get("directory") or os.getcwd()
            files = await asyncio.to_thread(
                find_media_files,
                directory,
                arguments.get("keyword"),
                arguments.get("max_results", 20),
            )
            if not files:
                text = "No media files found in: " + directory
            else:
                text = "Found {} file(s):\n{}".format(len(files), "\n".join(files))
            return [TextContent(type="text", text=text)]

        if name == "find_and_look":
            directory = arguments["directory"]
            keyword = arguments["keyword"]
            files = await asyncio.to_thread(
                find_media_files, directory, keyword, 1)
            if not files:
                text = "No media file matching '{}' found in: {}".format(
                    keyword, directory)
            else:
                found = files[0]
                result = await asyncio.to_thread(
                    _look,
                    found,
                    prompt=arguments.get("prompt"),
                    prompt_name=arguments.get("prompt_name"),
                    frame_count=arguments.get("frame_count"),
                )
                text = "File: {}\n\n{}".format(found, result)
            return [TextContent(type="text", text=text)]

        return [TextContent(type="text", text="Unknown tool: " + name)]

    async def _run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream,
                             server.create_initialization_options())

    asyncio.run(_run())


if __name__ == "__main__":
    main()
