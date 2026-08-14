# Troubleshooting

| Problem | Fix |
|---------|-----|
| `python: command not found` | Use the launcher (`vidlens.cmd` / `vidlens.sh`) which auto-finds Python, or add Python to PATH |
| `NEEDS CONFIG` | Run `python scripts/vidlens.py --init`, fill in `config.yaml`, then `--status`. See [SETUP.md](SETUP.md) |
| `config.yaml not found` | Run `--init` to create it from the template |
| API returns 401 / 403 | Check `api_key` is correct and has vision model access |
| API returns 404 | Check `api_url` ends with `/v1` (or the correct API version path) |
| API returns 429 | Rate limited. Set up a fallback provider in `config.yaml` |
| Video fails | Install [ffmpeg](https://ffmpeg.org) (preferred) or `pip install opencv-python numpy` |
| All providers failed | A local OCR fallback kicks in for images. Check your API key and URL. |
| Chinese path garbled | Fixed since v1.2 -- stdout/stderr forced to UTF-8 on Windows |
| Very slow / appears stuck | Set `reasoning_effort: low` when supported, keep `response_tokens` near 1200, and lower `http_timeout`/`total_timeout`. Provider failover stops at the total deadline. |
| Result is just thinking / no answer | The model spent all tokens on reasoning. Set `is_reasoning_model: true` to get more tokens upfront, or increase `response_tokens` |
| Image too large error | Some APIs reject large images. VidLens auto-compresses, but very high-res images may need manual resizing |
| Direct image input crashes a text-only Codex thread | Direct image content is sent in the first model request, before an agent rule can intercept it. Send the image path/URL instead and let VidLens return text. A text-only provider adapter should reject non-text content locally before upload. |

## Slow on first run (sandbox approval)

If the first image analysis takes 1-2 minutes but subsequent runs are fast,
this is normal. The agent's sandbox needs to approve the network request
once. After approval, subsequent vidlens calls run at full speed (8-15s
typical). This only affects the first run after install.

## Getting Help

- Check [SETUP.md](SETUP.md) for first-time configuration
- Check [ADVANCED.md](ADVANCED.md) for provider failover and other features
- Open an issue: https://github.com/francis20060728-jpg/vidlens/issues
