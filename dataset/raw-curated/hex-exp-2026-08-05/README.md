# Dec Vulhub Hex Experiment Raw Curated Dataset

โฟลเดอร์นี้เก็บ raw scanner outputs ที่คัดแล้วจากรอบทดลอง target วันที่ 2026-08-05

- source raw root: `dec-vulhub-2026-08-05-fixed/raw`
- experiment date: `2026-08-05`
- curated package date: `2026-08-24`
- purpose: เพิ่ม raw evidence และ scan provenance ให้ experimental targets ที่มีอยู่แล้วใน normalized core 43 targets ของ Dec

## Target set

targets ชุดนี้รวมอยู่ใน normalized Dec core 43 targets แล้ว จึงไม่ได้เพิ่มจำนวน normalized target แต่เพิ่มหลักฐานดิบสำหรับ feature engineering, scanner coverage analysis และ validation review

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

## สิ่งที่รวมไว้

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

รวมทั้งหมด 264 files

## สิ่งที่ไม่รวม

- `*.stderr`, `*.exit`, `*.log`, `*.yaml` ที่เป็น command metadata
- runtime/dependency/cache เช่น `.zaphome`, `chromedriver`, `*.jar`, `__pycache__`, `*.pyc`
- AutoRecon outputs เพราะต้องทำ path-normalized curation แยก
- OpenVAS เพราะไม่พบ report จริงใน target directories ชุดนี้

## วิธีใช้

ใช้ package นี้สำหรับ scanner coverage features, raw evidence review, manual PoC corroboration และ target-level feature extraction

อย่าใช้ target name หรือ CVE string ตรง ๆ เป็น ML input feature เว้นแต่งานนั้นเป็น retrieval/traceability demo เพราะ field เหล่านี้เป็น label/provenance และอาจทำให้ label leakage
