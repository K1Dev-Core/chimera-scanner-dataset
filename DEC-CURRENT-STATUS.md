# Dec Dataset: Current Status and Session Handoff

อัปเดตล่าสุด: 2026-08-05  
สัปดาห์: 2026-W32 (3-9 สิงหาคม 2026)  
Repository: `K1Dev-Core/chimera-scanner-dataset`  
Branch: `Dec`  
ขอบเขตการทดสอบ: Vulhub และระบบที่ได้รับอนุญาตเท่านั้น

## วิธีใช้ไฟล์นี้

ไฟล์นี้เป็นสถานะกลางของงาน Dec ให้เปิดอ่านก่อนเริ่ม session ใหม่ แล้วทำต่อจากหัวข้อ `งานถัดไป` โดยตรวจข้อมูลจริงและ GitHub ก่อนทุกครั้ง ไม่ต้องเริ่มวิเคราะห์ใหม่ตั้งแต่ต้น

ข้อความสำหรับเริ่ม session ใหม่:

> อ่านไฟล์ DEC-CURRENT-STATUS.md จาก branch Dec แล้วตรวจสถานะ repository และ dataset ปัจจุบัน จากนั้นทำงานต่อจากหัวข้อ "งานถัดไป" โดยรักษา raw เดิม ห้ามสร้างข้อมูลเทียม และรายงานสิ่งที่เปลี่ยนแปลง

## เป้าหมายโครงการ

สร้าง dataset สำหรับระบบ Exploit-DL ซึ่งใช้ข้อมูล recon และผลสแกนเพื่อประเมินหรือจัดอันดับ exploit candidate ก่อนทดสอบด้วย Metasploit แล้วนำผลการรันจริงกลับมาเป็น label

หน่วยข้อมูลที่ต้องการในระยะ model-ready คือ:

```text
หนึ่งแถว = หนึ่ง target snapshot + หนึ่ง exploit candidate
```

label หลักควรมาจากผลการยืนยันจริง เช่น `session_opened`, `exploit_succeeded`, `not_vulnerable`, `not_exploitable` หรือ `unknown` ไม่ใช้การพบ CVE จาก scanner เป็น success label โดยตรง

## ความคืบหน้าสัปดาห์นี้

- ตั้ง Vulhub lab แยก loopback IP และ port สำหรับหลาย CVE
- ทดลอง scanner และ recon tools กับเป้าหมายจริงใน lab
- เก็บข้อมูล 10 targets แยก `raw/` และ `normalized/` ตามเครื่องมือ
- ศึกษาความหมาย report ของ Nmap, Naabu, httpx-toolkit, Nuclei, Nikto, ZAP, Wapiti, sqlmap, AutoRecon, OpenVAS และ Metasploit
- วิเคราะห์รูปแบบ branch Hex แล้วกำหนดแนวทาง Dec ที่ลด data leakage
- เขียนข้อเสนอ feature, schema, label และเครื่องมือเก็บข้อมูลสำหรับ Exploit-DL
- เขียน builder รุ่นทดลอง `build_dec_dataset_v2.py`
- อัปเอกสารสองไฟล์ไป branch `Dec` แล้ว
- เปลี่ยนตัวอย่างรหัสผ่าน GVM ในเอกสารท้องถิ่นเป็นตัวแปร `${GVM_PASSWORD}` เพื่อไม่เผย credential
- sanitize ตัวอย่างรหัสผ่าน GVM ใน runbook 10 CVEs แล้ว

## สถานะ GitHub ที่ยืนยันแล้ว

Commit ล่าสุดที่สร้างในงานรอบนี้:

```text
00cb150b7d07fb53706b10fb822f2d70f5d3c079
Add Dec feature and scanner tool documentation
```

ไฟล์ที่อัปแล้ว:

- `dec-feature-and-tool-recommendations-th.md`
- `tool-study-article-th.md`

หมายเหตุ: สำเนา `tool-study-article-th.md` บน GitHub ยังมีรหัสผ่านตัวอย่างเดิมจนกว่าจะอัปฉบับแก้ไข ควรเปลี่ยนรหัสผ่านบัญชี GVM หากรหัสนั้นยังใช้งานอยู่

## Dataset ปัจจุบัน

ตำแหน่งบน Windows:

```text
C:\Users\rapii\Desktop\kali-share\dataset
```

ตำแหน่ง shared folder บน Kali:

```text
/media/sf_kali-share/dataset
```

สรุป inventory ณ 2026-08-05:

| รายการ | จำนวน |
|---|---:|
| Targets | 10 |
| ไฟล์ทั้งหมด | 348 |
| ขนาดรวม | 3,574,890 bytes (ประมาณ 3.41 MiB) |
| ไฟล์ 0 bytes | 16 |
| Raw files | 264 |
| Normalized files | 84 |

Targets:

1. `apache_41773`
2. `django_34265`
3. `druid_25646`
4. `elfinder_32682`
5. `glassfish_1000028`
6. `gogs_18925`
7. `jackson_7525`
8. `spring_22965`
9. `struts2_s2045`
10. `tomcat_12615`

## Coverage ตามเครื่องมือ

| Tool | Raw targets | Normalized targets | สถานะ |
|---|---:|---:|---|
| AutoRecon | 10 | 10 | มี raw 16 ไฟล์เป็น 0 bytes ต้องตรวจสาเหตุ |
| httpx-toolkit | 10 | 10 | JSONL ใช้งานได้ |
| Naabu | 10 | 10 | JSONL ใช้งานได้ |
| Nikto | 10 | 10 | normalized เป็น JSON หลายบรรทัด ไม่ใช่ JSONL จริง |
| Nmap | 10 | 10 | normalized เป็น JSON หลายบรรทัด ไม่ใช่ JSONL จริง |
| Nuclei | 10 | 10 | JSONL ใช้งานได้และมี finding จริง |
| Wapiti | 10 | 10 | normalized เป็น JSON หลายบรรทัด ไม่ใช่ JSONL จริง |
| ZAP | 10 | 10 | ผลปัจจุบันมีแนวโน้มเป็น startup/incomplete report |
| Metasploit | 3 | 3 | มีเฉพาะ Spring, Struts2 และ Tomcat |
| sqlmap | 1 | 1 | มีเฉพาะ Django และผลสุดท้ายไม่ยืนยัน SQLi |
| OpenVAS/GVM | 0 | 0 | ยังไม่ได้ export report เข้า dataset |

ผลตรวจรูปแบบ `.jsonl`:

- เป็น JSONL จริง: `httpx-toolkit`, `naabu`, `nuclei`
- เป็น JSON document หลายบรรทัดแต่ใช้นามสกุล `.jsonl`: `autorecon`, `metasploit`, `nikto`, `nmap`, `sqlmap`, `wapiti`, `zaproxy`
- ต้องแปลงกลุ่มหลังให้เป็น one JSON object per line หรือเปลี่ยนนามสกุลเป็น `.json` ก่อนใช้ pipeline

## ข้อค้นพบสำคัญ

- Nuclei มี findings หลายรายการ แต่ exact CVE match กับ ground truth ยังมีน้อย จึงห้ามตีความ `finding_count > 0` ว่า exploit สำเร็จ
- Struts2: Metasploit แสดงว่า injected code ทำงาน แต่ไม่มี session ต้องเก็บเป็นสถานะกลาง ไม่ใช่ success แบบเต็ม
- Spring: exploit completed แต่ไม่มี session
- Tomcat: module รายงาน not vulnerable/not exploitable และ upload ไม่สำเร็จ
- Django/sqlmap: มี heuristic signal แต่ผลสุดท้ายไม่ยืนยัน parameter injectable จัดเป็น false positive หรือ unconfirmed
- ZAP ที่รันใน Docker เข้าถึง `127.0.0.x` ของ host ไม่ได้โดยตรงหากไม่มี host networking หรือ host gateway ที่ถูกต้อง
- OpenVAS task เริ่มผ่าน GMP CLI ได้ แต่ report ยังไม่ถูก export เข้า raw/normalized

## กติกาข้อมูลที่ตกลงแล้ว

- เก็บ raw แบบ immutable และบันทึก hash
- normalized ต้องมี schema version และ provenance กลับไปยัง raw
- แยก observation, candidate และ execution label ออกจากกัน
- ใช้ `target_id`, `scan_run_id`, `tool`, `tool_version`, `observed_at` และ `raw_sha256` เป็น metadata หลัก
- split train/validation/test ตาม target, product หรือ CVE family ไม่สุ่มแถวแบบธรรมดา
- ห้ามใส่ label-derived fields เช่น exact exploit outcome, session text หรือ CVE ที่มาจากขั้นยืนยันลงใน input feature
- เก็บสถานะ missing/unknown แยกจากค่า 0
- redact IP ภายนอก, hostname, cookie, token, credential และข้อมูลส่วนตัวก่อนเผยแพร่
- ห้ามใช้ผลจากระบบที่ไม่ได้รับอนุญาต

## ไฟล์งานท้องถิ่น

ตำแหน่ง:

```text
C:\Users\rapii\Documents\Codex\2026-08-03\faraday-https-github-com-infobyte-faraday\outputs
```

ไฟล์สำคัญ:

- `DEC-CURRENT-STATUS.md` - handoff และสถานะล่าสุด
- `dec-feature-and-tool-recommendations-th.md` - feature/schema/tool recommendations
- `tool-study-article-th.md` - บทความอธิบายเครื่องมือที่ใช้จริง
- `hex-vs-dec-dataset-analysis-th.md` - วิเคราะห์ Hex เทียบ Dec และ leakage
- `build_dec_dataset_v2.py` - builder รุ่นทดลอง
- `agent-run-10-cves-raw-normalized-2026-08-04.md` - runbook สแกน 10 CVEs
- `dataset-platforms-cheatsheet.md` - คำสั่งแพลตฟอร์มและ import workflow
- `scanner-dataset-blueprint.md` - blueprint ของ dataset

## ไฟล์ที่ควรอัปเพิ่ม

ลำดับแนะนำ:

1. `DEC-CURRENT-STATUS.md` เพื่อใช้ handoff ข้าม session
2. `tool-study-article-th.md` ฉบับลบรหัสผ่านจริง
3. `build_dec_dataset_v2.py` เพื่อให้ dataset สร้างซ้ำได้
4. `scanner-dataset-blueprint.md` เป็นภาพรวมโครงสร้าง
5. `agent-run-10-cves-raw-normalized-2026-08-04.md` หลังตรวจคำสั่งและ secret scan อีกครั้ง
6. `dataset-platforms-cheatsheet.md` หลัง sanitize credential และค่าเริ่มต้นของฐานข้อมูล

ไม่อัป `hex-vs-dec-dataset-analysis-th.md` เป็นเอกสารแยก เพราะ Hex และ Dec เป็นส่วนที่จะต้องรวมกัน ให้ใช้ไฟล์นี้เป็น working note ภายใน แล้วนำ schema, leakage controls และข้อสรุปที่เกี่ยวข้องไปรวมในเอกสารกลางของ dataset

ยังไม่ควรอัปทันที:

- raw reports ที่ยังไม่ผ่าน secret/PII scan
- ไฟล์ 0 bytes
- normalized ที่นามสกุล `.jsonl` แต่ไม่เป็น JSONL จริง
- report ที่มี cookie, token, request body, credential หรือ external IP
- installer script ที่ยังไม่ได้ทดสอบแบบ clean install

## ช่องว่างที่ต้องปิด

- ไม่มี OpenVAS export
- Metasploit labels ยังไม่ครบ 10 targets
- SQLmap มีเพียง target เดียว และไม่ควรรันกับ endpoint ที่ไม่มี parameter
- ZAP reports ยังไม่ใช่ structured finding ที่พร้อมใช้
- normalized schema ยังไม่สม่ำเสมอข้ามเครื่องมือ
- ยังไม่มี manifest รวม `target_id`, CVE ground truth, image digest, exposed endpoint และ scan timestamps
- ยังไม่มี candidate exploit table ต่อ target
- ยังไม่มี quality report ที่วัด parse errors, duplicates, missing fields และ leakage
- ยังไม่มี reproducible train/validation/test split

## งานถัดไป

1. เปลี่ยนรหัสผ่าน GVM หากยังใช้ค่าเดิม และอัปเอกสารฉบับ sanitize
2. export OpenVAS report ของ Struts2 เป็น XML/JSON แล้ว normalize โดยเก็บ OID, CVE, CVSS, QoD, host, port และ evidence
3. แก้ normalized files ให้เป็น JSONL จริงและเพิ่ม `schema_version`
4. สร้าง `manifest.jsonl` สำหรับ 10 targets พร้อม CVE ground truth และ image digest
5. รัน `build_dec_dataset_v2.py` ไปยัง directory ใหม่ แล้วตรวจ quality report โดยไม่แก้ raw เดิม
6. ตรวจและจัด Metasploit outcome taxonomy ให้แยก `code_execution`, `session_opened`, `not_vulnerable`, `not_exploitable`, `failed` และ `unknown`
7. ทำ candidate generation จาก service/CPE/CVE ไปยัง Metasploit module แล้วสร้างหนึ่งแถวต่อ candidate
8. เพิ่มอย่างน้อยหนึ่ง negative control ที่ patched หรือ non-vulnerable ต่อ product family
9. ทำ grouped split ตาม product/CVE family และสร้าง baseline model ก่อน Deep Learning
10. เพิ่ม README index ที่ลิงก์ schema, builder, runbook, status และ data dictionary

## Definition of Done ระยะถัดไป

- 10 targets มี manifest ครบและตรวจย้อนกลับไปยัง Vulhub compose/image ได้
- raw ทุกไฟล์มี SHA-256 และไม่มี secret ที่ตรวจพบ
- normalized ทุกไฟล์ผ่าน parser และ schema validation
- OpenVAS, Nuclei, Nmap/httpx และ execution labels เชื่อมด้วย `target_id`/`scan_run_id`
- candidate table มีทั้ง positive, negative และ unknown
- train/validation/test ไม่มี target หรือ product leakage
- pipeline สร้าง dataset ซ้ำจาก raw ได้ด้วยคำสั่งเดียว

## บันทึกการตัดสินใจ

| วันที่ | การตัดสินใจ | เหตุผล |
|---|---|---|
| 2026-08-05 | ใช้ไฟล์นี้เป็น handoff หลัก | ลดการสูญเสียบริบทเมื่อเปลี่ยน session |
| 2026-08-05 | แยก raw, normalized, feature และ label | ป้องกัน leakage และตรวจย้อนกลับได้ |
| 2026-08-05 | ไม่ถือ scanner CVE match เป็น exploit success | detection กับ exploitation เป็นคนละหลักฐาน |
| 2026-08-05 | ใช้ target-candidate เป็นหน่วย model-ready | สอดคล้องกับงาน exploit ranking/selection |
| 2026-08-05 | เก็บ unknown แยกจาก false | การไม่พบอาจเกิดจาก coverage หรือ scanner failure |
