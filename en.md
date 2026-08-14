# VidLens


Give text-only AI agents the ability to see images and videos.

VidLens routes visual files through an external vision model and returns
plain text. Any agent -- Codex, Claude Code, Cursor, Cline -- can inspect,
verify, and respond to visual content without native image support.

**Zero pip dependencies for images.** Only Python 3 stdlib required.
Videos use ffmpeg (system binary) if available; opencv is an optional fallback.

**If your model already supports vision natively, do NOT use VidLens.**
It is only for text-only models that cannot see images.

## Prerequisites

- [Python 3](https://python.org) (3.7+)
- An OpenAI-compatible vision API key (gpt-4o, qwen-vl-max, gemini, etc.)
- (Optional) [ffmpeg](https://ffmpeg.org) for video support

## Quick Start: MCP Server (recommended)

MCP is the fastest way to use VidLens -- no process startup, no sandbox delays.

```bash
pip install mcp>=1.0,<2.0 opencv-python numpy
python scripts/vidlens.py --init     # create config.yaml
# Edit config.yaml: api_url, api_key, model_name
python vidlens/server.py             # start MCP server
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
python scripts/vidlens.py --init     # create config.yaml
# Edit config.yaml: api_url, api_key, model_name
python scripts/vidlens.py --status   # verify
python scripts/vidlens.py photo.png "What's in this image?"
```

## Auto-Use Rule (Codex / Claude Code)

```bash
python scripts/vidlens.py --install-agents   # auto-detect agent config files
python scripts/vidlens.py --remove-agents    # remove from all
```

The rule checks native vision first: if the model can see images, VidLens is
skipped. Only text-only models trigger it.

## Config

| Key | Default | Purpose |
|-----|---------|---------|
| `api_url` | "" | Vision API base URL |
| `api_key` | "" | API key |
| `model_name` | "" | Model name |
| `response_tokens` | 4000 | Max response tokens |
| `sampling_temp` | 0.1 | Temperature |
| `is_reasoning_model` | false | Set true for thinking models |

Any OpenAI-compatible vision API works.

## License

MIT. See [LICENSE](LICENSE).
