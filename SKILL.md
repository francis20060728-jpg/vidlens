---
name: vidlens
description: Give a text-only AI agent vision by routing images/videos through an external vision model. Use when you cannot view an image directly. Returns plain text via output_path=<file>. Zero pip deps for images.
---

# VidLens

Give text-only agents the ability to see images and videos. Zero pip deps
for images (Python stdlib only).

## First-Time Setup

```bash
python scripts/vidlens.py --status   # check if configured
python scripts/vidlens.py --init     # create config.yaml from template
```

If NEEDS CONFIG, run `--init` then edit config.yaml (api_url, api_key,
model_name). Full details in the --status output.
**Do not paste API keys into the chat.** Edit the file directly.

## Usage

```bash
python scripts/vidlens.py image.png "What is this?"             # single image
python scripts/vidlens.py video.mp4 "Describe the motion"        # video (ffmpeg)
python scripts/vidlens.py a.png b.png --task "Compare these"    # multiple
python scripts/vidlens.py image.png --prompt-name verify_output  # named prompt
python scripts/vidlens.py image.png -o result.md                 # custom output
```

## Reading the Result

The script prints `output_path=<file>`. **Read that file** for the full
description. Be transparent: tell the user you used an external vision model.

## More

- URL policy: screenshot via browser tool first, do NOT auto-download.
- Auto-use rule: `--install-agents` (multi-agent), `--remove-agents`.
- Provider failover: fallback_1 through fallback_9 in config.yaml.
- Local OCR fallback (Windows OCR / Tesseract) when all providers fail.
- Custom prompts: drop `.txt` in `prompts/`, use via `--prompt-name`.
- Full docs: [README.md](README.md) | [CHANGELOG.md](CHANGELOG.md)
