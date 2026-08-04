# Chimera Scanner Dataset - Vulhub Redo (2026-08-05)

Clean redo package for the **Exploit-DL** final project.

## Scope

- Source: local Docker labs from Vulhub
- Run ID: `202608041930-vulhub-expanded`
- Labs: 8
- Tools: naabu, nmap, httpx, nuclei, nikto
- Safety: scanner/fingerprint collection only; no exploit execution in this package

## Layout

```
datasets/
  labs/<lab-id>/lab.json
  tools-name-date/<tool-name>-2026-08-05/<lab-id>/
    raw/
    normalized/
records/
  all-records.jsonl
  exploit-dl-features.jsonl
  exploit-labels.jsonl
manifests/
  index.json
  source-run-manifest.json
  checksums.sha256
```

## Exploit-DL notes

`records/exploit-dl-features.jsonl` is the main modeling table. Each row joins scanner output with the known Vulhub CVE/product label.

Current labels are **candidate positive labels** from lab identity. They should not be treated as confirmed exploit-success labels until paired with an explicit exploit validation runner.
