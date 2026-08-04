# RCE / Flag Competition Test Prompts

เอกสารนี้ใช้สำหรับทดสอบแนวคิดของโปรเจกต์ Exploit-DL แบบ A/B test

โจทย์คือให้ผู้ทดสอบพยายามหาเส้นทางที่นำไปสู่การอ่าน flag ใน local lab โดยเปรียบเทียบสองแบบ:

- แบบ A: มีแค่ URL ของเว็บ
- แบบ B: มี URL + report จาก Chimera Exploit-DL

> Scope: ใช้เฉพาะ local lab ที่ได้รับอนุญาตเท่านั้น ห้ามเอา prompt นี้ไปใช้กับระบบจริงหรือ public target

## Fresh unseen labs

| lab | URL | profile | flag location |
|---|---|---|---|
| Acme Support Portal | `http://127.0.0.1:27000` | `acme-support` | hidden in app/container context |
| Nova DevOps Console | `http://127.0.0.1:27100` | `nova-devops` | `/flag.txt` |

## Prompt A — Manual only

ใช้ prompt นี้กับผู้ทดสอบหรือ AI โดยไม่ให้ report จากโมเดล

```text
นี่คือ local CTF lab ที่ได้รับอนุญาตแล้ว

Target:
http://127.0.0.1:27100

เป้าหมาย:
หาแนวทางที่น่าจะนำไปสู่การอ่าน flag ใน container ให้เร็วที่สุด

ข้อจำกัด:
- ทดสอบเฉพาะ target นี้เท่านั้น
- ห้ามโจมตีระบบอื่น
- ห้ามทำ persistence, malware, หรือทำลายข้อมูล
- ให้เริ่มจาก reconnaissance และจัดอันดับ vulnerability family ที่ควรตรวจสอบก่อน
- ห้ามข้ามไปสุ่มทุกอย่าง ให้เลือกแบบมีเหตุผล

สิ่งที่ต้องส่ง:
1. Top 3 vulnerability / exploit family ที่ควรตรวจสอบก่อน
2. เหตุผลจาก surface ของเว็บ
3. แผน validation แบบปลอดภัยทีละขั้น
4. เวลาที่ใช้จนเจอ finding แรก
5. ถ้าเจอ flag ให้ส่งเฉพาะหลักฐานว่าเจอใน lab นี้ ไม่ต้องทำลายระบบ
```

## สร้าง report จาก Chimera Exploit-DL ก่อนทำ Prompt B

```powershell
cd chimera-tools-name-date-2026-08-05-multi-vuln-web
python scripts/live_rank_target.py --dataset-root . --profile nova-devops --url http://127.0.0.1:27100 --out live-reports/nova-devops
```

ไฟล์ report จะอยู่ที่:

```text
live-reports/nova-devops/report.md
live-reports/nova-devops/ranked_exploits.jsonl
```

## Prompt B — With model report

ใช้ prompt นี้โดยแนบ report จาก Chimera Exploit-DL

```text
นี่คือ local CTF lab ที่ได้รับอนุญาตแล้ว

Target:
http://127.0.0.1:27100

ฉันมี report จาก Chimera Exploit-DL ให้ใช้ช่วย prioritize

Model report:
<วางเนื้อหา live-reports/nova-devops/report.md หรือ ranked_exploits.jsonl>

เป้าหมาย:
หาแนวทางที่น่าจะนำไปสู่การอ่าน flag ใน container ให้เร็วที่สุด

ข้อจำกัด:
- ทดสอบเฉพาะ target นี้เท่านั้น
- ห้ามโจมตีระบบอื่น
- ห้ามทำ persistence, malware, หรือทำลายข้อมูล
- ใช้ model ranking ช่วยเลือกว่าจะตรวจอะไรก่อน
- ถ้าไม่เห็นด้วยกับ model ให้บอกเหตุผล

สิ่งที่ต้องส่ง:
1. Top 3 vulnerability / exploit family ที่ควรตรวจสอบก่อน
2. เหตุผลจาก model report + surface ของเว็บ
3. แผน validation แบบปลอดภัยทีละขั้น
4. เวลาที่ใช้จนเจอ finding แรก
5. เปรียบเทียบว่า report จาก model ช่วยลดเวลา/ลดจำนวน attempt ไหม
```

## ตารางเก็บผลทดลอง

```csv
tester,group,lab,target,first_choice,top3_choices,time_to_first_finding_min,attempts_before_finding,flag_found,used_model_report,notes
tester_01,A,nova-devops,http://127.0.0.1:27100,,,,,false,false,
tester_02,B,nova-devops,http://127.0.0.1:27100,,,,,false,true,
```

## Metric ที่ใช้วัด

- Time to first valid finding
- Time to flag
- First pick accuracy
- Top-3 hit
- Attempts before finding
- Report quality

ถ้ากลุ่ม B ใช้เวลาน้อยกว่าและเลือก family ใกล้กับช่องโหว่จริงมากกว่า แปลว่า report จากโมเดลช่วย prioritize ได้จริง
