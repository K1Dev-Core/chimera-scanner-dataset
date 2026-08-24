# Chimera / Exploit-DL Demo Pack — Feature, Label, Model, Report

โฟลเดอร์นี้คือชุด demo สำหรับอัปเดตความคืบหน้าโปรเจกต์รอบนี้ โดยรวมข้อมูลสำคัญที่ใช้เล่าว่า:

```text
Target → Fingerprint → Dataset → Feature → Label → Model → Ranking Report
```

## เปิดไฟล์ไหนก่อน

1. `PRESENTATION_UPDATE_TH.md`  
   สรุปสำหรับนำเสนอความคืบหน้า

2. `PIPELINE_CODE_REFERENCE_TH.md`  
   อธิบายว่าแต่ละขั้นใช้ไฟล์โค้ดส่วนไหนทำงาน

3. `MODEL_RUNBOOK_TH.md`  
   คำสั่งรัน build feature, train model, predict และออก report

4. `data/passive_targets.csv`  
   target ที่ fingerprint ล่าสุด รวม picoCTF 2 ตัว

5. `data/ranked_family_examples.csv`  
   ranking report ตัวอย่างจาก target ใหม่และ target ก่อนหน้า

6. `data/feature_label_snapshot.csv`  
   snapshot ว่า feature/label ตอนนี้มีอะไรและมาจากไหน

7. `reports/`  
   report ที่เอาไปแปะ Prompt B หรือแคปลงสไลด์ได้

## Target ใหม่ที่เพิ่มในรอบนี้

```text
http://lonely-island.picoctf.net:49776/
```

Fingerprint ที่ได้:

```text
title: Login - picoCTF demo
server: Apache/2.4.66 (Debian)
form_count: 1
input_names: password, username, viewport
links: /register.php, /assets/css/styles.css
```

Ranking:

```text
1. auth-bypass — 0.78
2. sqli — 0.68
3. broken-access-control — 0.62
4. xss — 0.48
5. sensitive-data-exposure — 0.35
6. csrf — 0.28
```

## สถานะ dataset/model ตอนนี้

| ส่วน | สถานะ |
|---|---|
| Prototype training rows | 43 rows |
| Prototype feature matrix | 54 feature columns |
| Expanded Vulhub metadata | 66 labs / 264 rows / 84 feature columns |
| Baseline model | Random Forest |
| Main label | `is_recommended` |
| Ranking label | `rank`, `is_top1` |
| Label limitation | ยังเป็น weak/heuristic label |
| Label ที่ควรเพิ่ม | `exploit_success_observed = 1/0` |

## หมายเหตุด้านขอบเขต

เคส picoCTF ในรอบนี้ใช้ passive fingerprint และ weak-prior ranking เท่านั้น ไม่ใช่การยืนยัน exploit และไม่ใช่ payload guide

