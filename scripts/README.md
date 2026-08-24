# Scripts

โฟลเดอร์นี้เก็บ script สำหรับ build หรือ normalize dataset

## ไฟล์ตอนนี้

| path | ใช้ทำอะไร |
| --- | --- |
| `build_dec_dataset_v2.py` | script build dataset Dec v2 จาก records/raw ที่มี |
| `evaluate_dec_ml_ranking.py` | evaluate ranking ของชุด normalized fixed-core 43 targets |
| `evaluate_dec_ml_scan_20260825.py` | evaluate ranking จาก scanner-derived features ชุด Kali scan 29 targets |

ก่อนรัน script ควรอ่าน `docs/overview/DEC-DATASET-GUIDE-TH.md` และตรวจ path input/output ให้ตรงกับรอบ dataset ที่ต้องการสร้าง

ตัวอย่างรันชุด scan ล่าสุด:

```powershell
python scripts\evaluate_dec_ml_scan_20260825.py
```
