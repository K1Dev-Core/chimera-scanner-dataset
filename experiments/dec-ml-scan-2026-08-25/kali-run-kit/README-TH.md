# Dec Kali Validation Run Kit

โฟลเดอร์นี้คือชุดไฟล์ที่ส่งให้ Kali/opencode ใช้สแกน local Vulhub/Docker lab ต่อจากผล ML ranking

## ไฟล์ในชุดนี้

- `features.csv`: target URL/port/fingerprint จาก scanner รอบล่าสุด
- `validation-target-queue.csv`: queue ที่ควร validate ก่อน
- `hex-next-target-candidates.csv`: shortlist target จาก Hex สำหรับสแกนเพิ่มรอบถัดไป
- `attack-order-top5.csv`: family 5 อันดับแรกที่ ML แนะนำต่อ target
- `attack-order-top5-merged.csv`: family 5 อันดับแรกจากโหมด merged
- `scripts/kali/dec_validation_runner.py`: runner เก็บ evidence แบบปลอดภัย
- `DEC-KALI-VALIDATION-QUEUE-PROMPT-TH.md`: prompt สำหรับ opencode
- `DEC-KALI-VALIDATION-RUNBOOK-TH.md`: วิธีรันและวิธีนำผลกลับเข้า ML

## วิธีรันใน Kali

```bash
cd /media/sf_kali-share/dataset/dec-kali-validation-run-kit
python3 scripts/kali/dec_validation_runner.py \
  --queue validation-target-queue.csv \
  --features features.csv \
  --output-dir /home/kali/reports/dec-validation-manual
```

copy ผลกลับ shared folder:

```bash
mkdir -p /media/sf_kali-share/dataset/dec-validation-manual
cp -a /home/kali/reports/dec-validation-manual/. /media/sf_kali-share/dataset/dec-validation-manual/
```

## ข้อควรจำ

- รันเฉพาะ local lab/Vulhub ที่ควบคุมเอง
- ห้ามสแกน public target
- ห้าม destructive exploit
- raw-curated เก็บเฉพาะผล scan/probe จริง ไม่เก็บ cache/runtime/dependency
- ถ้า runner ให้ `inconclusive` ให้ opencode อ่าน evidence แล้วเติม validation ด้วยมือได้
