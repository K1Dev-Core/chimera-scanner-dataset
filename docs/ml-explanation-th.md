# สรุปการทำงานของ Chimera ML

เอกสารนี้สรุป Dataset, Feature, Label, XGBoost Gate, Family Ranker, การให้คะแนน, Loss, Metrics และ Runtime Guard ของโปรเจกต์ `chimera-ml-progress`

## 1. เป้าหมายของระบบ

ระบบช่วยตอบสองคำถาม:

1. Target มีหลักฐานพอให้ส่งต่อไปตรวจสอบหรือไม่
2. ถ้าควรตรวจสอบ ควรเริ่มจาก Exploit Family ใดก่อน

```text
Scanner Evidence → Features → XGBoost Gate → Family Ranker → Runtime Guard → Verification
```

ระบบเป็น Decision Support ไม่ได้ยืนยันว่า Exploit สำเร็จแน่นอน

## 2. Dataset และ Feature

แต่ละแถวของ Dataset แทน Target หนึ่งตัว เช่น Redis, Grafana หรือ CouchDB

ตัวอย่าง Feature:

```text
service_port
redis_detected
redis_info_accessible
lua_available
auth_required
no_auth_required
version_patched
version_in_vulnerable_range
precondition_pass_count
precondition_fail_count
grafana_detected
method_put_allowed
```

Feature คือหลักฐานจาก Scanner ที่แปลงเป็นตัวเลข เช่น:

```text
redis_detected = 1
lua_available = 1
auth_required = 0
```

Precheck Feature รู้ได้ก่อน Verification ส่วน Postcheck Feature เช่น `rce_confirmed` รู้หลัง Verification และไม่ควรใช้ทำนายก่อนตรวจจริง เพราะทำให้เกิด Data Leakage

## 3. XGBoost Gate

Gate เป็น Binary Classifier ตอบว่า Target ควรเข้าสู่ Safe Verification หรือไม่

```text
0 = no_exploit / ยังไม่ควรตรวจต่อ
1 = likely_exploitable / มีหลักฐานพอให้ตรวจต่อ
```

```text
Features → XGBClassifier → Probability → Threshold → 0 หรือ 1
```

ตัวอย่าง:

```text
Probability = 0.83
Threshold = 0.15
0.83 >= 0.15 → likely_exploitable
```

คำว่า `likely_exploitable` เป็นผลลัพธ์แบบข้อความ แต่ตอน Train ควร Encode เป็น `1` และ `no_exploit` เป็น `0`

## 4. การให้คะแนนของ Decision Tree

Feature เดินผ่านเงื่อนไขจนถึง Leaf Node:

```text
redis_detected == 1 ?
├── No  → Leaf weight = -0.25
└── Yes → lua_available == 1 ?
          ├── No  → Leaf weight = +0.40
          └── Yes → Leaf weight = +0.45
```

ถ้า `redis_detected=1` และ `lua_available=1` จะเดินเส้นทาง `Yes → Yes` และได้คะแนน `+0.45`

```text
Decision Node = เลือกเส้นทาง
Leaf Node = ให้คะแนน
```

Root และ Internal Node ไม่ได้บวกคะแนน เพราะมีหน้าที่แบ่งข้อมูล ส่วน Leaf เป็นกลุ่มข้อมูลที่ถูกแบ่งละเอียดพอแล้วจึงกำหนดน้ำหนักได้

## 5. Tree หลายต้น

Tree ใหม่แก้ Error ที่เหลือจาก Tree ก่อนหน้า:

```text
Features → Tree 1 → คำนวณ Error → Tree 2 → Tree 3 → รวมคะแนน
```

ตัวอย่าง:

```text
Tree 1 = +0.45
Tree 2 = +0.30
Tree 3 = +0.10
คะแนนรวม = 0.85
```

สูตรทั่วไป:

\[
F(x)=base\_score+\eta f_1(x)+\eta f_2(x)+...+\eta f_K(x)
\]

`η` คือ Learning Rate ซึ่งลดอิทธิพลของแต่ละ Tree

## 6. Loss, Gradient และ Hessian

```text
Prediction → Loss → Gradient/Hessian → สร้าง Tree ถัดไป
```

Gate ใช้ Binary Log Loss:

\[
L=-[y\log(p)+(1-y)\log(1-p)]
\]

ถ้า Label จริง `y=1` แต่โมเดลทำนาย `p=0.20` จะมี Loss สูง เพราะให้คะแนน Positive ต่ำเกินไป

Gradient บอกทิศทางการแก้:

\[
g=p-y
\]

ถ้า `p=0.20, y=1` จะได้ `g=-0.80` หมายถึงควรเพิ่มคะแนน

Hessian บอกขนาดการแก้:

\[
h=p(1-p)=0.20(0.80)=0.16
\]

จำง่าย ๆ: `Gradient = แก้ไปทางไหน`, `Hessian = แก้มากน้อยแค่ไหน`

## 7. Leaf Weight และค่า λ

สำหรับข้อมูลใน Leaf เดียวกัน ให้ `G` เป็นผลรวม Gradient และ `H` เป็นผลรวม Hessian:

\[
w^*=-\frac{G}{H+\lambda}
\]

ตัวอย่าง:

```text
G = -2.4
H = 1.6
λ = 0.1
w = -(-2.4)/(1.6+0.1) = 1.41
```

`λ=0.1` คือ Regularization ช่วยลดการปรับคะแนนที่แรงเกินไปและควบคุมความซับซ้อนของโมเดล

Gradient และ Hessian ใช้ทั้งเลือก Split ที่ลด Loss ได้ดีที่สุดและคำนวณน้ำหนักของ Leaf จึงใช้สร้าง Tree ใหม่ทั้งต้น ไม่ใช่เฉพาะ Leaf

## 8. XGBoost Family Ranker

เมื่อ Gate ผ่าน Ranker จะจัดลำดับ Exploit Family โดยใช้:

```text
Feature ของ Target + Feature เฉพาะ Candidate Family
```

ถ้ามี Candidate 3 ตัว:

```text
(Target A, Redis)
(Target A, Grafana)
(Target A, Tomcat)
```

Candidate ทุกตัวใช้ Model และ Tree ชุดเดียวกัน:

```text
Redis   → Tree 1 → Tree 2 → Tree 3 → คะแนน Redis
Grafana → Tree 1 → Tree 2 → Tree 3 → คะแนน Grafana
Tomcat  → Tree 1 → Tree 2 → Tree 3 → คะแนน Tomcat
```

ไม่ได้สร้าง Tree ใหม่แยกให้แต่ละ Candidate แต่คะแนนต่างกันเพราะ Feature และเส้นทางต่างกัน

ตัวอย่าง:

```text
Redis = 0.85
Grafana = 0.15
Tomcat = -0.25
```

ผลลัพธ์คือ `Redis > Grafana > Tomcat`

## 9. Label และ Pairwise Loss ของ Ranker

ถ้าตรวจสอบจริงแล้ว Target A เป็น Redis:

| Target | Candidate Family | Rank Label |
|---|---|---:|
| Target A | Redis | 1 |
| Target A | Grafana | 0 |
| Target A | Tomcat | 0 |

ความหมายคือ `Redis > Grafana` และ `Redis > Tomcat`

ถ้าคำตอบจริงคือ Redis แต่โมเดลให้ Redis ต่ำกว่า Grafana โมเดลจะเรียงผิด Pairwise Loss สูง และ Tree ถัดไปจะเพิ่มคะแนน Redis กับลดคะแนน Grafana

\[
L=\log(1+e^{-(s_{correct}-s_{wrong})})
\]

## 10. Metrics ของ Gate

|  | ทำนาย Positive | ทำนาย Negative |
|---|---:|---:|
| จริงเป็น Positive | TP | FN |
| จริงเป็น Negative | FP | TN |

- `TP`: ควรตรวจต่อและทายถูก
- `FP`: บอกให้ตรวจต่อแต่จริง ๆ ไม่ควร
- `TN`: ไม่ควรตรวจต่อและทายถูก
- `FN`: ควรตรวจต่อแต่ถูกคัดทิ้ง

ตัวอย่าง `TP=28, FP=2, TN=37, FN=0`

```text
Accuracy  = (TP+TN)/(TP+TN+FP+FN) = 65/67 = 97.01%
Precision = TP/(TP+FP) = 28/30 = 93.33%
Recall    = TP/(TP+FN) = 28/28 = 100%
F1        = 2×(Precision×Recall)/(Precision+Recall) = 96.55%
```

โปรเจกต์นี้ควรให้ความสำคัญกับ Recall เพราะ FN คือ Target ที่ควรตรวจต่อแต่โมเดลคัดทิ้ง

## 11. Metrics ของ Ranker

### Top-1 และ Top-3

Top-1 ตรวจว่า Family ที่ถูกต้องอยู่ในอันดับ 1 หรือไม่ ถ้าถูก 6 จาก 8 Target:

```text
Top-1 = 6/8 = 75%
```

Top-3 ตรวจว่า Family ที่ถูกต้องอยู่ใน 3 อันดับแรกหรือไม่ แม้อันดับ 1 จะผิดก็ตาม

### MRR

MRR ย่อมาจาก Mean Reciprocal Rank ใช้วัดว่า Family ที่ถูกต้องอยู่ใกล้อันดับ 1 แค่ไหน

\[
Reciprocal\ Rank=\frac{1}{r}
\]

| อันดับที่ถูก | Reciprocal Rank |
|---:|---:|
| 1 | 1.00 |
| 2 | 0.50 |
| 3 | 0.33 |
| 4 | 0.25 |

ตัวอย่าง:

```text
Target A: อันดับ 1 → 1.00
Target B: อันดับ 2 → 0.50
Target C: อันดับ 4 → 0.25
MRR = (1.00+0.50+0.25)/3 = 0.5833 = 58.33%
```

ถ้า True Family ไม่อยู่ใน Candidate List ให้ค่าเป็น 0 และควรส่งเข้า `unknown_family`

## 12. Runtime Guard

Runtime Guard ตรวจผลหลัง Gate และ Ranker เพื่อไม่ให้ระบบเชื่อคะแนนของโมเดลอย่างเดียว

### Confidence

ตรวจระยะห่างระหว่างอันดับหนึ่งกับอันดับสอง:

```text
Redis = 2.91
Grafana = 0.43
Margin = 2.48 → มั่นใจมากกว่า
```

ถ้าคะแนนสูสี เช่น `0.52` กับ `0.49` ให้เป็น `low_confidence`

### Family Readiness

ตรวจว่ามีหลักฐานเฉพาะ Family หรือไม่ เช่น Redis อาจต้องมี:

```text
redis_detected = 1
redis_info_accessible = 1
lua_available = 1
```

### Unknown Family

ถ้า Target เป็น Family ที่โมเดลไม่รู้จัก ไม่ควรฝืนเลือก Family ที่ใกล้ที่สุด แต่ควรส่งไป `unknown_family_triage`

## 13. Train, Test และ Feedback

Gate ใช้หนึ่ง Target ต่อหนึ่งแถว:

```text
Features → Label 0 หรือ 1
```

Ranker ใช้ Candidate หลายแถวต่อ Target และควรแบ่ง Train/Test เป็นกลุ่ม Target:

```text
Train: Target B, C, D
Test: Target A พร้อม Candidate ทุกตัว
```

ไม่ควรสุ่ม Candidate ของ Target เดียวกันไปอยู่ทั้ง Train และ Test เพราะคะแนนอาจดูดีเกินจริง

หลัง Verification ผลจริงจะถูกนำกลับไปสร้าง Ground Truth และใช้ปรับปรุง Dataset ในรอบถัดไป

## 14. สรุป Flow

```text
Features
   ↓
XGBClassifier
   ↓
Probability
   ↓
Threshold
   ↓
Gate Decision
   ↓
Target Features + Candidate Family Features
   ↓
XGBRanker
   ↓
คะแนนของแต่ละ Family
   ↓
เรียงลำดับ
   ↓
Runtime Guard
   ↓
final_decision
   ↓
Verification
   ↓
Feedback กลับเข้า Dataset
```

## แหล่งอ้างอิงใน Repository

- Dataset: `reports/evaluations/ranker-schema-backfill-redis-grafana-v01/target-exploitability-family-ranking-backfill-plus-redis-grafana.csv`
- Gate: `scripts/train_gate_profiles.py`
- Ranker และ Family Feature Map: `scripts/train_family_ranker.py`
- เอกสาร ML: `docs/10-ml-from-zero-th.md`
- Feature Schema: `docs/04-feature-schema-th.md`
