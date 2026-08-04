# Chimera Multi-Vulnerability Web Dataset (2026-08-05)

Dataset pack for **Exploit-DL: automatic exploit ranking with Deep Learning**.

This pack focuses on one-target-many-vulnerabilities labs, so the model can learn ranking behavior such as "which exploit family should be tried first".

## Labs

- OWASP Juice Shop (`owasp-juice-shop`)
- OWASP WebGoat (`owasp-webgoat`)
- Damn Vulnerable Web Application (`dvwa`)
- bWAPP (`bwapp`)
- OWASP Mutillidae / NOWASP (`mutillidae-nowasp`)

## Main files

- `records/exploit-dl-target-features.jsonl`: one feature row per target app
- `records/exploit-rank-candidates.jsonl`: candidate exploit family ranking rows
- `records/all-records.jsonl`: all normalized records
- `datasets/tools-name-date/<tool>-2026-08-05/<lab-id>/raw`: raw scanner outputs
- `datasets/tools-name-date/<tool>-2026-08-05/<lab-id>/normalized`: parsed scanner outputs

## Label warning

Rank rows are scanner-assisted candidate rankings, not confirmed exploit-success labels. For final supervised training, add an exploit validation stage inside local labs and populate `exploit_success_observed`.
