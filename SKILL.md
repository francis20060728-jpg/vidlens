---
name: vidlens
description: See and verify images, screenshots, charts, and videos when native vision is unavailable. Use MCP first; CLI only as fallback. Keep checks concise and time-boxed.
---

# VidLens

Vision bridge for text-only agents. Skip if you can already see images.
First confirm model/provider capability. Explicitly multimodal models use
native vision and may load a media path into native input. For text-only or
unknown capability, a path or URL is text and must go through VidLens, which
returns text only. A viewer tool's existence does not prove model support. If
native image input is rejected, do not retry it.

## Use

- **MCP tool**: call `look(path, prompt)` directly if available.
- **CLI**: `python scripts/vidlens.py <image> "question"`

After a frontend or visual-output change, capture the rendered result, verify
once with `prompt_name="verify_page"` or `"verify_output"` plus the intended
behavior, fix blockers, and recheck once. Avoid open-ended descriptions.

First time? `--status` / `--init` / edit config.yaml. See [docs/](docs/SETUP.md).

Be transparent: tell the user you used an external vision model.
