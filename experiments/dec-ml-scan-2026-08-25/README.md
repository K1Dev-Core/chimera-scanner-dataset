# Dec ML Scan 2026-08-25

ชุดนี้เป็นผลสแกนจาก Kali/Vulhub ที่เก็บเพิ่มเพื่อทดลอง ML ranking ของโปรเจกต์ Dec

เป้าหมายคือเพิ่มข้อมูล scanner-derived feature ให้โมเดลเห็น service/family ที่หลากหลายขึ้น ไม่ใช่เพิ่ม raw ทั้งก้อนแบบไม่คัด

## สถานะชุดนี้

- จำนวน target records: 29
- scan_success: 29
- raw หลักอยู่ที่ `dataset/raw-curated/dec-ml-scan-2026-08-25/`
- ชุด feature สำหรับทดลองอยู่ในโฟลเดอร์นี้

## ไฟล์สำคัญ

| ไฟล์ | ใช้ทำอะไร |
| --- | --- |
| `SCAN-SUMMARY-TH.md` | สรุปภาษาไทยของรอบสแกน |
| `observations.jsonl` | observation ระดับ target จาก scanner/fingerprint |
| `features.csv` | feature table สำหรับทดลอง ML ranking |
| `labels-draft.jsonl` | weak label จากชื่อ Vulhub path |
| `reports/dec-ml-scan-ranking-report-th.md` | รายงานทดสอบ ML ranking ภาษาไทยจากชุด scan นี้ |
| `reports/dec-ml-scan-ranking-metrics.json` | metric เต็มสำหรับอ่านด้วย script/notebook |
| `dec-ml-scan-2026-08-25.tar.gz` | archive ของ raw-curated รอบนี้ |

## ควรใช้ยังไง

ใช้ `features.csv` เป็น input ทดลอง ranking model ได้ทันที โดยเริ่มจากคอลัมน์พวกนี้:

- `protocol_kind`
- `port`
- `candidate_family`
- `title`
- `server`
- `x_powered_by`
- `http_status`
- `nmap_service_line`
- `scan_success`
- `has_nmap`
- `has_probe`
- `has_nikto`
- `has_wapiti`

ใช้ `labels-draft.jsonl` เพื่อเทียบว่า target นี้ควรอยู่ family ไหน แต่ต้องจำไว้ว่า label นี้ยังอ่อน เพราะได้จากชื่อ lab/folder ของ Vulhub

รัน evaluator รอบนี้ได้ด้วย:

```powershell
python scripts\evaluate_dec_ml_scan_20260825.py
```

ผลล่าสุด:

- ML logistic ranker: Top-1 `0.759`, Top-3 `0.862`, mean attempts `2.586`
- Scanner heuristic: Top-1 `0.724`, Top-3 `0.828`, mean attempts `2.724`
- Random expected: Top-1 `0.037`, Top-3 `0.111`, mean attempts `14.000`

ความหมายคือ ML ช่วยลดจำนวน candidate ที่ต้องลองจากค่าเฉลี่ยสุ่มประมาณ 14 เหลือประมาณ 2.6 แต่ยังไม่ใช่ความแม่น exploit จริง เพราะ label ยังเป็น weak label

จุดที่ ML ยังพลาดเกิน Top-3:

- `goahead_CVE-2017-17562`
- `joomla_CVE-2023-23752`
- `shiro_CVE-2016-4437`
- `spring_CVE-2022-22965`

## ยังไม่ควรใช้ยังไง

- อย่าใช้ `candidate_family`, ชื่อ CVE, หรือชื่อ target เป็น feature หลักในการวัดความแม่นจริง เพราะเสี่ยง label leakage
- อย่าถือว่า `labels-draft.jsonl` คือ exploit-success ground truth
- อย่าเทรนรวมกับชุดหลักโดยไม่แยก train/test ตาม family หรือ target group

## งานต่อ

- ทำ validation script สำหรับ target ที่มี probe เช่น Joomla, Grafana, ThinkPHP, Redis, Aria2
- ติดตั้ง ProjectDiscovery `httpx` ตัวจริงแทน Python `httpx`
- จูน `nuclei` ให้เลือก template เฉพาะ CVE เพื่อลด timeout
- normalize ชุดนี้เข้า schema หลักของ Dec ถ้าจะเอาไปรวมกับ 43-target fixed core
