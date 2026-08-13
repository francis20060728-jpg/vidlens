# Security

## API Keys

VidLens stores API keys in `config.yaml` next to the skill directory. This file
is listed in `.gitignore` and should never be committed.

- Do not paste API keys into chat conversations.
- Edit `config.yaml` directly in your file manager or editor.
- If you accidentally commit a key, rotate it immediately at your provider's dashboard.

## Environment Variable Overrides

VidLens also reads credentials from environment variables (checked before
`config.yaml`):

| Variable | Purpose |
|----------|---------|
| `VIDLENS_API_URL` | Override `api_url` |
| `VIDLENS_API_KEY` | Override `api_key` |
| `VIDLENS_MODEL` | Override `model_name` |
| `VIDLENS_FALLBACK1_URL` | Override `fallback_1_url` |
| `VIDLENS_FALLBACK1_KEY` | Override `fallback_1_key` |
| `VIDLENS_FALLBACK1_MODEL` | Override `fallback_1_model` |

## Local OCR

When all cloud providers fail (or no API key is configured), VidLens falls back
to local OCR for images. This uses system-built-in tools (Windows.Media.Ocr or
Tesseract) and sends no data over the network.

## Reporting

Found a security issue? Please open a private issue or contact the maintainers
directly. Do not post security vulnerabilities in public issues.