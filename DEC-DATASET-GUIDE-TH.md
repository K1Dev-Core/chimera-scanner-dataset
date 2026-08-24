# คู่มืออ่าน Dataset branch Dec

เอกสารนี้เขียนไว้ให้เปิด repo แล้วเข้าใจภาพรวมเร็วขึ้น ว่าไฟล์ไหนคือชุดหลัก ไฟล์ไหนเป็น raw evidence และไฟล์ไหนเป็นข้อมูลทดลองจาก branch `Hex`

## สรุปง่าย ๆ

ตอนนี้ของที่ควรถือเป็นแกนหลักคือ:

`generated/dec-vulhub-2026-08-24-fixed-core/`

ชุดนี้มี 43 targets และเป็น normalized/fixed core ล่าสุดของ `Dec`

ส่วน `dataset/raw-curated/` คือ raw scanner output ที่คัดแล้ว เอาไว้ตรวจหลักฐานหรือ parse feature เพิ่ม

ส่วนโฟลเดอร์ที่ขึ้นต้นด้วย `chimera-tools-name-date-2026-08-05-*` คือข้อมูลที่ import จาก branch `Hex` เพื่อช่วยเลือก target เพิ่มและทำ feature seed แต่ยังไม่ควรถือเป็น ground truth เต็มตัว

## โครงสร้างที่ควรรู้

| path | คืออะไร | ควรใช้เมื่อ |
| --- | --- | --- |
| `generated/dec-vulhub-2026-08-24-fixed-core/` | normalized dataset หลัก 43 targets | ใช้ทำ analysis, feature engineering, demo, baseline ML |
| `dataset/raw-curated/dec-vulhub-2026-08-24/` | raw scan output จากชุดแรก 10 targets | ใช้ตรวจหลักฐาน scanner output จริง |
| `dataset/raw-curated/hex-exp-2026-08-05/` | raw scan/manual PoC จากชุดทดลอง 12 targets | ใช้เพิ่ม scanner coverage และ manual evidence |
| `chimera-tools-name-date-2026-08-05-vulhub-cve-bulk/` | metadata จาก Vulhub 160 labs | ใช้เลือก target เพิ่ม และทำ feature seed |
| `chimera-tools-name-date-2026-08-05-vulhub-redo/` | active scan seed 8 labs จาก Hex | ใช้ดูตัวอย่าง feature จาก scanner suite |
| `chimera-tools-name-date-2026-08-05-multi-vuln-web/` | dataset ทดลองหลาย vulnerability family | ใช้ทำ demo ranking exploit/family |
| `demo-feature-label-model-2026-08-05/` | ชุด demo model/feature-label เล็ก ๆ | ใช้อธิบาย pipeline และ presentation |
| `HEX-BRANCH-PROGRESS-2026-08-05.md` | สรุปว่า branch Hex ทำอะไรไปแล้ว | ใช้อ่านความคืบหน้าฝั่ง Hex |

## ชุดหลัก 43 targets

ไฟล์หลัก:

- `records/targets.jsonl` รายชื่อ target ทั้งหมด
- `records/observations.jsonl` ข้อมูลทั่วไปที่ scanner เห็น
- `records/findings.jsonl` finding ที่ scanner รายงาน
- `records/validations.jsonl` validation/label/proof ที่มี
- `records/tool_runs.jsonl` สถานะการรัน tool
- `records/all-records.jsonl` รวม records ทุกชนิด
- `derived/target-features.json` feature ระดับ target
- `derived/target-candidate-features.json` feature ระดับ target + candidate family
- `labels/target-candidate-labels.jsonl` weak label สำหรับ candidate family
- `manifest.json` จำนวน records และ metadata ของชุดนี้
- `quality-report.json` รายงานตรวจคุณภาพ

ตัวเลขล่าสุดจาก manifest:

| record | count |
| --- | ---: |
| targets | 43 |
| observations | 704 |
| findings | 2046 |
| validations | 92 |
| tool_runs | 381 |
| candidate_rows | 602 |
| all_records | 3266 |

Tools ที่มีใน normalized core:

`gobuster`, `httpx-toolkit`, `manual_poc`, `metasploit`, `naabu`, `nikto`, `nmap`, `nuclei`, `sqlmap`, `wapiti`, `zaproxy`

## ความหมายของ records

### target

หนึ่ง target คือหนึ่ง lab/service ที่เราสแกน เช่น:

- `drupal_7600`
- `jenkins_1000861`
- `tomcat_12615`
- `weblogic_14882`

ใช้สำหรับรู้ว่า dataset มี lab อะไรบ้าง และ expected vulnerability คืออะไร

### observation

observation คือข้อมูลทั่วไปที่ scanner เจอ ยังไม่จำเป็นต้องเป็นช่องโหว่ เช่น:

- port เปิด
- HTTP status code
- page title
- server header
- technology fingerprint
- service/version

เหมาะสำหรับทำ feature แบบปลอดภัยกว่า finding เช่น `open_port_count`, `has_http_service`, `technology_count`

### finding

finding คือสิ่งที่ scanner รายงานว่าอาจเป็นช่องโหว่หรือความเสี่ยง เช่น:

- nuclei template match
- nikto finding
- zap alert
- wapiti vulnerability

finding มีประโยชน์มากสำหรับ demo และ triage แต่ต้องระวัง leakage ถ้าเอาไป train model เพราะบาง finding อาจเฉลย CVE หรือ vulnerability family โดยตรง

### validation

validation คือข้อมูลที่ช่วยบอกว่า target นี้ตรง expected vulnerability หรือมี proof บางอย่างหรือไม่

สำคัญ: label หลายตัวเป็น weak label จาก Vulhub/lab identity ไม่ใช่ exploit success จริงทั้งหมด

## Raw curated คืออะไร

raw curated คือ output ดิบที่คัดมาแล้วว่าเป็นผล scan จริง เก็บไว้เพื่อ:

- ตรวจหลักฐานย้อนหลัง
- parse feature ใหม่
- debug ว่าทำไม normalized record ออกมาแบบนั้น
- ใช้ประกอบ demo ว่า scanner แต่ละตัวเห็นอะไร

### ชุด `dec-vulhub-2026-08-24`

อยู่ที่:

`dataset/raw-curated/dec-vulhub-2026-08-24/`

มี 85 scanner files จาก 10 targets:

- httpx-toolkit
- metasploit
- naabu
- nikto
- nmap
- nuclei
- sqlmap
- wapiti
- zaproxy

### ชุด `hex-exp-2026-08-05`

อยู่ที่:

`dataset/raw-curated/hex-exp-2026-08-05/`

มี 264 files จาก 12 experimental targets:

- `drupal_7600`
- `drupal_7602`
- `weblogic_14882`
- `weblogic_10271`
- `jenkins_1000861`
- `joomla_8562`
- `phpmyadmin_12613`
- `solr_0193`
- `solr_17558`
- `thinkphp_5rce`
- `flask_ssti`
- `shiro_4437`

ไฟล์ในชุดนี้ถูกย่อชื่อเป็น `scan-001.*`, `scan-002.*` เพื่อลดปัญหา path ยาวบน Windows

## ของจาก branch Hex คืออะไร

`Hex` มีข้อมูลทดลองเยอะมาก แต่เราไม่ได้ merge ทั้ง branch เพราะ:

- มี path ยาวมาก
- มีการลบไฟล์ของ Dec หลายส่วน
- มีทั้ง metadata, demo, fresh lab, slide material ปนกัน
- บางส่วนเป็น weak label ไม่ใช่ exploit validation

สิ่งที่ import มาใน `Dec` คือเฉพาะข้อมูลที่ใช้ต่อได้ง่าย:

| ชุด | ใช้ทำอะไร |
| --- | --- |
| `vulhub-cve-bulk` | รายชื่อ lab จำนวนมาก ใช้เลือก target เพิ่ม |
| `vulhub-expanded-metadata` | metadata เพิ่มสำหรับ feature seed |
| `vulhub-redo` | ตัวอย่าง active scan 8 labs |
| `active-scanner-suite` | สรุป scanner suite และ feature เล็ก ๆ |
| `multi-vuln-web` | ทดลอง ranking หลาย vulnerability family |
| `demo-feature-label-model` | ชุดอธิบาย model/demo |

## Feature ที่ควรเริ่มทำ

ควรเริ่มจาก feature ที่ไม่เฉลย label ตรง ๆ:

| feature | มาจาก | เหตุผล |
| --- | --- | --- |
| `open_port_count` | nmap/naabu observations | บอก attack surface |
| `has_http_service` | nmap/httpx/nikto/zap/wapiti | target ส่วนใหญ่เป็น web/service |
| `http_status_code` | httpx/zap/wapiti | บอกว่า target reachable หรือไม่ |
| `detected_technology_count` | httpx/nuclei/nikto/zap | ช่วยจับ tech stack |
| `scanner_coverage_count` | tool_runs/raw-curated | บอกว่ามีหลักฐานจากกี่ tool |
| `finding_count_by_tool` | findings | ใช้ ranking/triage ได้ดี |
| `severity_counts` | findings | ใช้ทำ risk score/demo |

## Feature ที่ไม่ควรใช้เป็น input ตอน train

สิ่งเหล่านี้เสี่ยงทำให้ model จำคำตอบแทนที่จะเรียนรู้:

- `target_id` เช่น `drupal_7600`
- CVE ตรง ๆ เช่น `CVE-2018-7600`
- path ที่มีชื่อ lab/CVE
- title/finding ที่มี CVE ตรงกับ label
- expected vulnerability field
- exact Docker host port ถ้ามันผูกกับ lab มากเกินไป

ใช้ได้ถ้าเป็นงาน retrieval, traceability, หรือ dashboard แต่ไม่ควรใช้เป็น feature สำหรับวัด model prediction จริง

## Workflow แนะนำต่อจากนี้

1. ใช้ `generated/dec-vulhub-2026-08-24-fixed-core/` เป็น source หลัก
2. ใช้ `raw-curated` ตรวจ evidence หรือ parse feature เพิ่ม
3. ใช้ `vulhub-cve-bulk/records/lab-index.jsonl` เลือก targets รอบถัดไป
4. ให้ Kali/opencode scan target ใหม่
5. ทำ raw curated รอบใหม่ โดยไม่เอา cache/runtime/dependency
6. normalize เข้า schema เดิม
7. เพิ่ม feature table ใหม่และ quality report

## สถานะที่ยังค้าง

- `dataset/raw/autorecon/**` ยังมีปัญหา path ยาวบน Windows
- ตอนนี้ปล่อย unstaged deletion ของ AutoRecon path ยาวไว้ ไม่ได้ push
- ถ้าจะใช้ AutoRecon ต้องทำ path-normalized curated pass แยก

## สรุปแบบสั้นที่สุด

ถ้าจะทำงานต่อวันนี้:

- ใช้ `generated/dec-vulhub-2026-08-24-fixed-core/` เป็น dataset หลัก
- ใช้ `dataset/raw-curated/` เป็นหลักฐานดิบ
- ใช้ `chimera-tools-name-date-2026-08-05-vulhub-cve-bulk/records/lab-index.jsonl` เพื่อเลือก target เพิ่ม
- อ่าน `HEX-BRANCH-PROGRESS-2026-08-05.md` เพื่อรู้ว่า `Hex` ทำอะไรไปแล้ว
