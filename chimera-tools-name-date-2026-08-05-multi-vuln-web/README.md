# Chimera Multi-Vulnerability Web Dataset (2026-08-05)

ชุดนี้ทำมาเพื่อโปรเจกต์ **Exploit-DL: ระบบเลือก Exploit อัตโนมัติ** โดยเฉพาะ

ต่างจากชุด Vulhub CVE เดี่ยว ๆ ชุดนี้ใช้เว็บที่มีช่องโหว่หลายแบบในเว็บเดียว เพื่อจำลองโจทย์จริงว่า:

> เมื่อเจอ target หนึ่งเว็บ เราควรลอง exploit family ไหนก่อน เพื่อให้มีโอกาสสำเร็จสูงที่สุด

## Lab ที่ใช้

- OWASP Juice Shop
- OWASP WebGoat
- DVWA
- bWAPP
- OWASP Mutillidae / NOWASP

## Tools ที่ใช้สแกน

- `nmap` สำหรับ service/version fingerprint
- `httpx` สำหรับ web title, tech, status code
- `nuclei` สำหรับ vulnerability/template signal
- `nikto` สำหรับ web finding
- `wapiti` สำหรับ DAST finding
- `zap` สำหรับ DAST finding และ risk signal

## ไฟล์สำคัญ

```text
records/
  exploit-dl-target-features.jsonl    # feature ต่อ target
  exploit-rank-candidates.jsonl       # candidate exploit ranking
  all-records.jsonl                   # record รวมทั้งหมด

derived/
  training_examples.csv               # ตาราง train หลัก
  training_examples.jsonl
  feature_matrix.csv                  # one-hot encoded matrix
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

## วิธีรัน Step 2: Fingerprint → Feature

ติดตั้ง dependency:

```bash
pip install -r requirements.txt
```

สร้าง feature table:

```bash
python scripts/build_features.py --dataset-root .
```

ผลลัพธ์หลัก:

- `derived/training_examples.csv`
- `derived/feature_matrix.csv`
- `derived/feature_summary.json`

แนวคิดคือเอาข้อมูลจาก scanner เช่น port, service, title, tech, ZAP finding count, exploit family แล้วแปลงเป็นตัวเลข/ตารางที่โมเดลเรียนได้

## วิธีรัน Step 3: ML Decision Engine

Train baseline model:

```bash
python scripts/train_baseline.py --dataset-root .
```

ลอง predict target หนึ่งตัว:

```bash
python scripts/predict_example.py --dataset-root . --lab-id dvwa
```

ตัวอย่างผลลัพธ์ที่ควรเห็น:

```text
dvwa  command-injection  0.992
dvwa  sqli               0.988
dvwa  xss                0.084
```

แปลว่าโมเดลมองว่า DVWA ควรลอง `command-injection` หรือ `sqli` ก่อน

## Label ที่ใช้ตอนนี้

ตอนนี้ label คือ:

- `is_recommended`
- `rank`
- `rank_score`

label นี้มาจาก heuristic:

```text
known vulnerable app prior
+ scanner evidence
+ exploit family risk weight
```

พูดตรง ๆ คือยังไม่ใช่ “ยิง exploit สำเร็จจริง” แต่เป็น weak label สำหรับทำ prototype ให้ระบบเรียนรู้ pipeline ได้ก่อน

## ทำไมต้องเริ่มแบบนี้

เพราะตอนนี้เรายังไม่มี feedback loop ที่ยิง exploit ทุกตัวแล้วบันทึกผลสำเร็จ/ล้มเหลวจริง การใช้ weak label ทำให้เราทดสอบระบบได้ครบก่อน:

```text
scan → normalize → feature → train → predict ranking
```

พอ pipeline นี้นิ่งแล้ว ค่อยเพิ่ม exploit validation เพื่อเปลี่ยน label ให้เป็นของจริง

## ขั้นต่อไปที่ควรทำ

1. เพิ่ม exploit validation ใน local lab เท่านั้น
2. บันทึกผล `exploit_success_observed = true/false`
3. เพิ่ม negative samples เช่น เว็บปกติหรือ version ที่ไม่ vulnerable
4. เพิ่มจำนวน target เป็น 30–100 ตัว
5. เปลี่ยน baseline จาก RandomForest ไปเป็น ranking model เช่น LightGBM Ranker
6. ถ้าข้อมูลเยอะพอ ค่อยใช้ Deep Learning + text embeddings จาก banner/report

## ข้อควรระวัง

อย่า train ด้วย field ที่ทำให้โมเดลโกง เช่น:

- `lab_id`
- Docker image name
- local path
- timestamp
- generated host port

เพราะโมเดลจะจำชื่อ lab แทนที่จะเรียนรู้ fingerprint จริง
