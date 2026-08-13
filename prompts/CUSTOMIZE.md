# Custom Prompts

Drop `.txt` files here to create reusable prompt templates.
Reference them by name (without `.txt`) via `--prompt-name` (CLI) or
`prompt_name` (MCP).

## Built-in Templates

| Name | Purpose |
|------|---------|
| `describe` | General description of any media |
| `verify_output` | Self-verification: agent checks its own visual output |
| `quality_check` | Technical quality assessment |
| `object_inventory` | List and locate all objects |
| `compare_frames` | Sequential frame comparison for videos |

## Creating Project-Specific Prompts

Add files for your workflow. Example pipeline stages:

```
prompts/
  stage1_detection.txt    "Are candidate boxes covering all objects?"
  stage2_recognition.txt  "Are CLIP labels accurate and calibrated?"
  stage3_tracking.txt     "Are track IDs stable across frames?"
```

Then call:

```bash
python -m vidlens output.mp4 --prompt-name stage3_tracking
```

Or via MCP:

```json
{"tool": "look", "arguments": {"media_path": "...", "prompt_name": "stage3_tracking"}}
```
