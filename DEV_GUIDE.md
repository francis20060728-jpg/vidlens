# VidLens Developer Guide

> Complete handoff document for developers and AI models picking up this project.
> Covers: history, architecture, file map, known issues, environment, roadmap.

---

## 1. Project Summary

**VidLens** is an open-source vision bridge for text-only AI agents. It routes
images and videos through an external vision model API and returns plain text,
so agents without native image support can inspect, verify, and respond to
visual content.

- **GitHub**: https://github.com/francis20060728-jpg/vidlens
- **License**: MIT
- **Author email**: francis20060728@gmail.com
- **Current version**: v2.0.0

Core philosophy: **zero pip dependencies for images**. Only Python 3 stdlib.
Videos use ffmpeg (system binary); opencv is an optional fallback.

---

## 2. Repository Locations

| Location | Purpose |
|----------|---------|
| `F:\vscode\开源\vidlens\` | **Primary dev location** (after migration) |
| `C:\Users\franc\.codex\skills\vidlens\` | Installed Codex skill (live copy) |
| `F:\vscode\想法\零样本目标识别\vidlens\` | Private project-optimized variant (NOT open source) |

The private variant has project-specific optimizations and is separate.

---

## 3. Environment

| Item | Value |
|------|-------|
| Python | `F:\miniconda\sad\python.exe` (3.13) |
| Git | `D:\tool\Git\cmd\git.exe` |
| Shell | PowerShell (no `&&`, use `;`) |
| mcp SDK | 1.29.0 (pinned >=1.0,<2.0; 2.0 broke decorator API) |
| OS | Windows 11, Chinese locale (GBK console) |

### Critical encoding note

PowerShell uses GBK codepage. Chinese paths display as mojibake. Always:
- Set `$env:PYTHONIOENCODING="utf-8"` before running Python that prints Unicode
- Use Python argv for file operations (never inline Chinese paths in PowerShell)
- Read files with `pathlib.Path.read_text(encoding="utf-8")`

### Network

Network access requires `require_escalated` in the sandbox.

---

## 4. Version History

### v1.2.0 - Initial Release
- Single-file `scripts/vidlens.py` CLI (43KB monolith)
- Basic image analysis via vision API
- `--status`, `--init` commands, BOM stripping in YAML parser

### v1.3.0 - Reasoning Model Support
- Detects `reasoning_content` in API response
- Auto retry with 3x max_tokens for reasoning models
- 9-language README

### v1.4.0 - URL Support + Triggers
- URL support for images/videos
- Comprehensive trigger scenarios in AGENTS rule
- Multi-agent `--install-agents` with proactive rule

### v1.5.0 - Progressive Disclosure
- SKILL.md slimmed from 7.6KB to 1.7KB
- 3-layer: frontmatter -> SKILL.md body -> docs/

### v1.5.1 - stdout Fix
- Result printed to stdout BEFORE file write
- Eliminates GBK encoding problem and multi-minute delays

### v2.0.0 - MCP-First Architecture (current)
- MCP server (`vidlens/server.py`) with 3 tools: `look`, `list_media`, `find_and_look`
- CLI/skill is fallback for agents without MCP
- Native vision check: skip VidLens if model already sees images
- SKILL.md reduced to 542 bytes
- Multi-agent install (Codex, Claude Code, Cursor, any agent)
- Provider failover (up to 9), local OCR fallback
- Reasoning model auto-detection (no hardcoded list)
- One-Click Deploy + MCP Tools table + Contact in all 9 languages

---

## 5. Architecture

### Three-Layer Progressive Disclosure

Minimizes token cost for AI agents:

```
Layer 1 (always in context): Skill list entry
    name + 1-line description only (~100 bytes)

Layer 2 (read on trigger): SKILL.md
    3-line body (~542 bytes total)

Layer 3 (read on demand): docs/ files
    SETUP.md, ADVANCED.md, TROUBLESHOOTING.md
```

### MCP-First Priority Chain

```
1. NATIVE VISION  -> skip VidLens if model can see images
2. MCP TOOL       -> call look/list_media/find_and_look directly (fastest)
3. CLI FALLBACK   -> python scripts/vidlens.py <path> --task "question"
```

### Data Flow

```
Image/Video file
    |
    v
[media.py] load_media() / raw bytes read
    |
    v
[bridge.py] Bridge.ask() -- base64 -> HTTP POST to vision API
    |        (with provider failover chain)
    v
Vision API response (plain text) -> returned to agent
```

---

## 6. File-by-File Map

### Root Files

| File | Size | Purpose |
|------|------|---------|
| `README.md` | 5.3KB | English landing page (full content) + language switcher |
| `en.md` | 61B | Redirect to README.md |
| `zhcn.md` | 5.0KB | Simplified Chinese full docs |
| `zhtw.md` | 4.5KB | Traditional Chinese full docs |
| `ja.md` | 5.1KB | Japanese full docs |
| `ko.md` | 4.5KB | Korean full docs |
| `fr.md` | 4.4KB | French full docs |
| `es.md` | 4.4KB | Spanish full docs |
| `de.md` | 4.3KB | German full docs |
| `pt.md` | 4.4KB | Portuguese full docs |
| `SKILL.md` | 542B | Layer 2: minimal skill description |
| `CHANGELOG.md` | 2.6KB | Version history |
| `SECURITY.md` | 1.2KB | API key handling, env vars, reporting |
| `LICENSE` | 1.1KB | MIT license |
| `requirements.txt` | 505B | mcp>=1.0,<2.0 + optional opencv/numpy |
| `config.example.yaml` | 1.9KB | Template config (copy to config.yaml) |
| `.gitignore` | 139B | Ignores config.yaml, __pycache__ |
| `vidlens.cmd` | 1.2KB | Windows launcher: auto-finds Python |
| `vidlens.sh` | 726B | Unix launcher: auto-finds Python |

### `vidlens/` Package

| File | Size | Purpose |
|------|------|---------|
| `__init__.py` | 440B | Version + public API exports |
| `__main__.py` | 106B | `python -m vidlens` entry point |
| `bridge.py` | 6.9KB | Vision API client. Base64 encode -> HTTP POST. Provider failover. Config loading with env var overrides. |
| `media.py` | 5.8KB | Media loading: detect_kind, find_media_files, load_image, grab_frames, stitch_sheet. Uses cv2/numpy (lazy import). |
| `server.py` | 11.7KB | MCP server with 3 tools: look, list_media, find_and_look |
| `cli.py` | 638B | Thin CLI wrapper -> delegates to scripts/vidlens.py |

### `scripts/` Directory

| File | Size | Purpose |
|------|------|---------|
| `vidlens.py` | 43KB | The monolith CLI. Arg parsing, config (stdlib YAML), URL download, image/video analysis, provider failover, local OCR fallback, agent rule install/remove, output generation. |
| `check_config.py` | 303B | Wrapper -> vidlens.py --status |
| `look.py` | 312B | Wrapper -> vidlens.py (backward compat) |
| `local_ocr.py` | 3.9KB | Local OCR fallback: Windows OCR + Tesseract. Pure stdlib. |

### `docs/` (Layer 3)

| File | Purpose |
|------|---------|
| `SETUP.md` | Step-by-step installation guide |
| `ADVANCED.md` | Provider failover, reasoning models, custom prompts, video config |
| `TROUBLESHOOTING.md` | Common problems and fixes |

### `prompts/` Directory

| File | Purpose |
|------|---------|
| `describe.txt` | Default: describe what you observe |
| `object_inventory.txt` | Count and list all objects |
| `quality_check.txt` | Quality assessment checklist |
| `compare_frames.txt` | Compare frames in a video contact sheet |
| `verify_output.txt` | Verify generated visual output |
| `verify_page.txt` | Verify a rendered web page |
| `CUSTOMIZE.md` | How to create custom prompt templates |

### `examples/` Directory

| File | Purpose |
|------|---------|
| `README.md` | Example usage guide |
| `*.txt` | Example prompts (mirror of prompts/) |

### `agents/` Directory

| File | Purpose |
|------|---------|
| `openai.yaml` | OpenAI agent marketplace metadata |

---

## 7. Configuration System

### config.yaml (gitignored)

```yaml
api_url: "https://api.openai.com/v1"    # Required
api_key: "sk-xxxx..."                   # Required
model_name: "gpt-4o"                    # Required
response_tokens: 4000
sampling_temp: 0.1
http_timeout: 120
is_reasoning_model: false
fallback_1_url: "..."                   # Optional, up to 9
```

### Environment Variable Overrides

| Variable | Overrides |
|----------|-----------|
| `VIDLENS_API_URL` / `VIDLENS_ENDPOINT` | `api_url` |
| `VIDLENS_API_KEY` / `VIDLENS_SECRET` | `api_key` |
| `VIDLENS_MODEL` / `VIDLENS_VISION_MODEL` | `model_name` |

Env vars checked BEFORE config.yaml. This is how MCP server registration works.

### Config Loading Chain

1. Try pyyaml -> yaml.safe_load()
2. Fallback to _parse_flat_yaml() (stdlib-only flat YAML reader)
3. Apply VIDLENS_* env var overrides

---

## 8. Known Problems and Solutions

### 5-minute delay on first analysis
- **Cause**: Agent had to read output file separately; PowerShell GBK caused retries
- **Solution (v1.5.1)**: Print result to stdout FIRST, file write is best-effort

### Chinese path corruption in PowerShell
- **Cause**: GBK console mangles Chinese characters in shell args
- **Solution**: Use Python argv for file ops; set PYTHONIOENCODING=utf-8

### Reasoning models consume all tokens
- **Cause**: reasoning_content uses up max_tokens, content is empty
- **Solution (v2.0.0)**: Auto-detect reasoning models, use larger max_tokens

### Output file permission error
- **Cause**: Default output dir not writable in sandbox
- **Solution**: stdout-first design; use --output for writable path

### mcp 2.0 breaks decorator API
- **Solution**: Pin mcp>=1.0,<2.0 in requirements.txt

---

## 9. Design Decisions

- **Zero pip for images**: Works in sandboxed environments without pip install
- **MCP-first**: 10-50x faster than CLI (no process startup, no sandbox)
- **No auto-download URLs**: Security -- screenshot first so user sees what is analyzed
- **stdout not file**: Eliminates encoding issues, faster, works without write perms
- **Agent-agnostic install**: Auto-detects config files, not hardcoded agent names
- **Native vision check first**: Skip VidLens if model already sees images

---

## 10. Future Roadmap

### High Priority
1. PyPI package: `pip install vidlens`
2. Async MCP server for better concurrency
3. Batch analysis: `look_multiple()` for several images
4. Streaming responses for faster first-token

### Medium Priority
5. More local OCR backends (macOS Vision, EasyOCR, PaddleOCR)
6. Interactive `--setup` config wizard
7. Health check MCP tool to verify all providers
8. Token usage reporting

### Low Priority
9. Web UI dashboard for testing
10. Official Codex/Claude Code plugin marketplace submission
11. Video timeline navigation (request specific timestamps)

### Known Technical Debt
- `scripts/vidlens.py` (43KB) is a monolith -- consider splitting
- `examples/` and `prompts/` overlap -- consolidate
- No automated tests -- need unit tests for bridge.py, media.py
- `_parse_flat_yaml` does not support nested YAML

---

## Appendix: Quick Reference

```bash
# Status check
python scripts/vidlens.py --status

# Initialize config
python scripts/vidlens.py --init

# Analyze an image
python scripts/vidlens.py image.png "What is in this image?"

# Install agent rule
python scripts/vidlens.py --install-agents

# Start MCP server
python vidlens/server.py

# Run from package
python -m vidlens image.png "question"
```

### Git workflow

```bash
cd F:\vscode\开源\vidlens
& 'D:\tool\Git\cmd\git.exe' add -A
& 'D:\tool\Git\cmd\git.exe' commit -m "description"
& 'D:\tool\Git\cmd\git.exe' push origin main
```

### Sync to installed Codex skill

Use Python (never inline Chinese paths in PowerShell):

```python
import os, shutil, pathlib
src = pathlib.Path(r"F:\vscode\开源\vidlens")
dst = pathlib.Path(r"C:\Users\franc\.codex\skills\vidlens")
skip = {"config.yaml", ".git", "__pycache__"}
for root, dirs, files in os.walk(src):
    dirs[:] = [d for d in dirs if d not in {".git", "__pycache__"}]
    for f in files:
        if f in skip: continue
        sfp = pathlib.Path(root) / f
        rel = sfp.relative_to(src)
        dfp = dst / rel
        dfp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sfp, dfp)
```
