# Checklist หลัง opencode ฝั่ง Kali สแกนเสร็จ

ใช้ฝั่ง Windows/repo หลังจาก Kali copy ผลมาที่ shared folder แล้ว

## 1. เช็กว่าไฟล์กลับมาครบ

```powershell
Test-Path C:\Users\rapii\Desktop\kali-share\dataset\dec-validation-manual\validation-results.jsonl
Test-Path C:\Users\rapii\Desktop\kali-share\dataset\dec-validation-manual\SCAN-SUMMARY-TH.md
Get-ChildItem C:\Users\rapii\Desktop\kali-share\dataset\dec-validation-manual\raw-curated -Recurse -File
```

## 2. Import ผล scan เข้า experiment

```powershell
python scripts\ingest_dec_kali_validation_run.py --run-dir C:\Users\rapii\Desktop\kali-share\dataset\dec-validation-manual
```

## 3. สร้าง feature ใหม่จาก evidence

```powershell
python scripts\enrich_dec_ml_scan_features.py
```

## 4. Evaluate ML ใหม่

```powershell
python scripts\evaluate_dec_ml_scan_20260825.py --label-mode merged
```

## 5. Export attack order ใหม่

```powershell
python scripts\export_dec_attack_order.py --prediction-file experiments\dec-ml-scan-2026-08-25\reports\dec-ml-scan-ranking-merged-predictions.json --suffix merged --top-k 5
```

## 6. ดูว่ารอบต่อไปต้องสแกนอะไร

เปิดไฟล์:

```text
experiments/dec-ml-scan-2026-08-25/reports/dec-ml-scan-ranking-merged-failures.json
experiments/dec-ml-scan-2026-08-25/reports/dec-ml-scan-ranking-merged-report-th.md
```

ถ้า Spring/Shiro/GoAhead ยังพลาด ให้สร้าง queue รอบใหม่จาก failure report เท่านั้น อย่าเพิ่ม target แบบหว่าน เพราะจะเปลืองเวลาและทำให้สรุปยาก

