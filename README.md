# Chimera Scanner Dataset

repo นี้เก็บ dataset สำหรับทดลองทำ cyber vulnerability scanner dataset จาก Vulhub/Kali tools เพื่อใช้กับ demo, feature engineering และ baseline ML

branch ที่ใช้งานตอนนี้คือ `Dec`

## อ่านเร็วที่สุด

ถ้าเพิ่งเปิด repo นี้ ให้เริ่มตามลำดับนี้:

1. อ่านคู่มือภาพรวมภาษาไทย: `docs/overview/DEC-DATASET-GUIDE-TH.md`
2. เปิด dataset หลัก 43 targets: `generated/dec-vulhub-2026-08-24-fixed-core/`
3. ดู raw scanner output ที่คัดแล้ว: `dataset/raw-curated/`
4. ดูข้อมูลทดลอง ML scan ล่าสุด 29 targets: `experiments/dec-ml-scan-2026-08-25/`
5. ดูข้อมูลทดลองจาก `Hex`: `experiments/hex-2026-08-05/`
6. อ่านสถานะ/ประวัติงาน: `docs/status/`

## โครงสร้าง repo

| path | คืออะไร | ใช้เมื่อ |
| --- | --- | --- |
| `generated/` | normalized dataset ที่พร้อมใช้ | ทำ analysis, feature engineering, demo, baseline ML |
| `dataset/raw-curated/` | raw output จาก scanner ที่คัดเฉพาะผล scan จริง | ตรวจ evidence และ parse feature เพิ่ม |
| `dataset/raw/` | raw เก่าที่ยังไม่ curate ทั้งหมด | อ้างอิงเท่านั้น ตอนนี้ AutoRecon มี path ยาวบน Windows |
| `docs/` | คู่มือ สถานะ checklist และบทความอธิบาย | อ่านทำความเข้าใจ project |
| `experiments/` | ชุดทดลองจาก Hex/ZAP ที่ยังไม่ใช่แกนหลัก | ใช้เป็น feature seed หรือไอเดีย target เพิ่ม |
| `scripts/` | script สำหรับ build/normalize dataset | ใช้ตอน regenerate dataset |

## ชุดทดลอง ML scan ล่าสุด

ชุดล่าสุดจาก Kali/Vulhub อยู่ที่:

- summary และ feature table: `experiments/dec-ml-scan-2026-08-25/`
- รายงานทดสอบ ranking: `experiments/dec-ml-scan-2026-08-25/reports/dec-ml-scan-ranking-report-th.md`
- แผน validation/attack order: `experiments/dec-ml-scan-2026-08-25/reports/dec-ml-attack-order-validation-plan-th.md`
- target queue รอบ Kali ถัดไป: `experiments/dec-ml-scan-2026-08-25/validation-target-queue.csv`
- raw-curated evidence: `dataset/raw-curated/dec-ml-scan-2026-08-25/`

รอบนี้มี 29 target records และ scan_success 29 records ใช้สำหรับทดลอง feature/ranking เพิ่มเติม ยังไม่ใช่ exploit-success ground truth ทั้งหมด

ผลประเมินล่าสุดจาก scanner-derived features:

- ML logistic ranker: Top-1 `0.759`, Top-3 `0.862`, mean attempts `2.586`
- Scanner heuristic: Top-1 `0.724`, Top-3 `0.828`, mean attempts `2.724`
- Random expected: Top-1 `0.037`, Top-3 `0.111`, mean attempts `14.000`

คำอ่านสั้น ๆ คือ ML ช่วยเรียง candidate family ได้ดีกว่าสุ่มและดีกว่า heuristic เล็กน้อย แต่ยังมีจุดพลาด เช่น Joomla/Shiro/Spring ที่ scanner evidence ยังไม่เฉพาะพอ จึงต้องทำ exploit validation และเพิ่ม negative controls ต่อ

## ชุดหลักของ Dec

ชุดที่ควรถือเป็นแกนหลักตอนนี้คือ:

`generated/dec-vulhub-2026-08-24-fixed-core/`

ไฟล์สำคัญ:

- `records/targets.jsonl`
- `records/findings.jsonl`
- `records/observations.jsonl`
- `records/validations.jsonl`
- `derived/target-features.json`
- `derived/target-candidate-features.json`
- `labels/target-candidate-labels.jsonl`
- `manifest.json`
- `quality-report.json`

## คำศัพท์สำคัญ

- `target` คือ lab หรือ service ที่ถูกสแกน เช่น Drupal, Jenkins, Tomcat
- `observation` คือข้อมูลทั่วไปที่ scanner เห็น เช่น port เปิด, HTTP status, title, technology
- `finding` คือสิ่งที่ scanner มองว่าน่าสงสัยหรือเป็นช่องโหว่
- `validation` คือหลักฐานหรือ label ว่า target นี้ตรงกับช่องโหว่ที่คาดไว้หรือไม่
- `raw-curated` คือ output ดิบจาก scanner ที่คัดเฉพาะผล scan จริง ไม่เอา cache/runtime/dependency

## สิ่งที่ควรระวัง

- อย่าใช้ชื่อ target หรือ CVE ตรง ๆ เป็น feature สำหรับ train model ถ้าโจทย์คือทำนายช่องโหว่ เพราะจะเกิด label leakage
- ข้อมูลใน `experiments/hex-2026-08-05/` เป็นข้อมูลเสริมและ weak label ไม่ใช่ ground truth exploit success
- `dataset/raw/autorecon/**` ยังมี path ยาวบน Windows จึงยังไม่ควรนำขึ้นหรือใช้ตรง ๆ

รายละเอียดเต็มอยู่ใน `docs/overview/DEC-DATASET-GUIDE-TH.md`
