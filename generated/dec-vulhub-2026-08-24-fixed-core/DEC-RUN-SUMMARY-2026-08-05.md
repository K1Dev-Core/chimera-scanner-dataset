# DEC RUN SUMMARY — dec-vulhub-2026-08-05

- **Project**: Chimera Scanner Dataset / Dec branch
- **Scope**: Vulhub local lab (127.0.0.1 only). No public targets scanned.
- **Reused old data**: YES. 10 targets from 2026-08-04 reused (raw + normalized), 12 new targets run fresh.
- **Total targets**: 22 (10 old reuse + 12 new)
- **New CVEs added**: CVE-2018-7600, CVE-2018-7602, CVE-2020-14882, CVE-2017-10271,
  CVE-2018-1000861, CVE-2015-8562, CVE-2018-12613, CVE-2019-0193, CVE-2019-17558,
  CVE-2016-4437, thinkphp 5-rce (unknown), flask-ssti (unknown)
- **Dataset path**: `/home/kali/dataset/dec-vulhub-2026-08-05/`

## Tool results (recorded statuses, per spec)

| Tool | success | no_finding | failed | timeout | skipped | target_down |
|------|--------:|-----------:|-------:|--------:|--------:|------------:|
| nmap | 22 | 0 | 0 | 0 | 0 | 0 |
| naabu | 22 | 0 | 0 | 0 | 0 | 0 |
| httpx-toolkit | 22 | 0 | 0 | 0 | 0 | 0 |
| nuclei | 13 | 0 | 0 | 9 | 0 | 0 |
| nikto | 19 | 0 | 0 | 3 | 0 | 0 |
| wapiti | 20 | 0 | 0 | 2 | 0 | 0 |
| zaproxy | 22 | 0 | 0 | 0 | 0 | 0 |
| metasploit | 11 | 0 | 1 | 0 | 4 | 0 |
| sqlmap | 3 | 1 | 0 | 0 | 10 | 0 |
| manual_poc | 11 | 0 | 1 | 0 | 0 | 0 |

## Exploit validation (RCE confirmed in lab)

- drupal_7602 (Drupal 7.57, CVE-2018-7602): RCE via cancel-form destination poisoning — `touch /tmp/d7pwned_7602.txt` executed in container
- drupal_7600 (Drupal 8.5.0, CVE-2018-7600): version confirmed vulnerable; register-page vector returns HTTP 500, no code execution obtained (documented honestly)
- weblogic_14882 (CVE-2020-14882): RCE via console.portal MVEL ShellSession — `/tmp/success1` created
- weblogic_10271 (CVE-2017-10271): RCE via wls-wsat XMLDecoder — `/tmp/success.txt` created
- solr_0193 (CVE-2019-0193): RCE via DataImportHandler script transformer — `/tmp/success` created
- solr_17558 (CVE-2019-17558): RCE via Velocity template params.resource.loader — `/tmp/solr17558` created
- phpmyadmin_12613 (CVE-2018-12613): LFI→RCE via session file inclusion — `phpinfo()` executed
- shiro_4437 (CVE-2016-4437): RCE via rememberMe AES default key deserialization (ysoserial CommonsBeanutils1) — `/tmp/shiro_pwned` created
- joomla_8562 (CVE-2015-8562): RCE via HTTP header object injection — `phpinfo()` executed
- thinkphp_5rce: RCE via `\think\app/invokefunction` — `/tmp/thinkphp_x` created
- flask_ssti: SSTI confirmed (`{{7*7}}` → `49`); sqlmap: no injectable parameter
- jenkins_1000861 (CVE-2018-1000861): unauthenticated script-console RCE confirmed earlier (`/tmp/success` + MSF check)

## Records produced

- targets: 22
- observations: 1776
- findings: 1211
- validations: 41 (23 success)
- tool_runs: 195
- candidate rows (features): 198
- labels: 198 (positive_family_match = 16, unknown = 182 — see README weak-label note)

## Quality gate

```text
valid = true
jsonl_invalid_lines = 0
duplicate_record_ids = 0
missing_label_refs = 0
label_leakage_fields = 0
unredacted_sensitive_values = 0
public_ips = 0
targets = 22 (>= 20)
target_candidate_rows = 198 (>= 160)
```

## Raw file naming

All raw scan files renamed to `tool-name(cve)-date` pattern
(e.g. `nmap(CVE-2018-7600)-2026-08-05.txt`), old reused targets use
`2026-08-04`, new targets use `2026-08-05`. `cve=unknown` targets use
`(cve-unknown)` in filenames. Provenance paths in `records/tool_runs.jsonl`
and `normalized/**` updated to match.

## Known limitations

- nuclei ran 10,621+ templates at ~7 rps; timed out on 9 targets (incl. drupal 7600/7602, weblogic x2, batch3) and succeeded on 13 (old reuse 10 + drupal x2 after targeted rerun + solr_0193 + flask partial). Timeouts recorded per spec.
- nikto timed out on 3 targets (joomla partial text output kept and normalized).
- wapiti timed out on 2 targets (phpmyadmin: no output; joomla: partial JSON kept).
- drupal_7600 RCE not achieved via register vector (HTTP 500); MSF AutoCheck could
  not fingerprint Drupal 8.5.0; target recorded as vulnerable-by-version.
- sqlmap skip records present for targets without parameterized URLs.
- No public IPs scanned; no fabricated data. All statuses recorded as-is.
- Git handoff: not performed in this session (no commit pushed).

## Schema Fix Applied on 2026-08-25

- Corrected `records/findings.jsonl` so `record_type` is `finding`.
- Normalized finding `scan_status` from `finding` to `success`.
- Removed duplicated finding rows from `records/observations.jsonl`.
- Added `record_type=tool_run` to `records/tool_runs.jsonl`.
- Rebuilt `records/all-records.jsonl` from unique targets + observations + findings + validations + tool_runs.
- Latest unique record counts: targets=43, observations=704, findings=2046, validations=92, tool_runs=381, all_records=3266.
- This package is core-artifact only; raw scan files remain in the local shared folder.
