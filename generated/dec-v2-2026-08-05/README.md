# Dec Dataset v2 Generated Output

โฟลเดอร์นี้เป็น generated output รุ่นก่อนหน้า สร้างจาก Dec scanner collection ด้วย `scripts/build_dec_dataset_v2.py`

แหล่งข้อมูลต้นทางเป็น read-only และ raw scanner files ถูกอ้างอิงด้วย relative path ไม่ได้ copy เข้ามาทั้งหมด

## คำสั่ง build

```bash
python scripts/build_dec_dataset_v2.py <source-dataset> <destination>
```

## จำนวน records

| Record set | Count |
| --- | ---: |
| Targets | 10 |
| Observations | 48 |
| Findings | 386 |
| Validations | 5 |
| All records | 449 |
| Target features | 10 |
| Target-candidate features | 80 |
| Target-candidate labels | 80 |

## โครงสร้าง

- `records/`: target, observation, finding, validation records ที่ normalize แล้ว
- `derived/`: feature rows ที่ระวัง label leakage
- `labels/`: labels แยกจาก model features
- `manifest.json`: schema, source policy, tool coverage และ counts
- `quality-report.json`: JSONL validation, redaction count และข้อจำกัด
- `checksums.sha256`: SHA-256 checksum ของ generated artifacts

## ข้อจำกัดสำคัญ

- ไม่มี OpenVAS output ใน source collection นี้
- ZAP และ AutoRecon ตอนนั้นยังเป็น coverage summary ไม่ใช่ parsed findings เต็ม
- 10 targets เป็น Vulhub vulnerable labs ควรเพิ่ม patched controls ก่อนประเมิน model จริง
- `is_ground_truth_family` เป็น label จาก Vulhub family ไม่ใช่ proof ว่า exploit สำเร็จ
- ควร split train/validation/test ตาม target หรือ product family ก่อน join labels
