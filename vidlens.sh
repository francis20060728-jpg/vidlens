#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="${SCRIPT_DIR}/scripts/vidlens.py"

# Auto-find Python: python3, python, then conda
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        exec "$cmd" "$SCRIPT" "$@"
    fi
done

# Search common conda locations
for conda_py in \
    "$HOME/miniconda3/bin/python3" \
    "$HOME/anaconda3/bin/python3" \
    "$HOME/miniforge3/bin/python3" \
    /opt/homebrew/bin/python3 \
    /usr/local/bin/python3; do
    if [ -x "$conda_py" ]; then
        exec "$conda_py" "$SCRIPT" "$@"
    fi
done

echo "ERROR: Python not found. Install Python 3 or add it to PATH." >&2
exit 1
