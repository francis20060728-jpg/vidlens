# Setup Guide

First-time configuration for VidLens.

## Prerequisites

- [Python 3](https://python.org) (3.7+, any version)
- An OpenAI-compatible vision API key (gpt-4o, qwen-vl-max, gemini, etc.)
- (Optional) [ffmpeg](https://ffmpeg.org) for video support

## Steps

### 1. Check current status

```bash
python scripts/vidlens.py --status
```

If you see `READY`, you are done. If you see `NEEDS CONFIG`, continue.

### 2. Create config.yaml

```bash
python scripts/vidlens.py --init
```

This copies `config.example.yaml` to `config.yaml` and prints the full path.

### 3. Fill in credentials

Open the printed path and edit three fields:

```yaml
api_url: "https://api.openai.com/v1"   # any OpenAI-compatible endpoint
api_key: "sk-your-key"                  # your API key
model_name: "gpt-4o"                    # a vision-capable model
```

**Do not paste API keys into the chat.** Edit the file directly.

### 4. Verify

```bash
python scripts/vidlens.py --status
```

Should print `READY`.

## Where to get an API key

Any OpenAI-compatible vision API works:

| Provider | Endpoint | Example model |
|----------|----------|---------------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |
| Alibaba (DashScope) | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-vl-max` |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-2.0-flash` |
| OpenRouter | `https://openrouter.ai/api/v1` | `google/gemini-2.0-flash-exp:free` |

## Config reference

| Key | Default | Purpose |
|-----|---------|---------|
| `api_url` | "" | Vision API base URL |
| `api_key` | "" | API key |
| `model_name` | "" | Model name |
| `response_tokens` | 1200 | Max response tokens |
| `verification_tokens` | 350 | Shorter budget for structured PASS/FAIL prompts |
| `sampling_temp` | 0.1 | Temperature (0.1 = factual, 0.7 = creative) |
| `http_timeout` | 45 | Per-provider request timeout in seconds |
| `total_timeout` | 60 | Maximum seconds across provider attempts |
| `reasoning_effort` | empty | Optional low/medium/high provider control |
| `max_image_side` | 1600 | Maximum uploaded image side; 0 disables |
| `image_jpeg_quality` | 90 | JPEG quality for prepared images |
| `is_reasoning_model` | false | Set true for thinking models not in auto-detect |

For fallback providers and advanced options, see [ADVANCED.md](ADVANCED.md).
