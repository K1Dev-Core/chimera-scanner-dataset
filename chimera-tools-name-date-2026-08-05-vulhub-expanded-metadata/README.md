# Chimera Vulhub Expanded Metadata Dataset

ชุดนี้เป็น dataset เพิ่มสำหรับโปรเจกต์ **Exploit-DL: ระบบเลือก Exploit อัตโนมัติด้วย Deep Learning**

เป้าหมายของชุดนี้คือเพิ่มจำนวน lab/CVE/product ให้เยอะขึ้นก่อน เพื่อเอาไปทำขั้น:

```text
Fingerprint → Feature → Label Candidate → Ranking Model
```

## สถานะของชุดนี้

รอบนี้ **ยังไม่ใช่ live scan batch** เพราะตอนทำงาน Docker Desktop daemon บนเครื่อง start ไม่สำเร็จ และคืนค่า:

```text
Docker Desktop is unable to start
```

ดังนั้น dataset ชุดนี้เป็น:

- metadata จาก Vulhub local source
- feature seed สำหรับ Step 2
- weak label สำหรับ Step 3
- candidate ranking rows สำหรับลอง train baseline

ยังไม่ใช่:

- ผล exploit จริง
- proof ว่าโจมตีสำเร็จ
- label แบบ `exploit_success_observed=true/false`

## จำนวนข้อมูล

ดูสรุปเต็มได้ที่:

```text
manifests/index.json
```

สรุปหลัก:

```text
labs: 66
feature_seed_rows: 66
label_candidate_rows: 66
rank_candidate_rows: 264
derived_training_rows: 264
derived_feature_columns: 84
all_records: 462
```

## ไฟล์สำคัญ

```text
records/vulhub-lab-metadata.jsonl
```

metadata ของแต่ละ lab เช่น product, CVE, Docker image, exposed port

```text
records/exploit-dl-feature-seeds.jsonl
```

feature seed สำหรับเอาไปต่อยอดเป็น feature vector เช่น product, CVE year, port count, image count

```text
records/exploit-label-candidates.jsonl
```

label candidate แบบ weak label เช่น lab นี้น่าจะเป็น SQLi/RCE/auth-bypass family

```text
records/exploit-rank-candidates.jsonl
```

candidate exploit family หลายอันดับต่อ 1 lab ใช้สำหรับฝึก ranking baseline

```text
derived/training_examples.csv
```

ตารางพร้อมเอาไปลอง train model แบบเร็ว

```text
derived/feature_matrix.csv
```

feature matrix เบื้องต้นแบบ numeric/one-hot สำหรับ Step 2

## ทำไมชุดนี้มีประโยชน์

ชุด live scan เดิมของเราดีสำหรับ demo pipeline แต่จำนวน target ยังน้อยเกินไป ถ้าเอาไป train model เลย โมเดลจะจำ pattern แคบ ๆ เช่น `DVWA = command injection`, `Juice Shop = XSS/SQLi` มากเกินไป

ชุดนี้ช่วยเพิ่ม diversity:

- product จริงมากขึ้น
- CVE หลายปี
- vulnerability family หลายแบบ
- web app และ service app ปนกัน
- มีทั้ง SQLi, auth-bypass, command-injection, deserialization, file-upload, file-inclusion

## ข้อจำกัด

ข้อจำกัดสำคัญที่สุด:

```text
exploit_success_observed = null
```

แปลว่า label ตอนนี้ยังเป็น `weak label` ไม่ใช่ผลจากการลอง exploit แล้วสำเร็จ/ล้มเหลวจริง

ใช้ได้สำหรับ:

- baseline
- feature engineering
- ranking demo
- data preparation

ยังไม่ควรใช้ claim ว่าโมเดลโจมตีแม่นจริง

## ขั้นต่อไปที่ควรทำ

1. ทำให้ Docker Desktop กลับมารันได้
2. เลือก 10–20 lab จากชุดนี้มารันจริงก่อน
3. เก็บ scanner output จาก `naabu`, `nmap`, `httpx`, `nuclei`, `nikto`, `wapiti`, `ZAP`
4. merge scanner output เข้ากับ metadata ชุดนี้
5. แปลงเป็น feature vector
6. train baseline model ใหม่
7. ทำ validation loop ใน local lab เพื่อเก็บ `success/fail`

## สรุปสั้น

ชุดนี้ทำให้เรามีข้อมูลเยอะขึ้นพอสำหรับเริ่ม Step 2/3 แบบจริงจัง แต่ถ้าจะให้ Exploit-DL เก่งแบบ “เลือก exploit ที่มีโอกาสสำเร็จสูงสุด” ต้องเพิ่ม live scan และ label จริงต่อ
