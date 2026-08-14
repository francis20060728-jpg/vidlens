# VidLens

**[English](README.md)** | [简体中文](zhcn.md) | [繁體中文](zhtw.md) | [日本語](ja.md) | [한국어](ko.md) | [Français](fr.md) | [Español](es.md) | [Deutsch](de.md) | [Português](pt.md)

---

Give text-only AI agents the ability to see images and videos.

VidLens routes visual files through an external vision model and returns
plain text. Any agent -- Codex, Claude Code, Cursor, Cline -- can inspect,
verify, and respond to visual content without native image support.

> **If your model already supports vision natively, do NOT use VidLens.**
> It is only for text-only models that cannot see images.

## How It Works

```
Image/Video -> base64 encode -> Vision API -> plain text result
```

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

Three tools: `look`, `list_media`, `find_and_look`.

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

The rule checks native vision first: if the model can see images, VidLens is
skipped. MCP tools are preferred over CLI.

## Features

- **Zero pip dependencies for images** (Python stdlib only)
- **MCP server mode** for Claude Desktop, Cursor, Cline
- **Provider failover** (up to 9 fallback providers)
- **Reasoning model support** (mimo-v2.5, o1, o3, deepseek-r1, qwq)
- **Local OCR fallback** (Windows OCR / Tesseract) when all APIs fail
- **Video support** via ffmpeg (system binary) with opencv contact-sheet fallback
- **Custom prompt templates** (drop .txt in prompts/)
- **Multi-provider**: works with any OpenAI-compatible vision API

## Config

| Key | Default | Purpose |
|-----|---------|---------|
| `api_url` | `""` | Vision API base URL |
| `api_key` | `""` | API key |
| `model_name` | `""` | Model name |
| `response_tokens` | `4000` | Max response tokens |
| `sampling_temp` | `0.1` | Temperature (0.1 factual, 0.7 creative) |
| `http_timeout` | `120` | Timeout in seconds |
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
- [Changelog](CHANGELOG.md)

## License

MIT. See [LICENSE](LICENSE).
