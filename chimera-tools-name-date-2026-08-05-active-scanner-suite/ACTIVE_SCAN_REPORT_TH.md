# Active Scanner Suite Report — 2026-08-05

รอบนี้รัน scanner suite จริงกับ local Docker labs ที่เราควบคุมเอง 2 ตัว:

| lab_id | target | product |
|---|---|---|
| `acme-support` | `http://127.0.0.1:27000/` | Acme Support Portal |
| `nova-devops` | `http://127.0.0.1:27100/` | Nova DevOps Console |

## Tools ที่รัน

```text
nmap
httpx
nuclei
nikto
wapiti
zap
```

## ผลรวม

| Metric | Value |
|---|---:|
| Targets | 2 |
| Tools | 6 |
| Tool-target runs | 12 |
| Normalized records | 52 |
| Scanner findings | 46 |

## Summary ต่อ tool

| Target | nmap | httpx | nuclei | nikto | wapiti | zap |
|---|---:|---:|---:|---:|---:|---:|
| acme-support | service fingerprint | web fingerprint | 0 match | 7 findings | 4 findings | 12 alerts |
| nova-devops | service fingerprint | web fingerprint | 0 match | 7 findings | 4 findings | 12 alerts |

## Feature ที่ได้จาก active scan

ตัวอย่าง feature ที่ได้จากรอบนี้:

```text
service_product = Werkzeug httpd
service_version = 3.1.8
http_title = Dashboard | Acme Support Portal
http_tech = Flask:3.1.8 | Python:3.12.13
has_nmap_evidence = 1
has_httpx_evidence = 1
has_nuclei_evidence = 0
has_nikto_evidence = 1
has_wapiti_evidence = 1
has_zap_evidence = 1
nikto_finding_count = 7
wapiti_finding_count = 4
zap_finding_count = 12
```

## ไฟล์สำคัญ

```text
derived/active_scan_summary.csv
derived/active_target_features.csv
records/all-records.jsonl
manifests/index.json
```

## หมายเหตุ

Nuclei รอบนี้ใช้ template scope แบบเบาและไม่มี match ซึ่งยังมีประโยชน์ในฐานะ negative evidence feature (`has_nuclei_evidence = 0`, `nuclei_finding_count = 0`)

