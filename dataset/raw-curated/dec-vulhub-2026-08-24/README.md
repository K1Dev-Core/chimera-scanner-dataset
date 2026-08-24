# Dec Vulhub Raw Curated Dataset

โฟลเดอร์นี้เก็บ raw scanner outputs ที่คัดแล้วสำหรับ Dec Vulhub dataset update

- source raw root: `dataset/raw`
- source scan date: `2026-08-04`
- curated package date: `2026-08-24`
- purpose: เก็บผล scan จริงเพื่อ review, demo, ML และ feature engineering โดยไม่เอา cache/runtime/dependency ติดมาด้วย

## สิ่งที่รวมไว้

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

รวมทั้งหมด 85 files

## สิ่งที่ไม่รวม

- `dataset/raw/autorecon/**` เพราะ path ของ AutoRecon หลายไฟล์ยาวเกินบน Windows ต้องทำ path-normalization แยก
- ZAP home/cache/runtime เช่น `.zaphome`
- runtime/dependency artifacts เช่น `chromedriver`, `*.jar`, `__pycache__`, `*.pyc`

## หมายเหตุ

โครงสร้างในนี้ยังคงแยกตาม tool และ target เพื่อ trace กลับไปยัง scanner output ได้ง่าย แต่เก็บเฉพาะ artifact ที่เป็นผล scan จริง
