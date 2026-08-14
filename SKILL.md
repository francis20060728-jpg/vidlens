---
name: vidlens
description: Vision for text-only agents via external vision model. Use ONLY if you cannot see images natively. MCP tool or CLI. Zero pip deps for images.
---

# VidLens

Vision bridge for text-only agents. Skip if you can already see images.

## Use

- **MCP tool**: call `look(path, prompt)` directly if available.
- **CLI**: `python scripts/vidlens.py <image> "question"`

First time? `--status` / `--init` / edit config.yaml. See [docs/](docs/SETUP.md).

Be transparent: tell the user you used an external vision model.
