# -*- coding: utf-8 -*-
"""VidLens package: vision bridge for text-only AI agents.

The primary entry point is scripts/vidlens.py (standalone, zero dependencies).
This package provides the MCP server and reusable components.
"""
from .media import load_media, MediaKind
from .bridge import Bridge
from .media import find_media_files
__version__ = "1.2.0"
__all__ = ["load_media", "MediaKind", "Bridge", "find_media_files", "__version__"]