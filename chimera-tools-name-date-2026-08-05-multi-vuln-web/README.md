# Chimera Multi-Vulnerability Web Dataset (2026-08-05)

ชุดนี้เป็น dataset สำหรับโปรเจกต์ **Exploit-DL: ระบบช่วยเลือก exploit อัตโนมัติ** โดยเน้นโจทย์แบบ “หนึ่งเว็บมีช่องโหว่หลายแบบ” ซึ่งใกล้กับสถานการณ์ที่เราอยาก demo มากกว่า lab แบบหนึ่ง CVE ต่อหนึ่ง target

ไอเดียหลักคือ เมื่อ scanner เจอข้อมูลของ target แล้ว ระบบควรตอบได้ว่า:

> ถ้าจะลองโจมตีแบบแม่น ๆ ไม่สุ่มยิงมั่ว ควรลอง exploit family ไหนก่อน เพราะตัวไหนมีโอกาสสำเร็จสูงกว่า

ดังนั้น dataset ชุดนี้ไม่ได้เก็บแค่รายงาน scan แต่เตรียมข้อมูลไปถึงขั้น feature, candidate ranking และ baseline model ให้ทดลองได้ทันที

## Labs ที่ใช้

เลือก lab ที่เป็นเว็บฝึกโจมตีชื่อดังและมีช่องโหว่หลายกลุ่มในตัวเดียว:

- OWASP Juice Shop
- OWASP WebGoat
- DVWA
- bWAPP
- OWASP Mutillidae / NOWASP

แต่ละตัวเหมาะกับงาน ranking เพราะมี exploit family ให้เปรียบเทียบหลายแบบ เช่น `sqli`, `xss`, `command-injection`, `file-inclusion`, `auth-bypass`, `xxe`

## Tools ที่ใช้เก็บข้อมูล

- `nmap` — เก็บ service/version fingerprint
- `httpx` — เก็บ web title, status code, technology และ basic web fingerprint
- `nuclei` — เก็บ template/CVE-style signal ถ้ามี match
- `nikto` — เก็บ web finding แบบ classic web scanner
- `wapiti` — เก็บ DAST finding
- `zap` — เก็บ DAST finding และ risk signal จาก OWASP ZAP

## โครงสร้างไฟล์

```text
records/
  exploit-dl-target-features.jsonl    # feature ระดับ target
  exploit-rank-candidates.jsonl       # candidate exploit ranking
  all-records.jsonl                   # normalized record ทั้งหมด

derived/
  training_examples.csv               # ตารางหลักสำหรับ train/test
  training_examples.jsonl
  feature_matrix.csv                  # one-hot encoded feature matrix
  feature_summary.json
  baseline_predictions.csv
  baseline_metrics.json

models/
  random_forest_exploit_ranker.joblib

scripts/
  build_features.py
  train_baseline.py
  predict_example.py
```

## Step 2 — Fingerprint → Feature

รันคำสั่งนี้เพื่อแปลงข้อมูลจาก scanner ให้เป็น feature table:

```bash
pip install -r requirements.txt
python scripts/build_features.py --dataset-root .
```

ผลลัพธ์ที่ได้:

- `derived/training_examples.csv`
- `derived/training_examples.jsonl`
- `derived/feature_matrix.csv`
- `derived/feature_summary.json`

แนวคิดคือเอาข้อมูลที่ scanner มองเห็น เช่น port, service, title, tech stack, จำนวน finding จาก ZAP/Nikto/Wapiti และ exploit family ที่เป็น candidate มาแปลงเป็นตารางที่ ML ใช้ได้

ตัวอย่าง feature ที่ใช้:

- `port`
- `candidate_exploit_family`
- `rank_score`
- `family_risk_prior`
- `has_zap_evidence`
- `zap_finding_count`
- `observed_tech_count`
- `service_product_count`
- `observed_tech_text`
- `service_products_text`

ส่วนข้อความ เช่น product name, exploit family, tech stack จะถูกแปลงด้วย one-hot encoding ใน `feature_matrix.csv`

## Step 3 — ML Decision Engine

รัน baseline model:

```bash
python scripts/train_baseline.py --dataset-root .
```

ลองให้ model จัดอันดับ exploit family ของ lab หนึ่งตัว:

```bash
python scripts/predict_example.py --dataset-root . --lab-id dvwa
```

ตัวอย่าง output:

```text
lab_id  candidate_exploit_family  predicted_success_probability
dvwa    command-injection          0.992
dvwa    sqli                       0.988
dvwa    xss                        0.084
```

แปลแบบง่าย ๆ คือ สำหรับ DVWA model มองว่า `command-injection` และ `sqli` ควรถูกลองก่อนกลุ่มอื่น

## Label ที่ใช้ตอนนี้

ตอนนี้ label หลักคือ:

- `is_recommended`
- `rank`
- `rank_score`

label ชุดนี้เป็น **weak label** หรือ label สำหรับ demo ก่อน ยังไม่ใช่ผล “ยิง exploit สำเร็จจริง”

ที่มาของ label ตอนนี้คือ:

```text
known vulnerable app prior
+ scanner evidence
+ exploit family risk weight
```

พูดให้ตรงคือ dataset นี้ช่วยให้เราทดสอบ pipeline ได้ครบก่อน:

```text
scan → normalize → feature → train → predict ranking
```

แต่ถ้าจะทำเป็นงานวิจัยที่แข็งขึ้น ต้องเพิ่มขั้น exploit validation เพื่อเก็บผลจริงว่า exploit ไหนสำเร็จ/ไม่สำเร็จ

## ผล baseline รอบนี้

ดูรายละเอียดได้ที่ `derived/baseline_metrics.json`

สรุปสั้น ๆ:

- training rows: 43
- targets: 5
- feature columns: 54
- positive rows: 10
- validation: Leave-One-Target-Out
- accuracy: 0.9767
- ROC-AUC: 0.9939
- Top-1 hit rate by target: 1.0
- Top-3 hit rate by target: 1.0

ตัวเลขนี้ใช้ดูว่า pipeline ทำงานได้ ไม่ควรเอาไป claim ว่า model แม่นระดับ production เพราะ label ยังเป็น weak label และจำนวน target ยังน้อย

## ขั้นต่อไปที่ควรทำ

1. เพิ่ม exploit validation ใน local lab เท่านั้น
2. บันทึกผล `exploit_success_observed = true/false`
3. เพิ่ม negative samples เช่น target ที่ไม่ vulnerable หรือ version ที่ patch แล้ว
4. เพิ่มจำนวน target อย่างน้อย 30–100 ตัว
5. เปลี่ยน baseline จาก RandomForest ไปเป็น ranking model เช่น LightGBM Ranker
6. ถ้าข้อมูลเยอะพอ ค่อยต่อ Deep Learning + text embeddings จาก banner/report

## สิ่งที่ไม่ควรใช้เป็น feature

อย่าให้ model เรียนจากข้อมูลที่ทำให้โกง เช่น:

- `lab_id`
- Docker image name
- local file path
- timestamp
- generated host port

field พวกนี้ทำให้ผลดูแม่น แต่จริง ๆ model แค่จำชื่อ lab ไม่ได้เข้าใจ fingerprint ของ target
