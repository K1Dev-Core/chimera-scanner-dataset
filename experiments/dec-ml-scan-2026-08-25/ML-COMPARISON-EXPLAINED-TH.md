# อธิบายการวัดผล ML และ Source Code ที่ใช้

เอกสารนี้อธิบายว่า Dec ML scan experiment วัดผลอย่างไร ใช้ source code ไฟล์ไหน และ feature แต่ละชุดทำงานยังไง

## ไฟล์ source code หลัก

### `scripts/enrich_dec_ml_scan_features.py`

หน้าที่:

1. อ่าน `experiments/dec-ml-scan-2026-08-25/features.csv`
2. อ่าน raw evidence จาก `dataset/raw-curated/dec-ml-scan-2026-08-25/<target_id>/raw/`
3. รวมข้อความ evidence จากไฟล์ scan เช่น `curl`, `nmap`, `nikto`, `nuclei`, `wapiti`, validation probe
4. ตัดข้อมูลที่ทำให้โมเดลโกง เช่น `target_id`, ชื่อ CVE, path ของ dataset
5. สร้าง `features-enriched.csv`

คำสั่ง:

```powershell
python scripts\enrich_dec_ml_scan_features.py
```

output:

```text
experiments/dec-ml-scan-2026-08-25/features-enriched.csv
```

### `scripts/evaluate_dec_ml_scan_20260825.py`

หน้าที่:

1. อ่าน target feature จาก `features-enriched.csv`
2. อ่าน label จาก `labels-draft.jsonl` และ `derived/validated-labels.csv`
3. ขยาย 1 target เป็นหลาย candidate family เช่น target เดียวเทียบกับ `spring`, `shiro`, `goahead`, `tomcat`
4. สร้าง candidate-level feature เช่น `title_alias_score`, `evidence_alias_score`, `port_score`
5. เทรน logistic ranker แบบ Leave-One-Target-Out
6. เทียบผล ML กับ heuristic baseline และ random baseline
7. เขียน metrics, predictions, per-target report, failure report

คำสั่ง:

```powershell
python scripts\evaluate_dec_ml_scan_20260825.py --label-mode merged
python scripts\evaluate_dec_ml_scan_20260825.py --label-mode validated
```

output หลัก:

```text
experiments/dec-ml-scan-2026-08-25/reports/dec-ml-scan-ranking-merged-metrics.json
experiments/dec-ml-scan-2026-08-25/reports/dec-ml-scan-ranking-merged-predictions.json
experiments/dec-ml-scan-2026-08-25/reports/dec-ml-scan-ranking-merged-failures.json
experiments/dec-ml-scan-2026-08-25/derived/candidate-family-features-merged.csv
```

### `scripts/export_dec_attack_order.py`

หน้าที่:

อ่าน prediction จาก evaluator แล้ว export ลำดับ candidate family 5 อันดับแรกต่อ target เพื่อส่งให้ Kali/opencode validate ต่อ

คำสั่ง:

```powershell
python scripts\export_dec_attack_order.py --prediction-file experiments\dec-ml-scan-2026-08-25\reports\dec-ml-scan-ranking-merged-predictions.json --suffix merged --top-k 5
```

output:

```text
experiments/dec-ml-scan-2026-08-25/derived/attack-order-top5-merged.csv
```

### `scripts/ingest_dec_kali_validation_run.py`

หน้าที่:

1. อ่านผลจาก Kali shared folder ที่มี `validation-results.jsonl`
2. merge validation labels หลายรอบเข้าด้วยกัน
3. copy raw-curated evidence เข้า dataset
4. เขียน `derived/validated-labels.csv`

คำสั่ง:

```powershell
python scripts\ingest_dec_kali_validation_run.py --run-dir C:\Users\rapii\Desktop\kali-share\dataset\<run_id>
```

## เปรียบเทียบอะไรกับอะไร

ระบบวัดผลไม่ได้ถามว่า exploit สำเร็จจริงทุกตัวหรือยัง แต่ถามว่า:

```text
จาก scanner-derived features โมเดลจัด expected vulnerability family ไว้อันดับต้น ๆ ได้ไหม
```

ตัวที่นำมาเทียบ:

1. `ML logistic ranker`
   - โมเดล logistic regression ที่เทรนจาก candidate-level features
   - ประเมินแบบ Leave-One-Target-Out

2. `Scanner heuristic`
   - rule-based weighted score จาก feature เดียวกัน
   - ใช้เป็น baseline ว่า rule ธรรมดาทำได้แค่ไหน

3. `Random expected`
   - baseline แบบสุ่ม
   - ใช้บอกว่าถ้าไม่ใช้ feature เลยควรแย่ประมาณไหน

4. `Feature ablation`
   - ทดลองตัด feature บางชุดออก เช่น ใช้แค่ port/protocol หรือใช้แค่ text
   - ใช้ดูว่า feature ชุดไหนช่วยจริง

## วิธีวัดผล

### Top-1

ถ้า family ที่ถูกอยู่เป็นอันดับ 1 ถือว่าถูก

ตัวอย่าง:

```text
target = shiro_CVE-2016-4437
rank 1 = shiro
=> Top-1 hit
```

### Top-3

ถ้า family ที่ถูกอยู่ใน 3 อันดับแรก ถือว่าคน/agent ลองไม่เกิน 3 ทางก็เจอแนวที่ถูก

อันนี้สำคัญกับโปรเจกต์เรา เพราะระบบไม่ได้ต้องตอบอย่างเดียวเสมอ แต่ต้องช่วยจัดลำดับโจมตี/validate ให้ถูกก่อน

### Top-5

เหมือน Top-3 แต่ผ่อนขึ้น ใช้กับ attack order ที่ส่งให้ Kali/opencode

### MRR

Mean Reciprocal Rank คือคะแนนเฉลี่ยจากอันดับของคำตอบที่ถูก

ตัวอย่าง:

- ถูกอันดับ 1 ได้ `1/1 = 1.0`
- ถูกอันดับ 2 ได้ `1/2 = 0.5`
- ถูกอันดับ 4 ได้ `1/4 = 0.25`

ยิ่งสูงยิ่งดี

### Mean attempts

จำนวนครั้งเฉลี่ยที่ต้องลอง candidate family จนกว่าจะเจอ family ที่ถูก

ยิ่งต่ำยิ่งดี

## ผลล่าสุด

โหมด merged 29 targets:

- Top-1: `0.931`
- Top-3: `0.966`
- Top-5: `1.000`
- MRR: `0.955`
- mean attempts: `1.172`
- failure case เกิน Top-3: `1`

Scanner heuristic ในโหมด merged:

- Top-1: `0.931`
- Top-3: `1.000`
- Top-5: `1.000`
- mean attempts: `1.103`

โหมด validated-only 8 targets:

- Top-1: `1.000`
- Top-3: `1.000`
- Top-5: `1.000`
- MRR: `1.000`
- mean attempts: `1.000`

Random baseline:

- Top-1: `0.037`
- Top-3: `0.111`
- mean attempts: `14.000`

แปลว่า feature จาก scanner/evidence ช่วยจัดอันดับได้ดีกว่าสุ่มมาก และหลังเพิ่ม Kali validation evidence แล้ว target ที่เคยพลาด เช่น Shiro/GoAhead ขยับเข้าอันดับต้นได้

failure ล่าสุดของ ML logistic คือ `appweb_CVE-2018-8715` ซึ่งยังมี evidence เฉพาะ AppWeb ไม่พอ ทำให้โมเดลที่เรียนจาก evidence GoAhead รอบใหม่ดัน `goahead` ขึ้นก่อนในบาง fold จุดนี้ควรสแกน AppWeb เพิ่มเพื่อหา fingerprint เฉพาะ เช่น AppWeb banner/header/error page

## Label mode คืออะไร

### weak

ใช้ label จากชื่อ lab/folder เช่น `shiro_CVE-2016-4437` บอกว่า positive family คือ `shiro`

ข้อดี:

- มีครบทุก target
- ใช้ bootstrap โมเดลได้เร็ว

ข้อเสีย:

- ยังไม่ใช่ exploit-success ground truth

### validated

ใช้เฉพาะ target ที่ Kali/opencode ยืนยันด้วย evidence แล้ว เช่น `rememberMe=deleteMe` สำหรับ Shiro

ข้อดี:

- น่าเชื่อถือกว่า weak label

ข้อเสีย:

- ตอนนี้มีน้อยกว่า weak label

### merged

ใช้ validated label ก่อน ถ้า target ไหนยังไม่มี validated label ค่อย fallback เป็น weak label

นี่คือโหมดหลักตอนนี้ เพราะได้ทั้งความน่าเชื่อถือจาก validation และยังวัดภาพรวมครบ 29 targets

## Feature ที่ใช้จริงในโมเดล

โมเดลไม่ได้เอา raw text ตรง ๆ ทั้งก้อนเข้า logistic regression แต่แปลงเป็นคะแนน numeric ต่อ candidate family:

```text
title_alias_score
server_alias_score
nmap_alias_score
body_alias_score
evidence_alias_score
port_score
protocol_score
http_tool_score
scan_depth_score
```

ไฟล์ feature ทั้งหมด:

```text
experiments/dec-ml-scan-2026-08-25/feature-inventory.csv
experiments/dec-ml-scan-2026-08-25/features-enriched.csv
experiments/dec-ml-scan-2026-08-25/derived/candidate-family-features-merged.csv
```

## สิ่งที่ห้ามใช้เป็น feature

ห้ามใช้:

- `target_id`
- `candidate_family` เดิมจาก features.csv
- `positive_family`
- CVE จากชื่อ target
- path ที่มีชื่อ target/CVE

เพราะข้อมูลพวกนี้ทำให้โมเดลโกงได้ เช่นเห็นชื่อ `shiro_CVE-2016-4437` แล้วตอบ `shiro` โดยไม่ได้อ่าน scanner evidence จริง

## ข้อสรุป

ตอนนี้ pipeline ใช้ได้เป็นรูปเป็นร่างแล้ว:

1. opencode/Kali ทำ scan และ validation
2. Codex ingest raw-curated + labels
3. enrich scanner evidence เป็น feature
4. evaluate ranking
5. export attack order รอบถัดไป

จุดที่ยังควรทำต่อคือเพิ่ม validated evidence ให้ target ที่ยังไม่ชัด โดยเฉพาะ Spring และเพิ่ม Metasploit safe check ใน local lab เพื่อให้ label แข็งแรงขึ้น
