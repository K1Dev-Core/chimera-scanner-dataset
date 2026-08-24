# DEC Dataset: dec-vulhub-2026-08-24-fixed-core

ชุดนี้คือ normalized/fixed core ล่าสุดของ branch `Dec` สำหรับ Chimera Scanner Dataset

## ภาพรวม

- แหล่งที่มา: Vulhub local lab
- จำนวน target ล่าสุดหลังแก้ schema: 43 targets
- ใช้สำหรับ: analysis, feature engineering, demo, baseline ML
- raw scan files ตัวเต็มไม่ได้อยู่ใน package นี้ทั้งหมด ให้ดู evidence ที่คัดแล้วใน `dataset/raw-curated/`

## ความหมายของ label สำคัญ

`positive_family_match` ใน `labels/target-candidate-labels.jsonl` เป็น weak label จาก ground truth ของ Vulhub

แปลว่า:

- candidate family ตรงกับ family ที่รู้จาก lab เช่น Drupal lab อยู่ในกลุ่ม `cms`
- ไม่ได้แปลว่า exploit สำเร็จทุกแถว
- ถ้ามีการยืนยันด้วย manual PoC, Metasploit หรือ sqlmap จะดู signal แยก เช่น `candidate_validation_available`
- แถวอื่นที่ยังไม่ยืนยันจะเป็น `unknown`

ดังนั้นอย่าใช้ `positive_family_match` เป็นหลักฐาน exploit success โดยตรง

## โครงสร้างไฟล์

| path | คืออะไร |
| --- | --- |
| `records/` | targets, observations, findings, validations, tool_runs, all-records แบบ JSONL |
| `derived/` | feature ระดับ target และ target-candidate |
| `labels/` | label แยกจาก feature เพื่อกัน leakage |
| `normalized/` | per-tool normalized records |
| `metadata/` | target selection และข้อมูล reuse target เก่า |
| `logs/` | pipeline scripts และ run logs |
| `manifest.json` | metadata และจำนวน record |
| `quality-report.json` | ผลตรวจคุณภาพ |
| `checksums.sha256` | checksum ของ artifact |

## Security / data hygiene

- เป็น lab-only ใช้ loopback/private lab ไม่ใช่ public target
- sensitive values เช่น session, cookie, token, password ถูก redact เป็น `[REDACTED]`
- ไม่มี fabricated records
- tool status เช่น `success`, `no_finding`, `failed`, `timeout`, `skipped` ถูกบันทึกตามจริง
