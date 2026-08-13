# -*- coding: utf-8 -*-
"""Backward-compatible wrapper: delegates to scripts/vidlens.py."""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_VIDLENS = os.path.join(_HERE, "vidlens.py")

if __name__ == "__main__":
    os.execv(sys.executable, [sys.executable, _VIDLENS] + sys.argv[1:])