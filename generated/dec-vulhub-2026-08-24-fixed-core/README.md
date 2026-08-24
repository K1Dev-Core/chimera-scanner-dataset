# DEC Dataset — dec-vulhub-2026-08-05

Chimera Scanner Dataset (Dec branch). 22 targets from Vulhub local lab.

## Label semantics (IMPORTANT)

The label `positive_family_match` in `labels/target-candidate-labels.jsonl` is a
**weak label** derived from Vulhub ground truth:
- It means the candidate family equals the application's known family
  (e.g. a Drupal lab is `cms`).
- It is **NOT** an "exploit succeeded" label.
- A separate signal, `candidate_validation_available`, marks rows where a manual
  PoC / MSF / sqlmap validation completed successfully for that target.
- All other rows are labeled `unknown`.

Do not treat this dataset as ground-truth exploit success for every
`positive_family_match` row.

## Contents

- `records/` — targets, observations, findings, validations, tool_runs, all-records (JSONL)
- `derived/` — target-features.json, target-candidate-features.json
- `labels/` — target-candidate-labels.jsonl
- `normalized/` — per-tool normalized records (`dec.dataset.v2`)
- `raw/` — per-target scanner outputs renamed to `tool-name(cve)-date`
- `metadata/` — target selection + old-target reuse
- `logs/` — pipeline scripts and run logs
- `manifest.json`, `quality-report.json`, `checksums.sha256`, `DEC-RUN-SUMMARY-2026-08-05.md`

## Security

- Lab-only: all hosts are 127.0.0.x loopbacks; no public IPs.
- Normalized output: sensitive values (sessions, cookies, tokens, passwords)
  redacted as `[REDACTED]`.
- No fabricated records; all tool statuses (success/no_finding/failed/timeout/skipped)
  are recorded as observed.