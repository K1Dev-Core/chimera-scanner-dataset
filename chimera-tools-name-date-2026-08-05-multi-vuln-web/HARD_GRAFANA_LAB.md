# Harder Unseen Lab: Grafana CVE-2024-9264

Lab นี้ใช้ Grafana จาก Vulhub เป็น target ที่สมจริงขึ้นกว่าเว็บฝึกทั่วไป

## Target

```text
http://127.0.0.1:27210
```

## Analyzer profile

```text
grafana-hard
```

## Run model report

```powershell
python scripts/live_rank_target.py --dataset-root . --profile grafana-hard --url http://127.0.0.1:27210 --out live-reports/grafana-hard
```

## เหตุผลที่ใช้ lab นี้

- Product จริง: Grafana
- CVE จริงปี 2024
- Surface น้อยกว่า lab ฝึกแบบ DVWA/Juice Shop
- เหมาะกับการวัดว่า model report ช่วย prioritize ได้ไหมในเคสที่ยากขึ้น

## Prompt แบบไม่มี model report

```text
นี่คือ local lab ที่ได้รับอนุญาตแล้ว

Target:
http://127.0.0.1:27210

ให้วิเคราะห์จากเว็บและ fingerprint เท่านั้น:
1. เว็บนี้น่าจะเป็น product อะไร
2. Top 3 vulnerability / exploit family ที่ควรตรวจสอบก่อนคืออะไร
3. เหตุผลคืออะไร
4. ถ้าจะ validate แบบปลอดภัยควรเก็บ evidence อะไร

ห้ามโจมตีระบบอื่น ห้ามทำ persistence ห้ามทำลายข้อมูล
```

## Prompt แบบมี model report

```text
นี่คือ local lab ที่ได้รับอนุญาตแล้ว

Target:
http://127.0.0.1:27210

Model report:
<วาง live-reports/grafana-hard/report.md>

ช่วยวิเคราะห์ว่า model ranking ช่วย prioritize ได้ไหม:
1. Top 3 ที่ model แนะนำคืออะไร
2. เห็นด้วยไหม เพราะอะไร
3. ถ้าไม่เห็นด้วย ควรปรับ feature/label อย่างไร
4. ควรเก็บ evidence อะไรเพิ่มเพื่อทำ label จริง
```
