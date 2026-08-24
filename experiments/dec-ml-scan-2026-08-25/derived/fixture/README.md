# Fixture สำหรับทดสอบ Validation Import

โฟลเดอร์นี้สร้างจาก `validation-results.fixture.jsonl` เพื่อทดสอบว่า pipeline รองรับผล validation หลายสถานะได้จริง

ใช้ทดสอบ:

- `validated_positive`
- `validated_negative`
- `inconclusive`
- `not_run`

ไฟล์นี้ไม่ใช่ผล scan จริงจาก Kali และไม่ควรใช้เป็น ground truth ของโมเดล

คำสั่งสร้างใหม่:

```powershell
python scripts\import_dec_validation_results.py --input experiments\dec-ml-scan-2026-08-25\validation-results.fixture.jsonl --output-dir experiments\dec-ml-scan-2026-08-25\derived\fixture
python scripts\evaluate_dec_ml_scan_20260825.py --label-mode validated --validated-labels experiments\dec-ml-scan-2026-08-25\derived\fixture\validated-labels.csv --output-dir experiments\dec-ml-scan-2026-08-25\reports\fixture
python scripts\evaluate_dec_ml_scan_20260825.py --label-mode merged --validated-labels experiments\dec-ml-scan-2026-08-25\derived\fixture\validated-labels.csv --output-dir experiments\dec-ml-scan-2026-08-25\reports\fixture
```
