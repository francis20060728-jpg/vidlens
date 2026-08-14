# Testing and Boundaries

## Automated suite

```bash
python -m unittest discover -s tests -v
python -m compileall -q scripts vidlens tests
```

The suite covers:

- Capability policy: multimodal uses native vision; text-only/unknown uses VidLens
- Prompt combination and structured `VERDICT/EVIDENCE/BLOCKERS/NEXT FIX` output
- Separate response budgets for verification and general description
- Large-image downscaling and oversized-image enforcement
- Provider failover, per-request timeout, and total deadline
- Environment overrides and outbound request shape
- Recursive media discovery, dependency-directory pruning, and image-first sorting
- CLI positional parsing and URL download content/size handling
- OpenCV contact-sheet fallback when ffmpeg is absent

## Manual matrix

| Boundary | Expected result |
|----------|-----------------|
| Exact image path | Call `look` directly; do not call `list_media` first |
| Vague media name | Call `find_and_look` in one request |
| Explicit multimodal model | Use native vision; do not call VidLens |
| Text-only or unknown model | Send path/URL through VidLens; main agent receives text only |
| Rejected native image input | Do not retry native input; use VidLens |
| Direct image pixels into text-only Codex endpoint | Request reaches provider before an agent rule can run; use path/URL instead |
| Frontend/UI output | Capture to a local file and use `verify_page` once with intended behavior |
| Generated visual output | Use `verify_output` once; fix blockers and recheck once |
| Web page URL | Capture a screenshot first unless the user explicitly asks for a direct download |
| Video without ffmpeg | OpenCV samples frames into a labeled contact sheet |

## Safety rule

Never place an image into a Codex conversation merely to test a text-only
provider. Keep test media in a project-local temporary directory and pass its
path to VidLens. The external vision model returns text, keeping image bytes out
of the main conversation.
