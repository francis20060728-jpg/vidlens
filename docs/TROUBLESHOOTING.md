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
| Very slow / appears stuck | Model may be a reasoning model (thinking before answering). VidLens auto-triples max_tokens. Or set `is_reasoning_model: true`. |
| Result is just thinking / no answer | The model spent all tokens on reasoning. Set `is_reasoning_model: true` to get more tokens upfront, or increase `response_tokens` |
| Image too large error | Some APIs reject large images. VidLens auto-compresses, but very high-res images may need manual resizing |

## Getting Help

- Check [SETUP.md](SETUP.md) for first-time configuration
- Check [ADVANCED.md](ADVANCED.md) for provider failover and other features
- Open an issue: https://github.com/francis20060728-jpg/vidlens/issues
