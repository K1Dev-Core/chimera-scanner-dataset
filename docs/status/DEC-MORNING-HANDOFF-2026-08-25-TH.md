# Dec Morning Handoff - 2026-08-25

สรุปสำหรับเริ่มงานต่อหลังพัก

## สถานะล่าสุด

- branch ที่ถูกต้อง: `Dec`
- remote ล่าสุดที่ยืนยัน: `98f02029fc41434e803e2fe5430bbaec56c09f4b`
- dataset หลัก: `generated/dec-vulhub-2026-08-24-fixed-core/`
- ML scan ล่าสุด: `experiments/dec-ml-scan-2026-08-25/`
- shared folder สำหรับ Kali: `C:\Users\rapii\Desktop\kali-share\dataset\dec-kali-validation-run-kit`

## สิ่งที่พร้อมแล้ว

- `derived/attack-order-top5.csv`: ML แนะนำลำดับ candidate family ต่อ target
- `validation-target-queue.csv`: 9 targets ที่ควร validate ก่อน
- `hex-next-target-candidates.csv`: 20 targets จาก Hex สำหรับเพิ่ม dataset
- `hex-next-scan-queue.csv`: 10 targets แรกจาก Hex ที่ควรสแกนต่อ
- `scripts/kali/dec_validation_runner.py`: runner ฝั่ง Kali สำหรับเก็บ safe evidence

## คำสั่งบน Kali

```bash
cd /media/sf_kali-share/dataset/dec-kali-validation-run-kit
python3 scripts/kali/dec_validation_runner.py \
  --queue validation-target-queue.csv \
  --features features.csv \
  --output-dir /home/kali/reports/dec-validation-manual
```

หลังรันเสร็จ:

```bash
mkdir -p /media/sf_kali-share/dataset/dec-validation-manual
cp -a /home/kali/reports/dec-validation-manual/. /media/sf_kali-share/dataset/dec-validation-manual/
```

## เอาผลกลับเข้า Dec

```powershell
python scripts\import_dec_validation_results.py --input path\to\validation-results.jsonl
python scripts\evaluate_dec_ml_scan_20260825.py --label-mode merged
python scripts\export_dec_attack_order.py --prediction-file experiments\dec-ml-scan-2026-08-25\reports\dec-ml-scan-ranking-merged-predictions.json --suffix merged --top-k 5
python scripts\validate_dec_artifacts.py
```

## ข้อควรระวัง

- อย่า stage/commit `dataset/raw/autorecon/**`
- สแกนเฉพาะ local Vulhub/Docker lab เท่านั้น
- raw รอบต่อไปต้องเป็น `raw-curated` ไม่เอา cache/runtime/dependency
