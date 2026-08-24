# Dec Vulhub Raw Curated Dataset

Curated raw scanner outputs for the Dec Vulhub dataset update.

- Source raw root: `dataset/raw`
- Source scan date: `2026-08-04`
- Curated package date: `2026-08-24`
- Purpose: keep real scanner outputs for dataset review, demo, ML, and feature engineering without runtime caches or tool dependencies.

## Included

| Tool | Files | Formats |
| --- | ---: | --- |
| httpx-toolkit | 10 | `.jsonl` |
| metasploit | 4 | `.txt` |
| naabu | 10 | `.jsonl` |
| nikto | 10 | `.txt` |
| nmap | 20 | `.txt`, `.xml` |
| nuclei | 10 | `.jsonl` |
| sqlmap | 1 | `.txt` |
| wapiti | 10 | `.json` |
| zaproxy | 10 | `.txt` |

Total: 85 files.

## Excluded

- `dataset/raw/autorecon/**` for this first curated raw pass because several AutoRecon report paths are too long on Windows and need a separate path-normalization pass.
- ZAP home/cache/runtime folders such as `.zaphome`.
- Runtime/dependency artifacts such as `chromedriver`, `*.jar`, `__pycache__`, and `*.pyc`.

## Notes

This folder intentionally preserves the per-tool and per-target structure from `dataset/raw` for traceability while keeping only scan-result artifacts.
