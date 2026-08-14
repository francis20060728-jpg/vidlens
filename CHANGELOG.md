# Changelog

All notable changes to this project are documented here.
Versions follow [semantic versioning](https://semver.org).

## [Unreleased]

## [1.5.0] - 2026-08-14

### Changed
- **Progressive disclosure architecture**: SKILL.md body reduced 40%
  (1732 -> 1047 bytes). Only the essential run + read-result commands
  remain in the always-loaded body.
- Moved detailed content into `docs/` layer 3 reference files:
  - `docs/SETUP.md` -- first-time configuration walkthrough, API provider
    table, config reference
  - `docs/ADVANCED.md` -- provider failover, reasoning models, OCR
    fallback, video, custom prompts, agent integration, MCP server
  - `docs/TROUBLESHOOTING.md` -- problem/fix table
- SKILL.md now follows the proper two-layer skill pattern:
  Layer 1 = frontmatter description (always in context),
  Layer 2 = minimal body (loaded on trigger),
  Layer 3 = docs/ (read on demand)

## [1.4.0] - 2026-08-14

### Added
- URL support: pass `https://...` directly, auto-downloads the media file
- Comprehensive trigger scenarios in AGENTS rule (URLs, UI, charts, build verification, etc.)
- `verify_page` prompt template for checking if web pages render correctly
- Multi-agent auto-detection for `--install-agents` (Codex, Claude Code, Cursor)
- `--path` flag to install the rule into any agent's config file
- Agent-agnostic rule: unknown agents (opencode, zcode, mimocode) get printed instructions
- Auto-Use Rule section added to all 9 README languages

### Changed
- Rule wording: proactive "check first" + comprehensive trigger list (not just files)
- `--status` shows per-agent install status
- Rule paths use forward slashes for cross-platform compatibility
- README: all 9 languages now consistent (Install + Auto-Use + Usage)

## [1.3.0] - 2026-08-14

### Added
- Reasoning model support (mimo-v2.5, o1, o3, o4, deepseek-r1, qwq, thinking)
- Auto-detection of reasoning model names -- triples `max_tokens` upfront
  so the model has room to finish thinking and produce a real answer
- `is_reasoning_model` config option for manual override
- Fallback to `reasoning_content` when `content` is empty
- 9-language README (EN, ZH-CN, ZH-TW, JA, KO, FR, ES, DE, PT)
- Quick Start now starts from `git clone` (merged Install + Quick Start)
- SECURITY.md

### Changed
- SKILL.md and AGENTS rule rewritten for transparency (no hidden routing)
- Config field names: `api_url` / `api_key` / `model_name` (clearer)

### Fixed
- BOM stripping in YAML parser (`\ufeff`)
- Windows UTF-8 stdout/stderr (GBK garbled output)
- `nargs="*"` swallowing question text as media path

## [1.2.0] - 2026-08-14

### Added
- Initial release
- Multi-provider failover chain (up to 9 fallback providers)
- Local OCR fallback (Windows OCR / Tesseract)
- Zero-dependency image analysis (Python stdlib only)
- Video support via ffmpeg (system binary) with opencv contact-sheet fallback
- MCP server mode for Claude Desktop, Cursor, Cline
- Custom prompt templates (`prompts/` directory)
- `--init`, `--status`, `--install-agents`, `--remove-agents` commands
- Launcher scripts (`vidlens.cmd` / `vidlens.sh`) with Python auto-detection

[Unreleased]: https://github.com/francis20060728-jpg/vidlens/compare/v1.4.0...HEAD
[1.5.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.5.0
[1.4.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.4.0
[1.3.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.3.0
[1.2.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.2.0
