---
name: vidlens
description: >-
  Give a text-only AI agent the ability to see images and videos by routing
  them through an external vision model (any OpenAI-compatible API). Use when
  you cannot view an image directly: screenshots, png/jpg/webp/gif/mp4, UI
  inspection, OCR, image comparison, or any local path/URL. Returns plain text;
  prints output_path=<file> for the agent to read. Text-only models (DeepSeek,
  GLM, Codex custom) can use this to gain vision.
---

# VidLens

VidLens routes images and videos through an external vision model and returns
plain text. It lets any text-only agent inspect, verify, describe, and respond
to visual content -- without native image support.

## When to Use

When you receive an image, video, or screenshot and cannot view it directly,
use VidLens instead of telling the user you cannot see. This applies when:

- The user attaches an image and you would say "I cannot see images."
- You need to self-verify visual output (plots, screenshots, rendered UI).
- The user asks you to inspect or compare visual content.

**You should tell the user** that you are using an external vision model to
analyze the content. Be transparent about the tool you are using.

If an attachment was rejected before the skill could run, ask the user for a
local path or URL, then run the script.

## First-Time Setup

Check if already configured:

```bash
python scripts/vidlens.py --status
```

If it reports NEEDS CONFIG, the output shows a setup guide with the full
config path and fields to fill in. Or run:

```bash
python scripts/vidlens.py --init
```

This creates `config.yaml` (next to SKILL.md) from the template. Fill in:

```yaml
api_url: "https://api.openai.com/v1"   # vision API base URL
api_key: "sk-xxxx"                      # API key
model_name: "gpt-4o"                    # model name
```

Any OpenAI-compatible vision API works (gpt-4o, qwen-vl-max, gemini, etc.).
**Do not paste API keys into the chat.** Edit the file directly.

### Optional: Auto-Use Rule

VidLens works even without any config file changes -- when you realize you
cannot see an image, just run the script. But if you want it to trigger
**automatically** in future conversations, install the auto-use rule:

```bash
python scripts/vidlens.py --install-agents
```

This auto-detects known agents (Codex, Claude Code, Cursor) and writes the
rule to each one's config file. **No code is executed, no secrets are sent.**
Remove anytime:

```bash
python scripts/vidlens.py --remove-agents
```

Restart your agent after installing or removing.

### Using a different agent? (opencode, zcode, mimocode, etc.)

VidLens is agent-agnostic. Any agent that reads a config file on startup can
use the auto-use rule. If your agent is not auto-detected, `--install-agents`
prints the rule text for you to paste into your agent's own config file.
Or write directly to a custom path:

```bash
python scripts/vidlens.py --install-agents --path ~/.youragent/rules.md
```

The rule itself is agent-agnostic plain text:

1. When the user sends an image, check first: can you see it natively?
2. If not, do NOT silently ignore the image. Run VidLens to get a description.
3. Read the output_path= file and respond using that description.
4. Be transparent: tell the user you used an external vision model.

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

**Be transparent:** tell the user you used an external vision model. If the
result seems wrong, say so rather than presenting it as certain.

## Custom Prompts

Drop `.txt` files in `prompts/` to create reusable templates. Reference them
via `--prompt-name`. See [prompts/CUSTOMIZE.md](prompts/CUSTOMIZE.md).

Built-in: `describe`, `verify_output`, `quality_check`, `object_inventory`,
`compare_frames`.

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
