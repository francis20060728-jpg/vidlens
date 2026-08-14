---
name: vidlens
description: Give a text-only AI agent vision by routing images/videos through an external vision model. Use when you cannot view an image directly. Returns plain text via output_path=<file>. Zero pip deps for images.
---

# VidLens

See images and videos by routing them through a vision model.

## Run

```bash
python scripts/vidlens.py image.png "What is this?"
```

- Single image, multiple images, or video (needs ffmpeg).
- Question goes as trailing positional arg or --task "..."
- First time? Run --status. If NEEDS CONFIG, run --init, then edit
  config.yaml (api_url, api_key, model_name).
  Full walkthrough: docs/SETUP.md

## Read the result

The script prints output_path=<file>. **Read that file** for the
description. Tell the user you used an external vision model.

## Deeper docs (read on demand)

- Setup details: [docs/SETUP.md](docs/SETUP.md)
- Advanced (failover, reasoning models, OCR, video, MCP): [docs/ADVANCED.md](docs/ADVANCED.md)
- Troubleshooting: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
