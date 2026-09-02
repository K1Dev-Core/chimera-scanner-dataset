# chimera-scanner-dataset

## ML Runtime Prototype Handoff

Branch นี้เพิ่มแพ็ก `ml-runtime/` สำหรับทดลองต่อ Chimera ML prototype เข้ากับ scanner และ LLM advisor

เริ่มอ่านจาก:

- [docs/ML-RUNTIME-HANDOFF-TH.md](docs/ML-RUNTIME-HANDOFF-TH.md)
- [docs/ML-RUNTIME-USAGE-TH.md](docs/ML-RUNTIME-USAGE-TH.md)
- [docs/ML-FEATURE-CONTRACT-TH.md](docs/ML-FEATURE-CONTRACT-TH.md)

Runtime ที่เพิ่มเข้ามา:

- `ml-runtime/models/prototype/gate_precondition_only.json`
- `ml-runtime/models/prototype/family_ranker.json`
- `ml-runtime/models/prototype/prototype_manifest.json`
- `ml-runtime/scripts/predict_prototype.py`
- `ml-runtime/requirements.txt`
- `ml-runtime/sample-features/*.json`

สถานะ: พร้อมใช้เป็น prototype สำหรับ decision-support แต่ยังไม่ใช่ autonomous exploit runner

ลองใช้งานเร็ว ๆ:

```bash
python -m pip install -r ml-runtime/requirements.txt
python ml-runtime/scripts/predict_prototype.py \
  --features ml-runtime/sample-features/redis_positive_example.json \
  --model-dir ml-runtime/models/prototype \
  --top-k 5
```
