# -*- coding: utf-8 -*-
"""Backward-compatible CLI wrapper: delegates to scripts/vidlens.py.

The standalone script at scripts/vidlens.py is the canonical entry point
with full provider failover, local OCR fallback, and UTF-8 enforcement.
This module redirects 'python -m vidlens' to it for backward compatibility.
"""
import os
import sys


def main():
    _here = os.path.dirname(os.path.abspath(__file__))
    _scripts = os.path.join(os.path.dirname(_here), "scripts")
    _vidlens = os.path.join(_scripts, "vidlens.py")
    os.execv(sys.executable, [sys.executable, _vidlens] + sys.argv[1:])


if __name__ == "__main__":
    main()