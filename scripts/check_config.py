# -*- coding: utf-8 -*-
"""Thin wrapper: delegates to scripts/vidlens.py --status."""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_VIDLENS = os.path.join(_HERE, "vidlens.py")

if __name__ == "__main__":
    os.execv(sys.executable, [sys.executable, _VIDLENS, "--status"])