# สรุปหลัง Import Kali Validation

วันที่ทำงาน: 2026-08-26

## Input

ผล scan จาก Kali:

```text
C:\Users\rapii\Desktop\kali-share\dataset\dec-validation-manual
```

ไฟล์สำคัญ:

- `validation-results.jsonl`
- `SCAN-SUMMARY-TH.md`
- `raw-curated/`

## ผล validation ที่ import

- total: 9 targets
- validated_positive: 8
- inconclusive: 1
- not_run: 0

หมายเหตุ: `SCAN-SUMMARY-TH.md` ฝั่ง Kali นับ `validated_positive` เป็น 7 แต่ `validation-results.jsonl` มี validated_positive จริง 8 แถว จึงใช้ JSONL เป็น source of truth

## Target ที่ช่วย ML ชัดเจน

- `shiro_CVE-2016-4437`: พบ `rememberMe=deleteMe` ซึ่งเป็น fingerprint ของ Shiro
- `goahead_CVE-2017-17562`: พบ `Document Error` / `Access Error` ซึ่งเป็น pattern เฉพาะของ GoAhead
- `joomla_CVE-2023-23752`: พบ `JoomlaAPI/1.0` และ public config API
- `redis_CVE-2022-0543`: พบ `redis_version:5.0.7`
- `aria2_rce`: พบ JSON-RPC version
- `grafana_CVE-2021-43798`: พบ Grafana version จาก `/api/health`
- `tomcat_CVE-2017-12615`: พบ Apache Tomcat title/docs
- `nginx_CVE-2017-7529`: พบ `Server: nginx/1.13.2`

## Target ที่ยังต้องระวัง

- `spring_CVE-2022-22965`: ยังเป็น `inconclusive` เพราะ evidence รอบนี้บอก Tomcat/JSESSIONID แต่ไม่พบ Spring-specific fingerprint เช่น actuator หรือ Whitelabel Error Page

## ผล ML หลัง import

โหมด merged 29 targets:

- Top-1: `0.931`
- Top-3: `1.000`
- Top-5: `1.000`
- mean attempts: `1.103`
- failure case เกิน Top-3: `0`

โหมด validated-only 8 targets:

- Top-1: `1.000`
- Top-3: `1.000`
- mean attempts: `1.000`

## สิ่งที่แก้ใน pipeline

- เพิ่ม ingest script สำหรับดึงทั้ง validation labels และ raw-curated evidence กลับเข้า experiment
- แก้ feature enrichment ให้อ่านไฟล์ validation evidence ที่มาจาก Kali ได้
- เพิ่ม alias จาก evidence จริงให้ Shiro และ GoAhead โดยใช้เนื้อหา evidence ไม่ใช้ชื่อ target/CVE เป็น feature
- export attack order ใหม่หลัง metrics ดีขึ้น

## งานต่อ

รอบถัดไปควรโฟกัส Spring อย่างเดียวก่อน:

- ใช้ Spring lab ที่มี actuator หรือ Spring-specific error page
- เพิ่ม nuclei/template เฉพาะ Spring fingerprint แบบ safe
- ไม่ใช้ payload ที่เขียนไฟล์หรือ destructive

## เพิ่มเติมจากรอบ tool-scope

รอบ `dec-tool-scope-2569-08-26-0058` import แล้ว แต่เป็น quick smoke run 5 targets:

- validated_positive: 4
- inconclusive: 1 (`spring_CVE-2022-22965`)
- tool ที่ใช้จริง: `naabu`, `httpx-toolkit`, `nuclei`, `nikto`, `curl`, `manual_poc`
- tool ที่ยังไม่ได้ใช้: `nmap`, `wapiti`, `zaproxy`, `metasploit`, `sqlmap`

ผล heuristic ยังดีเท่าเดิม แต่ ML logistic มี failure ใหม่ 1 ตัวคือ `appweb_CVE-2018-8715` หลัง GoAhead evidence แข็งขึ้น จุดนี้เป็นสัญญาณที่ดีต่อ workflow เพราะบอกชัดว่ารอบถัดไปต้องเพิ่ม AppWeb-specific evidence ไม่ใช่เพิ่มข้อมูลแบบหว่าน
