# Advanced Features

## Provider Failover

If the primary provider fails (rate limit, timeout, network error), VidLens
tries each fallback provider in order. Up to 9 fallbacks supported.

```yaml
# Primary
api_url: "https://api.openai.com/v1"
api_key: "sk-primary..."
model_name: "gpt-4o"

# Fallbacks
fallback_1_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
fallback_1_key: "sk-alibaba..."
fallback_1_model: "qwen-vl-max"

fallback_2_url: "https://openrouter.ai/api/v1"
fallback_2_key: "sk-openrouter..."
fallback_2_model: "google/gemini-2.0-flash-exp:free"
```

## Reasoning Models

Some models (mimo-v2.5, o1, o3, o4, deepseek-r1, qwq, thinking variants) output
a `reasoning_content` field before the actual answer. This consumes many extra
tokens.

VidLens auto-detects known reasoning model names and triples `max_tokens`
upfront. For models not in the auto-detect list:

```yaml
is_reasoning_model: true
```

If `content` is empty but `reasoning_content` has text, VidLens uses the
reasoning output as the result.

## Latency Controls

VidLens optimizes for bounded response time:

- Images larger than `max_image_side` are downscale-re-encoded before upload.
- `http_timeout` bounds each provider request (default 45 seconds).
- `total_timeout` bounds the entire provider failover chain (default 60 seconds).
- Structured `verify_page`/`verify_output` prompts use `verification_tokens`
  instead of the larger general `response_tokens` budget.

Use `reasoning_effort: low` when the provider supports it. For visual checks,
pass concrete acceptance criteria in `prompt`; avoid broad description requests.

## Local OCR Fallback

When all cloud providers fail for an **image** (not video), VidLens
automatically tries local OCR:

- **Windows**: Windows.Media.Ocr (built into Windows 10+, no install needed)
- **Any OS**: Tesseract CLI (`tesseract` on PATH)

No configuration required. Detected automatically.

## Video Support

Videos need one of:

- **ffmpeg** (preferred): `ffmpeg` on PATH. VidLens compresses the video and
  sends the whole file to the vision API.
- **opencv** (fallback): `pip install opencv-python numpy`. VidLens extracts
  frames into a contact sheet image.

If neither is installed, video analysis fails with a clear error message.

### Video config options (opencv mode only)

```yaml
sample_count: 9       # frames to extract for contact sheet
grid_columns: 3       # contact sheet layout
jpeg_quality: 95      # 0-100
```

Use `--frames N` on the CLI to override `sample_count` per run.

## Custom Prompts

Drop `.txt` files in `prompts/` for reusable question templates:

```bash
# prompts/stage1_detection.txt contains your custom question
python scripts/vidlens.py output/stage1.mp4 --prompt-name stage1_detection
```

Built-in prompts:

- `describe` -- general description
- `verify_output` -- check if build output looks correct
- `quality_check` -- assess image/video quality
- `object_inventory` -- list all objects visible
- `compare_frames` -- compare frames (use with multiple media)
- `verify_page` -- check if a web page renders correctly

See [prompts/CUSTOMIZE.md](../prompts/CUSTOMIZE.md) for writing your own.

## Auto-Use Rule (Agent Integration)

By default, the agent decides when to use VidLens. To make it trigger
automatically whenever visual content arrives:

```bash
python scripts/vidlens.py --install-agents     # auto-detect Codex, Claude Code, Cursor
python scripts/vidlens.py --install-agents --path ~/.youragent/rules.md   # any agent
python scripts/vidlens.py --remove-agents      # remove from all
python scripts/vidlens.py --status             # check per-agent status
```

The rule is capability-first. Explicitly multimodal models use native vision;
text-only or unknown-capability providers route media paths/URLs through
VidLens and receive text only. VidLens use is disclosed to the user.

### Supported agents

| Agent | Config file |
|-------|-------------|
| Codex | `~/.codex/AGENTS.md` |
| Claude Code | `~/.claude/CLAUDE.md` |
| Cursor | `~/.cursor/rules/vidlens.mdc` |
| Any other | use `--path` |

## URL Policy

When a user sends a web page URL:

1. Use your browser tool to **screenshot** the page
2. Pass the screenshot to VidLens

Do NOT auto-download unless the user explicitly asks. Direct image/video URLs
can be passed to VidLens directly.

## MCP Server Mode

For Claude Desktop, Cursor, Cline:

```bash
pip install mcp opencv-python numpy
python vidlens/server.py
```

Three tools: `look`, `list_media`, `find_and_look`.
