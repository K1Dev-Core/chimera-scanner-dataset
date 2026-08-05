# สรุปสำหรับทำสไลด์ — Chimera / Exploit-DL

## 1. ปัญหาที่โปรเจกต์แก้

ในการทดสอบช่องโหว่หรือ CTF เป้าหมายหนึ่งตัวอาจมีหลายช่องทางให้ตรวจ เช่น login, upload, API, admin panel, service version หรือ CVE เก่า ๆ ปัญหาคือผู้ทดสอบมักต้องลองหลายแนวโดยไม่มีลำดับความสำคัญ ทำให้เสียเวลาและอาจเริ่มผิดจุด

โปรเจกต์นี้จึงพยายามตอบคำถามว่า:

> จาก fingerprint ของเป้าหมายนี้ ควรตรวจ vulnerability/exploit family ไหนก่อน เพื่อมีโอกาสเจอผลลัพธ์เร็วที่สุด

## 2. แนวคิดของระบบ

Chimera / Exploit-DL ใช้ pipeline แบบนี้:

```text
Target / Docker Lab / Vulhub
        ↓
Scanner + Passive Fingerprint
        ↓
Raw Data / Metadata
        ↓
Normalize
        ↓
Feature Engineering
        ↓
Baseline Model
        ↓
Ranked Vulnerability Family Report
```

ระบบไม่ได้ยิง exploit แทนผู้ใช้ แต่ช่วยจัดอันดับว่า “ควรเริ่มตรวจอะไร” จากข้อมูลที่เห็น

## 3. Dataset ที่มีตอนนี้

| Dataset | Rows | Features/Columns | ใช้ทำอะไร |
|---|---:|---:|---|
| Multi-vuln web prototype | 43 | 54 feature columns | train baseline model และทดสอบ live ranking |
| Vulhub expanded metadata | 264 | 84 feature columns | เพิ่ม lab/CVE seed เพื่อขยายข้อมูล |
| Vulhub redo feature JSONL | 8+ labs | JSONL records | ชุดเริ่มต้นจาก lab vulnerable web |

## 4. แหล่งข้อมูล

ข้อมูลมาจาก 4 แหล่งหลัก:

1. Vulhub CVE Labs  
   ใช้ข้อมูล product, CVE, docker image, exposed port, lab directory และ vulnerability family

2. Custom Vulnerable Labs  
   เช่น Acme Support Portal, Nova DevOps Console ที่สร้างเองเพื่อจำลองเว็บใช้งานจริง

3. Scanner / Passive Fingerprint  
   เช่น ZAP, Nuclei, Wapiti, Nikto, HTTP title, server header, form/input name

4. Weak Label / Heuristic Mapping  
   สร้าง label เบื้องต้นจาก CVE metadata, scanner evidence, lab prior และ risk score

## 5. Feature ที่ใช้

ตัวอย่าง feature:

```text
port / exposed_port_count
has_http_port_hint
product_grafana
product_wordpress
service_apache_httpd
service_werkzeug
has_zap_evidence
has_nuclei_evidence
zap_finding_count
observed_tech_count
candidate_exploit_family_sqli
candidate_exploit_family_auth_bypass
```

แนวคิดคือแปลงข้อมูลที่มนุษย์อ่านได้ เช่น `Grafana`, `Werkzeug`, `login form`, `CVE-2024-9264` ให้กลายเป็นตัวเลข 0/1 หรือ count เพื่อให้โมเดลเรียนรู้ได้

## 6. Label ที่มีตอนนี้

Label ปัจจุบัน:

```text
is_recommended
is_top1
is_known_family
```

ความหมาย:

- `is_recommended` = candidate นี้ควรถูกแนะนำหรือไม่
- `is_top1` = candidate นี้เป็นอันดับ 1 หรือไม่
- `is_known_family` = candidate ตรงกับ family ที่รู้จาก CVE/lab metadata หรือไม่

Label ที่ควรเพิ่มต่อ:

```text
exploit_success_observed
```

อันนี้คือ label สำคัญที่สุดสำหรับ Exploit-DL เพราะจะบอกว่า exploit/family ที่เลือก “สำเร็จจริงหรือไม่”

## 7. Model ปัจจุบัน

ตอนนี้ใช้ Random Forest เป็น baseline ก่อน

เหตุผล:

- train ได้เร็ว
- อธิบายง่าย
- ใช้เทียบกับ Deep Learning ในอนาคตได้
- เหมาะกับ dataset ที่ยังไม่ใหญ่มาก

ผล baseline ที่เคยได้จาก prototype:

```text
Accuracy: 0.9767
ROC-AUC: 0.9939
Top-1/Top-3 hit by target: 1.0
```

ข้อควรอธิบาย:

> Metric นี้เป็น proof-of-concept จาก weak label ยังไม่ใช่ผลวัด exploit success จริงทั้งหมด

## 8. จุดที่น่าสนใจของงานตอนนี้

- มี pipeline ตั้งแต่ lab → data → feature → model → report
- Dataset เริ่มมีหลาย vulnerability family ไม่ใช่แค่ SQLi อย่างเดียว
- มีทั้ง public lab และ lab ที่สร้างเอง
- เริ่มออกแบบ A/B test เพื่อวัดว่า report จาก model ช่วยลดเวลาทดสอบจริงหรือไม่
- เห็น limitation ของ model แล้ว เช่น bias ตามข้อมูลฝึก จึงมีแผนเพิ่ม exploit feedback label

## 9. แผนต่อไป

1. รัน lab เพิ่มและเก็บ scanner output จริงให้มากขึ้น
2. เพิ่ม label แบบ `exploit_success_observed = 1/0`
3. ขยาย feature จาก HTTP/form/service/CVE ให้ละเอียดขึ้น
4. train baseline หลายโมเดล เช่น Random Forest, XGBoost, Neural Network
5. ทำ A/B test ระหว่าง manual-only กับ model-assisted
6. สรุปว่า model ช่วยลดเวลาและเพิ่มความแม่นในการเลือก exploit family ได้จริงไหม

