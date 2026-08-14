# Changelog

All notable changes to this project are documented here.
Versions follow [semantic versioning](https://semver.org).

## [2.1.0] - 2026-08-14

### Added
- Capability-first vision policy: explicitly multimodal models use native vision; text-only and unknown-capability providers use VidLens and receive text only
- Bounded latency architecture with image downscaling, per-provider timeouts, a total failover deadline, and a smaller PASS/FAIL response budget
- Concise `verify_page` and `verify_output` templates that combine review method with caller intent
- MCP runtime now shares URL handling, media preparation, provider failover, OCR fallback, and timeout behavior with the CLI
- Automated boundary tests for media discovery, CLI parsing, URL limits, environment overrides, outbound request shape, timeout bounds, text-safe rules, and video fallback

### Changed
- Reasoning model list no longer hardcoded (was mimo-v2.5, o1, o3, etc. -- now says "auto-detects thinking models")
- MCP now reuses the canonical CLI runtime for URL handling, image preparation, provider failover, OCR fallback, and timeouts
- Verification prompts now return a concise VERDICT/EVIDENCE/BLOCKERS/NEXT FIX and combine templates with caller intent
- Large images are downscale-re-encoded before upload; provider failover is bounded by `total_timeout`
- Structured verification prompts use a smaller token budget than general descriptions
- Tool descriptions and the AGENTS rule prevent generic image-view tools from inserting image content into text-only model conversations
- Documented that direct image input reaches a text-only provider before agent rules can run; use a path/URL so VidLens returns text

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

[2.1.0]: https://github.com/francis20060728-jpg/vidlens/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v2.0.0
[1.5.1]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.5.1
[1.5.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.5.0
[1.4.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.4.0
[1.3.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.3.0
[1.2.0]: https://github.com/francis20060728-jpg/vidlens/releases/tag/v1.2.0
