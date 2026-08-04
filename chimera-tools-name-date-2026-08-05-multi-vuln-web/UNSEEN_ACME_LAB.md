# Unseen Lab: Acme Support Portal

ตัวนี้เป็น lab ใหม่ที่ไม่ได้อยู่ใน training dataset เดิม เหมาะสำหรับลองดูว่า baseline model จะ generalize ได้ไหม

## Target

```text
http://127.0.0.1:27000
```

## Profile สำหรับ analyzer

```text
acme-support
```

## คำสั่งรัน model วิเคราะห์ report

```powershell
python scripts/live_rank_target.py --dataset-root . --profile acme-support --url http://127.0.0.1:27000 --out live-reports/acme-support
```

ผลลัพธ์จะได้:

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
ช่วยวิเคราะห์ ranking ว่า exploit family ไหนควรลองก่อน เพราะอะไร
ให้แยกเหตุผลจาก fingerprint, model score, และข้อจำกัดของ weak-label model
สุดท้ายช่วยเสนอว่าถ้าจะทำ validation ให้ได้ label จริง ควรเก็บ field อะไรเพิ่ม

ข้อมูล:
<วางเนื้อหา live-reports/acme-support/report.md หรือ ranked_exploits.jsonl>
```

## หมายเหตุ

เว็บนี้มี vulnerability family หลายกลุ่มในระบบเดียว แต่ยังไม่ควรเอาเข้า training ทันที ให้ใช้เป็น unseen target สำหรับทดสอบก่อน
