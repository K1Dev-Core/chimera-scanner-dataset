# Dec Vulhub Hex Experiment Raw Curated Dataset

Curated raw scanner outputs from the 2026-08-05 experimental target run.

- Source raw root: `dec-vulhub-2026-08-05-fixed/raw`
- Experiment date: `2026-08-05`
- Curated package date: `2026-08-24`
- Purpose: add raw evidence and scan provenance for the experimental targets already represented in the Dec 43-target normalized core.

## Target Set

These targets are already included in the 43-target normalized Dec core, so this package does not increase the normalized target count. It adds supporting raw evidence for feature engineering, scanner coverage analysis, and validation review.

| target_id | expected vulnerability |
| --- | --- |
| `drupal_7600` | CVE-2018-7600 |
| `drupal_7602` | CVE-2018-7602 |
| `weblogic_14882` | CVE-2020-14882 |
| `weblogic_10271` | CVE-2017-10271 |
| `jenkins_1000861` | CVE-2018-1000861 |
| `joomla_8562` | CVE-2015-8562 |
| `phpmyadmin_12613` | CVE-2018-12613 |
| `solr_0193` | CVE-2019-0193 |
| `solr_17558` | CVE-2019-17558 |
| `thinkphp_5rce` | unknown/non-CVE lab |
| `flask_ssti` | unknown/non-CVE lab |
| `shiro_4437` | CVE-2016-4437 |

## Included

| Tool | Files | Formats |
| --- | ---: | --- |
| httpx-toolkit | 24 | `.jsonl`, `.stdout` |
| manual_poc | 12 | `.txt`, `.out` |
| metasploit | 34 | `.stdout`, `.rc` |
| naabu | 24 | `.jsonl`, `.stdout` |
| nikto | 24 | `.txt`, `.stdout` |
| nmap | 36 | `.txt`, `.xml`, `.stdout` |
| nuclei | 54 | `.jsonl`, `.stdout` |
| sqlmap | 9 | `.txt`, `.stdout` |
| wapiti | 23 | `.json`, `.stdout` |
| zaproxy | 24 | `.json`, `.stdout` |

Total: 264 files.

## Excluded

- `*.stderr`, `*.exit`, `*.log`, and `*.yaml` command metadata.
- Runtime/dependency/cache artifacts such as `.zaphome`, `chromedriver`, `*.jar`, `__pycache__`, and `*.pyc`.
- AutoRecon outputs from this package, because AutoRecon needs a separate path-normalized curation pass.
- OpenVAS for this package because no real OpenVAS reports were present for these target directories.

## How To Use

Use this package for scanner coverage features, raw evidence review, manual PoC corroboration, and target-level feature extraction.

Avoid using target names or exact CVE strings as ML input features unless the task is explicitly a retrieval or traceability demo. Those fields are labels/provenance and can leak the answer into training.
