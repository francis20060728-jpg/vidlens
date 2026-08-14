# VidLens

**[English](README.md)** | [简体中文](zhcn.md) | [繁體中文](zhtw.md) | [日本語](ja.md) | [한국어](ko.md) | [Français](fr.md) | [Español](es.md) | [Deutsch](de.md) | [Português](pt.md)

---

Give text-only AI agents the ability to see images and videos.

VidLens routes visual files through an external vision model and returns
plain text. Any agent -- Codex, Claude Code, Cursor, Cline -- can inspect,
verify, and respond to visual content without native image support.

> **If the current model/provider is explicitly multimodal, use native vision.**
> For text-only or unknown capability, use VidLens and keep image bytes outside the main conversation.

## How It Works

```
Image/Video -> base64 encode -> Vision API -> plain text result
```

## One-Click Deploy (ask your AI agent)

Tell your agent:

> Install vidlens from https://github.com/francis20060728-jpg/vidlens and configure it for me.

The agent will clone the repo, run --init, and help you fill in config.yaml.

## Prerequisites

- [Python 3](https://python.org) (3.7+, any version)
- An OpenAI-compatible vision API key (gpt-4o, qwen-vl-max, gemini, etc.)
- (Optional) [ffmpeg](https://ffmpeg.org) for video support

## Quick Start: MCP Server (recommended)

MCP is the fastest way to use VidLens -- no process startup, no sandbox delays.

```bash
# 1. Install
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
pip install "mcp>=1.0,<2.0" opencv-python numpy

# 2. Configure
python scripts/vidlens.py --init
# Edit config.yaml: api_url, api_key, model_name

# 3. Run MCP server
python vidlens/server.py
```

Register in your MCP client (Claude Desktop, Cursor, Cline):

```json
{
  "mcpServers": {
    "vidlens": {
      "command": "python",
      "args": ["/abs/path/to/vidlens/vidlens/server.py"]
    }
  }
}
```

### MCP Tools

| Tool | Description | Key Arguments |
|------|-------------|---------------|
| `look` | Analyze a single image or video file with the vision model. Videos are auto-sampled into a labeled contact sheet. | `media_path` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional, default 9) |
| `list_media` | Find image and video files in a directory. Searches recursively, filters by filename keyword. Returns absolute paths sorted images-first. | `directory` (optional, default cwd), `keyword` (optional), `max_results` (optional, default 20) |
| `find_and_look` | Search a directory by keyword, then analyze the best match in one call. Convenience combo of list_media + look. | `directory` (required), `keyword` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional) |

Example: `look(media_path="chart.png", prompt="What is this chart showing?")`

## Quick Start: CLI (fallback for non-MCP agents)

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
# Edit config.yaml: api_url, api_key, model_name
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "What's in this image?"
```

The result prints to stdout directly. No need to read a separate file.

## Auto-Use Rule (Codex)

```bash
python scripts/vidlens.py --install-agents   # writes to ~/.codex/AGENTS.md
python scripts/vidlens.py --remove-agents    # remove
python scripts/vidlens.py --status           # check
```

The rule first checks actual model/provider capability. Explicitly multimodal
models use native vision and may load a media path into native input;
text-only or unknown-capability providers route through VidLens, which returns
text only. A rejected native-image request is not retried.

## Features

- **Zero pip dependencies for images** (Python stdlib only)
- **MCP server mode** for Claude Desktop, Cursor, Cline
- **Provider failover** (up to 9 fallback providers)
- **Reasoning model support** (auto-detects thinking/reasoning models)
- **Local OCR fallback** (Windows OCR / Tesseract) when all APIs fail
- **Video support** via ffmpeg (system binary) with opencv contact-sheet fallback
- **Custom prompt templates** (drop .txt in prompts/)
- **Multi-provider**: works with any OpenAI-compatible vision API
- **Text-safe bridge**: image bytes stay outside the main text-model conversation
- **Fast verification prompts**: concise PASS/FAIL evidence plus one next fix
- **Latency controls**: image downsampling, bounded retries, per-request and total timeouts

## Config

| Key | Default | Purpose |
|-----|---------|---------|
| `api_url` | `""` | Vision API base URL |
| `api_key` | `""` | API key |
| `model_name` | `""` | Model name |
| `response_tokens` | `1200` | Max response tokens |
| `verification_tokens` | `350` | Shorter budget for structured PASS/FAIL prompts |
| `sampling_temp` | `0.1` | Temperature (0.1 factual, 0.7 creative) |
| `http_timeout` | `45` | Per-provider timeout in seconds |
| `total_timeout` | `60` | Maximum time across all provider attempts |
| `reasoning_effort` | `""` | Optional low/medium/high provider control |
| `max_image_side` | `1600` | Maximum uploaded image side (0 disables) |
| `image_jpeg_quality` | `90` | JPEG quality for prepared images |
| `is_reasoning_model` | `false` | Set true for thinking models |
| `fallback_N_url` | `""` | Fallback provider N URL (N=1-9) |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `NEEDS CONFIG` | Run `--init`, fill config.yaml, then `--status` |
| `python: not found` | Use launcher (`vidlens.cmd` / `vidlens.sh`) |
| Video fails | Install ffmpeg or `pip install opencv-python numpy` |
| First run slow | Sandbox approving network -- only happens once |

Full troubleshooting: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Documentation

- [Setup Guide](docs/SETUP.md)
- [Advanced Features](docs/ADVANCED.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Testing and Boundaries](docs/TESTING.md)
- [Changelog](CHANGELOG.md)

## Contact

Questions or suggestions? Email **francis20060728@gmail.com**.

## License

MIT. See [LICENSE](LICENSE).
