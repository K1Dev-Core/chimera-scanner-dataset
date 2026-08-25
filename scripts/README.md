# Scripts

โฟลเดอร์นี้เก็บ script สำหรับ build หรือ normalize dataset

## ไฟล์ตอนนี้

| path | ใช้ทำอะไร |
| --- | --- |
| `build_dec_dataset_v2.py` | script build dataset Dec v2 จาก records/raw ที่มี |
| `evaluate_dec_ml_ranking.py` | evaluate ranking ของชุด normalized fixed-core 43 targets |
| `evaluate_dec_ml_scan_20260825.py` | evaluate ranking จาก scanner-derived features ชุด Kali scan 29 targets |
| `export_dec_attack_order.py` | export top-k attack order จาก ML predictions เป็น CSV/JSONL |
| `import_dec_validation_results.py` | validate/import `validation-results.jsonl` จาก Kali ให้เป็น label table |
| `validate_dec_artifacts.py` | ตรวจสุขภาพ artifacts หลักของ Dec เช่น fixed core, ML scan, reports และ candidate rows |

ก่อนรัน script ควรอ่าน `docs/overview/DEC-DATASET-GUIDE-TH.md` และตรวจ path input/output ให้ตรงกับรอบ dataset ที่ต้องการสร้าง

ตัวอย่างรันชุด scan ล่าสุด:

```powershell
python scripts\evaluate_dec_ml_scan_20260825.py
```

หลัง import validation แล้วรัน evaluator แบบรวม validated label กับ weak fallback:

```powershell
python scripts\evaluate_dec_ml_scan_20260825.py --label-mode merged
```

สร้าง attack order top-5 สำหรับให้ Kali/opencode ใช้:

```powershell
python scripts\export_dec_attack_order.py --top-k 5
```

ตัวอย่าง import ผล validation จาก Kali:

```powershell
python scripts\import_dec_validation_results.py --input experiments\dec-ml-scan-2026-08-25\validation-results.example.jsonl
```

ตรวจ artifacts หลักก่อน commit/push:

```powershell
python scripts\validate_dec_artifacts.py
```

validator นี้รวม fixture ของ validation import ด้วย เพื่อเช็กว่า `validated`, `merged`, `validated_negative`, `inconclusive` และ `not_run` ยังทำงานตามที่ตั้งใจ
