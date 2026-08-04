# Live Demo: Fresh Unseen Lab

รอบนี้ใช้ lab ใหม่ที่ไม่ได้อยู่ใน training dataset เดิม เพื่อทดสอบว่า model พอจะ generalize ได้ไหม

## Lab ที่รันอยู่

| lab | URL | analyzer profile |
|---|---|---|
| Acme Support Portal | `http://127.0.0.1:27000` | `acme-support` |

## Start lab ใหม่

ถ้ายังไม่ได้รัน container:

```powershell
cd fresh-labs/acme-support-portal
docker build -t chimera/acme-support-portal:local .
docker run -d --name chimera-fresh-acme-support -p 127.0.0.1:27000:8080 chimera/acme-support-portal:local
```

เช็คว่า lab ยังรันอยู่:

```powershell
docker ps --format "{{.Names}} {{.Ports}}" | Select-String -Pattern "chimera-fresh-acme-support"
```

## Run model analysis

เข้าโฟลเดอร์ dataset ก่อน:

```powershell
cd chimera-tools-name-date-2026-08-05-multi-vuln-web
pip install -r requirements.txt
```

สั่งให้ model วิเคราะห์ target ใหม่:

```powershell
python scripts/live_rank_target.py --dataset-root . --profile acme-support --url http://127.0.0.1:27000 --out live-reports/acme-support
```

ผลลัพธ์:

```text
live-reports/acme-support/
  fingerprint.json
  ranked_exploits.csv
  ranked_exploits.jsonl
  report.md
```

## Prompt สำหรับให้ AI วิเคราะห์ต่อ

```text
นี่คือ report จาก Chimera Exploit-DL สำหรับ unseen target ชื่อ Acme Support Portal
ช่วยวิเคราะห์ว่า exploit family อันดับต้น ๆ คืออะไร เพราะอะไร
ให้แยกเหตุผลจาก fingerprint, model score และข้อจำกัดของ weak-label model
สุดท้ายช่วยเสนอว่าถ้าจะทำ validation ให้ได้ label จริง ควรเก็บ field อะไรเพิ่ม

ข้อมูล:
<วางเนื้อหา live-reports/acme-support/report.md หรือ ranked_exploits.jsonl>
```

## Stop lab

```powershell
docker rm -f chimera-fresh-acme-support
```
