# Chimera Active Scanner Suite Dataset (2026-08-05)

ชุดนี้เป็น active scan dataset ที่รันกับ local Docker labs ที่เราควบคุมเอง

## Tools

- nmap
- httpx
- nuclei
- nikto
- wapiti
- zap

## Targets

- Acme Support Portal — `http://127.0.0.1:27000/`
- Nova DevOps Console — `http://127.0.0.1:27100/`

## Output สำคัญ

- `datasets/tools-name-date/<tool>-2026-08-05/<lab>/raw/` — output ดิบจาก tool
- `datasets/tools-name-date/<tool>-2026-08-05/<lab>/normalized/` — JSONL ที่ normalize แล้ว
- `records/all-records.jsonl` — รวม normalized records ทั้งหมด
- `derived/active_scan_summary.csv` — สรุปจำนวน finding ต่อ tool/target
- `derived/active_target_features.csv` — feature table สำหรับต่อเข้า Exploit-DL
- `manifests/index.json` — manifest ของ dataset

## Summary

- Tool-target runs: 12
- Normalized records: 52
- Scanner findings: 46

หมายเหตุ: Nuclei ในรอบนี้ใช้ template scope เบาและอาจไม่มี match ซึ่งยังเป็นข้อมูลเชิงลบที่ใช้เป็น feature ได้
