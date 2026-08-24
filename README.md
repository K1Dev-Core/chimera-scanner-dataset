# Chimera Scanner Dataset

repo นี้เก็บ dataset สำหรับทดลองทำ cyber vulnerability scanner dataset จาก Vulhub/Kali tools เพื่อใช้กับ demo, feature engineering และ baseline ML

branch หลักที่ใช้งานตอนนี้คือ `Dec`

## เริ่มอ่านตรงไหนดี

ถ้าเพิ่งเปิด repo นี้ ให้เริ่มตามลำดับนี้:

1. อ่านคู่มือไทย: `DEC-DATASET-GUIDE-TH.md`
2. ดู normalized dataset ล่าสุด: `generated/dec-vulhub-2026-08-24-fixed-core/`
3. ดู raw ที่คัดสะอาดแล้ว: `dataset/raw-curated/`
4. ดูของที่ import จาก branch `Hex`: `HEX-BRANCH-PROGRESS-2026-08-05.md`

## ภาพรวมสั้น ๆ

ชุดหลักของ `Dec` ตอนนี้คือ normalized core จำนวน 43 targets

ไฟล์สำคัญอยู่ที่:

- `generated/dec-vulhub-2026-08-24-fixed-core/records/targets.jsonl`
- `generated/dec-vulhub-2026-08-24-fixed-core/records/findings.jsonl`
- `generated/dec-vulhub-2026-08-24-fixed-core/records/observations.jsonl`
- `generated/dec-vulhub-2026-08-24-fixed-core/records/validations.jsonl`
- `generated/dec-vulhub-2026-08-24-fixed-core/derived/target-features.json`
- `generated/dec-vulhub-2026-08-24-fixed-core/derived/target-candidate-features.json`

## คำศัพท์สำคัญ

- `target` คือ lab หรือ service ที่ถูกสแกน เช่น Drupal, Jenkins, Tomcat
- `observation` คือข้อมูลทั่วไปที่ scanner เห็น เช่น port เปิด, HTTP status, title, technology
- `finding` คือสิ่งที่ scanner มองว่าน่าสงสัยหรือเป็นช่องโหว่
- `validation` คือหลักฐานหรือ label ว่า target นี้ตรงกับช่องโหว่ที่คาดไว้หรือไม่
- `raw-curated` คือ output ดิบจาก scanner ที่คัดเฉพาะผล scan จริง ไม่เอา cache/runtime/dependency

## สิ่งที่ควรระวัง

- อย่าใช้ชื่อ target หรือ CVE ตรง ๆ เป็น feature สำหรับ train model ถ้าโจทย์คือทำนายช่องโหว่ เพราะจะเกิด label leakage
- `Hex` import เป็นข้อมูลเสริมและ weak label ไม่ใช่ ground truth exploit success
- `dataset/raw/autorecon/**` ยังมี path ยาวบน Windows จึงยังไม่ควรนำขึ้นหรือใช้ตรง ๆ

## สถานะล่าสุด

- `Dec` normalized core: 43 targets
- raw curated หลัก: `dataset/raw-curated/dec-vulhub-2026-08-24/`
- raw curated จากชุดทดลอง Hex: `dataset/raw-curated/hex-exp-2026-08-05/`
- import จาก `Hex`: compact metadata, feature seeds, demo model pack, multi-vuln web records

รายละเอียดทั้งหมดอยู่ใน `DEC-DATASET-GUIDE-TH.md`
