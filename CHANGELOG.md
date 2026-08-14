# Changelog

All notable changes to this project are documented here.
Versions follow [semantic versioning](https://semver.org).

## [Unreleased]

## [2.0.0] - 2026-08-14

### Changed
- **MCP-first architecture**: MCP server is now the recommended way to use VidLens. CLI/skill is the fallback for agents without MCP support.
- **Native vision check**: if the model already supports vision, VidLens is NOT used. Only text-only models trigger it.
- **SKILL.md reduced to 542 bytes** (69% reduction). Layer 1 = frontmatter, Layer 2 = 3-line body, Layer 3 = docs/ on demand.
- README split from one 23KB file into 1KB index + 9 per-language files.
- requirements.txt: mcp pinned to >=1.0,<2.0 (2.0 broke decorator API).
- AGENTS rule rewritten: MCP preferred > CLI fallback > native vision check.
- Do not install both MCP and skill. Use MCP if available, skill only as fallback.

### Added
- Multi-language docs: en, zhcn, zhtw, ja, ko, fr, es, de, pt
- docs/SETUP.md, docs/ADVANCED.md, docs/TROUBLESHOOTING.md

### Fixed
- bridge.py now supports reasoning models (mimo-v2.5, o1, etc.)
- Result printed to stdout before file write (no crash on permission error)
- Prevents agents from reading output file twice

## [1.5.1] - 2026-08-14
### Fixed
- Result printed to stdout, eliminates GBK encoding problem

## [1.5.0] - 2026-08-14
### Changed
- Progressive disclosure architecture: SKILL.md body reduced 40%
- Moved detailed content into docs/ layer 3 reference files

## [1.4.0] - 2026-08-14
### Added
- URL support, comprehensive trigger scenarios, multi-agent auto-detection

## [1.3.0] - 2026-08-14
### Added
- Reasoning model support, 9-language README

## [1.2.0] - 2026-08-14
### Added
- Initial release

[Unreleased]: https://github.com/francis20060728-jpg/vidlens/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v2.0.0
[1.5.1]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.5.1
[1.5.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.5.0
[1.4.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.4.0
[1.3.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.3.0
[1.2.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.2.0
