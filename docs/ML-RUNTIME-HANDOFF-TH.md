# Chimera ML Runtime Handoff

เอกสารนี้อธิบายว่า branch นี้เพิ่มอะไรเข้ามาใน `chimera-scanner-dataset` และถ้าจะเอา ML prototype ไปต่อกับ scanner/LLM ต้องใช้ไฟล์ไหนบ้าง

## สถานะปัจจุบัน

ML ฝั่งนี้อยู่ระดับ prototype สำหรับ decision-support แล้ว

ความหมายคือ:

- ใช้ช่วยตัดสินว่า target น่าตรวจ exploit ต่อไหม
- ใช้ช่วยจัดอันดับ exploit family ที่ควรตรวจต่อ
- ใช้ให้ LLM อธิบายเหตุผลจาก feature ได้
- ยังไม่ควรให้ยิง exploit อัตโนมัติเต็มตัวโดยไม่มี human approval

## Runtime Flow

```text
scanner / feature extractor
        ↓
flat precheck feature JSON
        ↓
XGBoost Exploitability Gate
        ↓
ถ้า likely_exploitable
        ↓
XGBoost Family Ranker
        ↓
final decision สำหรับ LLM / operator
```

## ไฟล์ที่อัปเข้ามา

```text
ml-runtime/
  models/prototype/
    prototype_manifest.json
    gate_precondition_only.json
    family_ranker.json
  scripts/
    predict_prototype.py
    evaluate_runtime_predictions.py
    train_family_ranker.py
    train_gate_profiles.py
    train_runtime_models.py
  requirements.txt
  feature-schema/
    runtime_feature_schema.json
  sample-features/
    full_feature_template.json
    redis_positive_example.json
    redis_negative_example.json
    grafana_positive_example.json
    solr_velocity_positive_example.json
    solr_velocity_negative_example.json
    couchdb_positive_example.json
    tomcat_put_positive_example.json
    unknown_drupal_example.json
docs/
  ML-RUNTIME-HANDOFF-TH.md
  ML-RUNTIME-USAGE-TH.md
  ML-FEATURE-CONTRACT-TH.md
```

## ความหมายของ model artifacts

`gate_precondition_only.json`

คือ XGBoost classifier ที่ตอบว่า target นี้น่าจะ exploit ได้ไหม โดยใช้เฉพาะ precheck feature ที่รู้ได้ก่อนยิง exploit

Output สำคัญ:

- `likely_exploitable`: น่าตรวจต่อ
- `low_confidence`: ยังไม่มั่นใจ ต้องเก็บ evidence เพิ่ม
- `no_exploit`: ยังไม่ควรตรวจ exploit ต่อ

`family_ranker.json`

คือ XGBoost ranker ที่ทำงานหลัง Gate ผ่านแล้วเท่านั้น หน้าที่คือจัดอันดับ family เช่น `redis`, `grafana`, `tomcat_put`, `tomcat_ajp`, `solr_velocity`, `couchdb_auth`

`prototype_manifest.json`

คือ metadata สำหรับ runtime บอกว่า:

- โหลด model path ไหน
- Gate ใช้ feature อะไร
- threshold เท่าไหร่
- Ranker รู้จัก family อะไรบ้าง
- train มาจาก dataset ไหน
- metric ล่าสุดของ model คืออะไร

`feature-schema/runtime_feature_schema.json`

คือ schema สำหรับ scanner integration สรุปจาก manifest จริง มีรายการ Gate features, optional scanner features, candidate families และ field ที่ห้ามใช้เป็น precheck feature

`sample-features/full_feature_template.json`

คือ template เต็มที่ใส่ feature runtime ที่ scanner อาจส่งได้ โดย default เป็น 0 ทั้งหมด ใช้เป็น starting point ตอนเขียน feature extractor

## Runtime Safety Guard ล่าสุด

runtime script เวอร์ชันนี้มี guard หลัง Ranker แล้ว

ภาษาคนคือ:

```text
ถ้า family ที่ชนะคะแนนไม่ชนะขาด หรือมีหลักฐานเฉพาะ family ไม่พอ ระบบจะไม่บอกว่าพร้อมตรวจต่อทันที
```

field ที่ LLM/operator ควรอ่านเพิ่ม:

- `ranker.confidence`
- `ranker.family_readiness`

เพิ่ม guard จาก validation ล่าสุด:

- Redis ที่ `redis_detected=1` แต่ `lua_available=0` และ `known_family_signal_count=0` จะถูก downgrade
- Grafana ที่ `path_traversal_blocked=1` และ `public_plugin_path_accessible=0` จะถูก downgrade
- ถ้า scanner ส่ง `known_family_signal_count=0` runtime จะถือว่า family ที่ Ranker เลือกยังไม่พร้อม (`family_readiness.ready=false`)

## Model ที่ใช้

Gate:

```text
XGBClassifier
objective = binary:logistic
profile = precondition_only
threshold = 0.15
train targets = 67
```

Ranker:

```text
XGBRanker
objective = rank:pairwise
positive train targets = 28
candidate families = 16
```

## Candidate Families

Runtime prototype รู้จัก 16 families:

```text
couchdb_auth
elasticsearch
flask
grafana
jenkins
joomla
nextjs
nexus
nginx
redis
shiro_key
solr_velocity
struts2
thinkphp_rce
tomcat_ajp
tomcat_put
```

ถ้า scanner เจอ product/family นอกกลุ่มนี้ ต้องส่ง unknown-family signal ให้ runtime guard ส่งไป `unknown_family_triage`

## Validation ล่าสุด

ชุด `ranker-guard-unknown-validation-v01` ทดสอบ 24 targets:

| กลุ่ม | จำนวน | ผล |
| --- | ---: | --- |
| Known family | 12 | 12/12 safe |
| Unknown family | 6 | 6/6 ถูกส่งไป unknown triage |
| Weak/noisy | 6 | 6/6 ไม่ถูกปล่อยเป็น exploit |

ผล runtime หลังแก้ guard:

| Metric | Result |
| --- | ---: |
| Gate FP/FN | 0 / 0 |
| Known-positive Ranker Top-1 | 1.0000 |
| Unknown-family rejected | 1.0000 |
| Safety flow | 1.0000 |
| Strict flow | 1.0000 |

หมายเหตุ: ตัวเลขนี้เป็นผล validation ของชุดควบคุม 24 targets ยังไม่ใช่ production accuracy

## ผล validation ล่าสุด

Default runtime ผ่าน validation ชุดล่าสุดใน repo ML progress:

Solr unseen schema validation:

```text
total targets = 4
Gate FP/FN = 0 / 0
Ranker Top-1 = 1.0000
Safety flow = 1.0000
```

Multi-family unseen validation:

```text
total targets = 10
families = Redis, Grafana, Tomcat PUT, Tomcat AJP, CouchDB
Gate FP/FN = 0 / 0
Ranker Top-1 = 1.0000
Safety flow = 1.0000
Strict flow = 1.0000
```

ข้อควรระวัง: ตัวเลขนี้เป็น prototype validation บนชุดเล็ก ไม่ใช่ production accuracy

## สิ่งที่ห้ามอัปหรือห้ามใช้ผิดที่

ไม่ควรอัป:

- raw evidence ทั้งโฟลเดอร์
- prompts
- post-exploit logs ที่หนักหรือมีข้อมูล sensitive
- target ที่ยัง quarantine

ไม่ควรใช้เป็น precheck feature:

- `tool_metasploit_success`
- `msf_check_confirmed`
- `rce_confirmed`
- `manual_poc_failed`

เหตุผลคือ feature พวกนี้รู้หลังยิง exploit หรือหลัง verify แล้ว ถ้าใช้ตอน train/precheck จะทำให้ model ดูแม่นเกินจริง

## สถานะสำหรับ LLM

พร้อมต่อ LLM แบบ advisor/planner:

- อธิบาย decision
- สรุป reason features
- เลือก next probe
- สร้าง report
- เตือนเมื่อควรหยุดหรือ triage

ยังไม่พร้อมให้ LLM ยิง exploit เองอัตโนมัติเต็มตัว
