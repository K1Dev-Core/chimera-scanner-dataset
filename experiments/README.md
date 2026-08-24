# Experiments

โฟลเดอร์นี้เก็บข้อมูลทดลองที่มีประโยชน์ แต่ยังไม่ใช่ normalized dataset หลักของ `Dec`

## ชุดที่มีตอนนี้

| path | คืออะไร |
| --- | --- |
| `hex-2026-08-05/` | records, feature seeds, demo model และ metadata ที่ import จาก branch Hex |
| `zap-n8n-5-8-69/` | ZAP report สำหรับ n8n target ทดลอง |

## ใช้ยังไง

- ใช้เลือก target เพิ่มจาก `hex-2026-08-05/vulhub-cve-bulk/records/lab-index.jsonl`
- ใช้ดู feature seed และ scanner coverage เพิ่ม
- ใช้เป็นตัวอย่าง demo/ranking ได้

## ยังไม่ควรใช้ยังไง

- อย่าใช้เป็น ground truth สุดท้ายทันที
- อย่า train รวมกับชุดหลักโดยไม่ normalize เข้า schema ของ `Dec`
- ระวัง feature ที่มีชื่อ CVE, lab name หรือ target name เพราะอาจเกิด label leakage
