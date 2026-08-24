# Hex Branch Progress Import - 2026-08-05

This note summarizes the useful work imported from `origin/Hex` into `Dec` without merging the whole branch.

## Why Not Merge `Hex` Directly

`Hex` contains useful dataset experiments, but a direct merge is risky:

- It deletes several current `Dec` generated datasets and docs.
- It contains very deep bulk dataset paths that trigger Windows `Filename too long` warnings.
- Some records are static metadata or weak labels, not active scanner evidence.
- It mixes demo labs, slide materials, fresh lab source code, and dataset records in one branch.

For `Dec`, we imported compact records, feature tables, manifests, and curated experiment raw evidence only.

## Imported From `Hex`

| Path | Purpose |
| --- | --- |
| `chimera-tools-name-date-2026-08-05-vulhub-cve-bulk/` | Bulk Vulhub metadata: 160 labs, feature seeds, weak labels, rank candidates, feature matrix. |
| `chimera-tools-name-date-2026-08-05-vulhub-expanded-metadata/` | Expanded Vulhub metadata and exploit label candidates. |
| `chimera-tools-name-date-2026-08-05-vulhub-redo/` | Active scanner redo seed: 8 labs with exploit labels/features. Records only, not raw tree. |
| `chimera-tools-name-date-2026-08-05-active-scanner-suite/` | Active scanner suite summary records and target features. |
| `chimera-tools-name-date-2026-08-05-multi-vuln-web/` | Multi-vulnerability web dataset records, feature matrix, and build script. |
| `demo-feature-label-model-2026-08-05/` | Demo feature-label model pack and small report/data tables. |
| `dataset/raw-curated/hex-exp-2026-08-05/` | Curated raw scanner/manual PoC outputs for the 12 experimental targets from the 2026-08-05 run. |

## Hex Progress Snapshot

- `Hex` branch head: `a471f55 Add bulk Vulhub CVE dataset and active scanner suite`
- Bulk Vulhub CVE dataset: 160 labs, 640 training/ranking rows, 117 feature columns, 1120 total records.
- Vulhub redo active scan seed: 8 labs using `naabu`, `nmap`, `httpx`, `nuclei`, and `nikto`.
- Multi-vulnerability web dataset: records and feature matrix for exploit ranking experiments.
- Demo feature-label model pack: small explainable demo tables and reports.
- Fresh lab ideas present on `Hex` but not imported here: Acme support portal, Nova DevOps console, Grafana CVE-2024-9264, TeamCity CVE-2024-27198.

## How To Use This In `Dec`

Use the imported `Hex` materials as reference and feature seed data:

- Good for target discovery, feature vocabulary, weak labels, scanner coverage analysis, and demo ranking examples.
- Good for selecting next Kali scan targets from the 160-lab bulk metadata.
- Good for explaining why scanner-only labels are weak until exploit validation is recorded.

Do not treat these imports as final ground truth:

- `label-candidates` and `exploit-labels` are weak labels from lab identity.
- `feature-seeds` are useful model inputs but may leak labels if target names, CVE strings, or lab names are used directly.
- Imported records should be normalized into the current Dec schema before training alongside `generated/dec-vulhub-2026-08-24-fixed-core`.

## Next Integration Step

Use `chimera-tools-name-date-2026-08-05-vulhub-cve-bulk/records/lab-index.jsonl` to pick the next 10-20 targets for Kali active scans, then write new scanner outputs into a fresh `raw-curated` package and normalized Dec records.
