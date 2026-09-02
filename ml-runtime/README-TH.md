# ML Runtime Prototype

โฟลเดอร์นี้เป็น runtime handoff สำหรับนำ Chimera ML prototype ไปต่อกับ scanner หรือ LLM advisor

เริ่มอ่าน:

- `../docs/ML-RUNTIME-HANDOFF-TH.md`
- `../docs/ML-RUNTIME-USAGE-TH.md`
- `../docs/ML-FEATURE-CONTRACT-TH.md`

ไฟล์ model:

- `models/prototype/gate_precondition_only.json`
- `models/prototype/family_ranker.json`
- `models/prototype/prototype_manifest.json`

ไฟล์ script หลัก:

- `scripts/predict_prototype.py`

ไฟล์สำหรับลองใช้ทันที:

- `requirements.txt`
- `sample-features/redis_positive_example.json`
- `sample-features/redis_negative_example.json`
- `sample-features/tomcat_put_positive_example.json`

ติดตั้ง dependency:

```bash
python -m pip install -r ml-runtime/requirements.txt
```

ลอง predict:

```bash
python ml-runtime/scripts/predict_prototype.py \
  --features ml-runtime/sample-features/redis_positive_example.json \
  --model-dir ml-runtime/models/prototype \
  --top-k 5
```

ข้อควรระวัง: runtime นี้ยังเป็น prototype สำหรับ decision-support ไม่ใช่ autonomous exploit runner
