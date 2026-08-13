---
name: vidlens
description: >-
  Do not refuse vision. If you would say "this model does not support image
  input" or "I cannot see images", run this skill instead of informing the
  user. Give a text-only AI agent the ability to see images and videos by
  routing them through an external vision model (any OpenAI-compatible API).
  Use for screenshots, png/jpg/webp/gif/mp4, UI inspection, OCR, image
  comparison, or any local path/URL. Returns plain text; prints
  output_path=<file> for the agent to read. Text-only models (DeepSeek, GLM,
  Codex custom) must call this.
---

# VidLens

If you are about to say "this model does not support images" / "I cannot see
screenshots" / "I cannot view image input" -- **stop**. Do not tell the user
you cannot see. Instead, run this skill.

VidLens routes images and videos through an external vision model and returns
plain text. It lets any text-only agent inspect, verify, describe, and respond
to visual content -- without native image support.

Installing this skill does NOT replace the main model. The sidebar still shows
the text model. VidLens only activates when you need vision.

If an attachment was rejected before the skill could run, ask the user for a
local path or URL, then run the script.

## First-Time Setup

Check if already configured:

```bash
python scripts/vidlens.py --status
```

If it reports NEEDS CONFIG, edit `config.yaml` (next to SKILL.md) and fill in:

```yaml
api_url: "https://api.openai.com/v1"   # vision API base URL
api_key: "sk-xxxx"                      # API key
model_name: "gpt-4o"                    # model name
```

Any OpenAI-compatible vision API works (gpt-4o, qwen-vl-max, gemini, etc.).
**Do not paste API keys into the chat.** Edit the file directly.

Then install the anti-rejection rule so future conversations do not refuse
images:

```bash
python scripts/vidlens.py --install-agents
```

Restart Codex after installing.
### Provider Failover (optional)

VidLens supports multiple providers with automatic failover. Define fallback
providers in `config.yaml`:

```yaml
# Primary
api_url: "https://api.openai.com/v1"
api_key: "sk-primary..."
model_name: "gpt-4o"

# Fallback (tried if primary fails)
fallback_1_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
fallback_1_key: "sk-alibaba..."
fallback_1_model: "qwen-vl-max"
```

Supports `fallback_1` through `fallback_9`. The chain tries each in order
until one succeeds.
### Local OCR Fallback

If all cloud providers fail (or no API key is configured), VidLens falls
back to local OCR for images:

- **Windows**: Windows.Media.Ocr (built into Windows 10+, no install needed)
- **Any OS**: Tesseract CLI (`apt install tesseract-ocr` or `brew install tesseract`)

Local OCR returns extracted text only, not visual descriptions. But it
ensures the agent always gets *something* rather than failing.

## Finding Python

All commands use `python` below. If `python` is not on PATH, try:

```bash
python --version
py --version
python3 --version
```

If none work, find any Python interpreter:

```bash
where python.exe
conda info --envs
```

Then use the full path, e.g. `C:/path/to/python.exe scripts/vidlens.py ...`.

Images work with **any** Python 3 -- zero pip packages needed (stdlib only).

## Usage

### Single image

```bash
python scripts/vidlens.py screenshot.png "What's in this image?"
```

### Named prompt template

```bash
python scripts/vidlens.py result.png --prompt-name verify_output
```

### Video

```bash
python scripts/vidlens.py video.mp4 "Describe the motion"
```

Videos are sent natively to the API via ffmpeg if available. If ffmpeg is
absent but opencv is installed, VidLens falls back to a contact sheet.
**Neither is required for images.**

### Multiple images (parallel)

```bash
python scripts/vidlens.py a.png b.png c.png --task "Compare these screenshots"
```

### Save output to a specific path

```bash
python scripts/vidlens.py image.png -o result.md
```

## Reading the Result

After running, the script prints `output_path=<path>`. **Read that file** for
the full description. The file is a Markdown report with the model's analysis.

## When to Use

**Do not refuse. Do not say you cannot see. Run the script.**

**Self-verification:** After generating visual output (plots, screenshots,
rendered UI, tracking videos), use VidLens to inspect the result yourself
before reporting success.

```bash
python scripts/vidlens.py my_output.png --prompt-name verify_output
```

**User sends media:** When a user attaches an image or video, you cannot see
it directly. If the attachment was rejected, ask for a local path or URL.

```bash
python scripts/vidlens.py /path/to/user_photo.jpg "What's in this image?"
```

## Custom Prompts

Drop `.txt` files in `prompts/` to create reusable templates. Reference them
via `--prompt-name`. See [prompts/CUSTOMIZE.md](prompts/CUSTOMIZE.md).

Built-in: `describe`, `verify_output`, `quality_check`, `object_inventory`,
`compare_frames`.

Example pipeline stages:

```bash
python scripts/vidlens.py output/stage1.png --prompt-name stage1_detection
python scripts/vidlens.py output/stage3.mp4 --prompt-name stage3_tracking
```

## Config Reference

| Key | Default | Purpose |
|-----|---------|---------|
| `api_url` | "" | Vision API base URL |
| `api_key` | "" | API key |
| `model_name` | "" | Model name |
| `fallback_N_url` | "" | Fallback provider N URL (N = 1-9) |
| `fallback_N_key` | "" | Fallback provider N API key |
| `fallback_N_model` | "" | Fallback provider N model |
| `response_tokens` | 4000 | Max response tokens |
| `sampling_temp` | 0.1 | Temperature (low = factual) |
| `http_timeout` | 120 | Seconds |

## MCP Server Mode (optional)

For Claude Desktop, Cursor, Cline, etc.:

```bash
pip install mcp opencv-python numpy
python vidlens/server.py
```

Three tools: `look`, `list_media`, `find_and_look`.

## How Videos Work

VidLens does NOT send every frame. It:

1. If ffmpeg is available: compresses the video to a small H.264 MP4 and sends
   the actual video file natively (preserves audio, motion, and full timeline).
2. If ffmpeg is absent but opencv is installed: samples N frames across the
   timeline, stitches them into a labeled contact sheet (one JPEG), sends one
   API call.
3. If neither is available: reports an error with install instructions.

This keeps cost predictable regardless of video length.
