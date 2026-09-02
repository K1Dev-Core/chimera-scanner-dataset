# วิธีใช้ ML Runtime Prototype

เอกสารนี้เป็นคู่มือเรียกใช้ runtime ที่อยู่ใน branch นี้

## Dependency ขั้นต่ำ

ต้องมี Python และ package:

```text
numpy
xgboost
scikit-learn
```

ติดตั้งจากไฟล์ที่ให้ไว้:

```bash
python -m pip install -r ml-runtime/requirements.txt
```

สำหรับ inference จริง ใช้หลัก ๆ:

```text
numpy
xgboost
```

แต่ไฟล์ `predict_prototype.py` import helper จาก `train_family_ranker.py` และ `train_gate_profiles.py` ด้วย จึงต้องวาง scripts ทั้งชุดไว้ด้วยกัน

## โครงสร้างที่ runtime คาดหวัง

เมื่อเอาไปใช้งานใน repo scanner แนะนำวางแบบนี้:

```text
ml-runtime/
  models/prototype/
    prototype_manifest.json
    gate_precondition_only.json
    family_ranker.json
  scripts/
    predict_prototype.py
    train_family_ranker.py
    train_gate_profiles.py
```

## Input

Runtime รับ flat JSON feature object 1 target ต่อ 1 ไฟล์

ตัวอย่าง Redis positive:

```json
{
  "target_id": "redis_positive_example",
  "redis_detected": 1,
  "redis_info_accessible": 1,
  "lua_available": 1,
  "auth_required": 0,
  "no_auth_required": 1,
  "version_in_vulnerable_range": 1,
  "version_patched": 0,
  "known_family_signal_count": 2,
  "unknown_family_signal_count": 0,
  "unknown_product_detected": 0
}
```

มี sample input ให้ลองใช้ได้ทันทีที่:

```text
ml-runtime/sample-features/redis_positive_example.json
ml-runtime/sample-features/redis_negative_example.json
ml-runtime/sample-features/tomcat_put_positive_example.json
```

## Command

จาก root repo:

```powershell
python ml-runtime/scripts/predict_prototype.py `
  --features sample-features/redis_positive_example.json `
  --model-dir ml-runtime/models/prototype `
  --top-k 5
```

ถ้าใช้ Linux:

```bash
python3 ml-runtime/scripts/predict_prototype.py \
  --features sample-features/redis_positive_example.json \
  --model-dir ml-runtime/models/prototype \
  --top-k 5
```

## Output

ตัวอย่าง output:

```json
{
  "target_id": "redis_positive_example",
  "gate": {
    "model": "gate_precondition_only",
    "score": 0.933099,
    "threshold": 0.15,
    "decision": "likely_exploitable"
  },
  "ranker": {
    "model": "family_ranker",
    "decision": "known_family_ready",
    "top_families": [
      {
        "family": "redis",
        "score": 2.917933,
        "positive_signals": 5,
        "negative_signals": 0,
        "specific_positive_signals": 3
      }
    ]
  },
  "final_decision": "ready_for_safe_verification",
  "recommended_next_action": "run_safe_metasploit_check_or_manual_probe",
  "reason_features": [
    "lua_available",
    "no_auth_required",
    "redis_detected",
    "redis_info_accessible",
    "version_in_vulnerable_range"
  ],
  "safety_note_th": "ยังไม่ยิง exploit อัตโนมัติ ต้องใช้ Metasploit check/manual PoC หลังผู้ใช้ยืนยัน"
}
```

## วิธีแปล final_decision

`do_not_exploit_now`

ยังไม่ควรตรวจ exploit ต่อในตอนนี้ เพราะ evidence ไม่พอหรือมี blocker ชัดเจน

`needs_more_evidence`

ยังไม่มั่นใจพอ ควรให้ scanner เก็บ precheck evidence เพิ่ม เช่น auth, endpoint, version, config access

`ready_for_safe_verification`

พร้อมเข้าสู่ขั้น verification แบบปลอดภัย โดยยังต้องให้ operator หรือ policy layer อนุมัติก่อน

`manual_triage_before_exploit`

มีสัญญาณบวก แต่มี blocker หรือความไม่มั่นใจใน family ต้องตรวจมือก่อน

`unknown_family_triage`

target อาจน่าสนใจ แต่ไม่อยู่ใน family ที่ model รู้จัก ต้องหยุดการเลือก exploit family อัตโนมัติ

## ตัวอย่าง Negative

Redis ที่ต้อง auth:

```json
{
  "target_id": "redis_negative_example",
  "redis_detected": 1,
  "auth_required": 1,
  "redis_info_accessible": 0,
  "lua_available": 0,
  "version_in_vulnerable_range": 1
}
```

ผลที่คาดหวัง:

```text
gate_decision = low_confidence หรือ no_exploit
final_decision = needs_more_evidence หรือ do_not_exploit_now
```

ไม่ควรได้:

```text
final_decision = ready_for_safe_verification
```

## Integration กับ LLM

LLM ควรอ่าน field เหล่านี้:

- `gate.decision`
- `gate.score`
- `ranker.top_families`
- `final_decision`
- `recommended_next_action`
- `reason_features`
- `schema_warnings`

LLM ไม่ควรใช้ score เพียงตัวเดียวเพื่อตัดสิน ต้องดู `final_decision` เป็นหลัก
