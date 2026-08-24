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
- พัฒนาและรัน `build_dec_dataset_v2.py` กับข้อมูลจริง 10 targets สำเร็จ
- ตรวจ reproducibility สองรอบ พบว่า artifacts ที่ต้อง deterministic จำนวน 10 ไฟล์มี SHA-256 ตรงกันทั้งหมด
- อัปเอกสาร, builder และ generated Dec v2 dataset ไป branch `Dec` แล้ว
- เปลี่ยนตัวอย่างรหัสผ่าน GVM ในเอกสารท้องถิ่นเป็นตัวแปร `${GVM_PASSWORD}` เพื่อไม่เผย credential
- sanitize ตัวอย่างรหัสผ่าน GVM ใน runbook 10 CVEs แล้ว

## สถานะ GitHub ที่ยืนยันแล้ว

Commits สำคัญที่สร้างในงานรอบนี้:

```text
00cb150b7d07fb53706b10fb822f2d70f5d3c079
Add Dec feature and scanner tool documentation

2017e2721d904483f8d1f3d413e846f9f0f75555
Add Dec weekly status and session handoff

3efa7b5725f813b26c661cf0c0ee45159d2d5e87
Add reproducible Dec dataset builder

54b27803dca617ec16c948acc236124042a6ed27
Add scanner dataset blueprint

6b33080788afeb103e49014dfa28390b5acfba6b
Replace duplicated tool study with sanitized version

9b415f8678d96b61c126cd022977bae0b3852143
Add redaction and integrity checks to Dec builder

88a2a8dd067f26932c237014a928c76aeb96ded0
Add Dec v2 manifest and quality report

b837b4e92a12f67afba5dce913d3d4438470cd3f
Add Dec v2 target feature datasets
```

ไฟล์ที่อัปแล้ว:

- `dec-feature-and-tool-recommendations-th.md`
- `tool-study-article-th.md`
- `DEC-CURRENT-STATUS.md`
- `build_dec_dataset_v2.py`
- `scanner-dataset-blueprint.md`
- `generated/dec-v2-2026-08-05/` พร้อม records, derived features, labels, manifest, quality report และ checksums

`tool-study-article-th.md` บน GitHub ถูกแทนที่ด้วยฉบับ sanitize แล้ว ไม่พบรหัสผ่านแล็บเดิมและใช้ `${GVM_PASSWORD}` แทน อย่างไรก็ตามควรเปลี่ยนรหัสผ่านบัญชี GVM หากค่าดังกล่าวเคยใช้จริง

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

## Generated Dec v2

ผลจาก builder ที่ผ่านการตรวจอยู่ที่:

```text
C:\Users\rapii\Documents\Codex\2026-08-03\faraday-https-github-com-infobyte-faraday\work\dec-dataset-v2-2026-08-05
```

GitHub:

```text
https://github.com/K1Dev-Core/chimera-scanner-dataset/tree/Dec/generated/dec-v2-2026-08-05
```

| Record set | Count |
|---|---:|
| Targets | 10 |
| Observations | 48 |
| Findings | 386 |
| Validations | 5 |
| All records | 449 |
| Target features | 10 |
| Target-candidate features | 80 |
| Target-candidate labels | 80 |

ผลตรวจ:

- JSONL ทุกไฟล์ valid และไม่มี invalid line
- ไม่พบ `record_id` ซ้ำ
- ทุก target มี candidate 8 families
- label references เชื่อมกับ candidate features ครบ
- ไม่พบ label-derived field ใน feature table
- ไม่พบ unredacted sensitive record หลัง builder redact session identifier 1 record
- source path ใน manifest เป็นค่า portable `dataset` ไม่เผย absolute path ของเครื่อง
- deterministic artifacts 10 ไฟล์มี SHA-256 ตรงกันเมื่อสร้างซ้ำสองรอบ
- OpenVAS ยังไม่มี output และ ZAP/AutoRecon ยังเป็น coverage summary ตาม warnings ใน quality report

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

## ไฟล์ที่ควรอัปเพิ่มในรอบถัดไป

ลำดับแนะนำ:

1. `agent-run-10-cves-raw-normalized-2026-08-04.md` หลังตรวจคำสั่งและ secret scan อีกครั้ง
2. `dataset-platforms-cheatsheet.md` หลัง sanitize credential และค่าเริ่มต้นของฐานข้อมูล
3. README index หลัง schema ของ Hex และ Dec ถูกรวมเป็นแบบเดียวกันแล้ว

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
- source normalized เดิมยังไม่สม่ำเสมอ แต่ generated v2 ถูกแปลงเป็น JSONL schema 2.0.0 แล้ว
- generated manifest มี target/CVE/tool coverage และ counts แต่ยังขาด container image digest กับ scan timestamps บางส่วน
- generated candidate table เป็น vulnerability-family candidates ยังไม่ใช่ Metasploit module candidates
- ยังไม่มี reproducible train/validation/test split

## งานถัดไป

1. เปลี่ยนรหัสผ่าน GVM หากยังใช้ค่าเดิม และอัปเอกสารฉบับ sanitize
2. export OpenVAS report ของ Struts2 เป็น XML/JSON แล้ว normalize โดยเก็บ OID, CVE, CVSS, QoD, host, port และ evidence
3. กำหนดให้ generated schema 2.0.0 เป็น canonical normalized dataset หรือ migrate source normalized เดิมให้ตรง schema นี้
4. เพิ่ม container image digest, exposed endpoint และ scan timestamps ลง manifest ของ 10 targets
5. รวม schema ของ Hex และ Dec ให้เป็น schema กลาง โดยไม่อัปเอกสารเปรียบเทียบแยก
6. ตรวจและจัด Metasploit outcome taxonomy ให้แยก `code_execution`, `session_opened`, `not_vulnerable`, `not_exploitable`, `failed` และ `unknown`
7. ทำ candidate generation จาก service/CPE/CVE ไปยัง Metasploit module แล้วสร้างหนึ่งแถวต่อ candidate
8. เพิ่มอย่างน้อยหนึ่ง negative control ที่ patched หรือ non-vulnerable ต่อ product family
9. ทำ grouped split ตาม product/CVE family และสร้าง baseline model ก่อน Deep Learning
10. เพิ่ม README index ที่ลิงก์ schema, builder, generated output, runbook, status และ data dictionary

## Definition of Done ระยะถัดไป

- [ ] 10 targets มี manifest ครบและตรวจย้อนกลับไปยัง Vulhub compose/image ได้
- [ ] raw ทุกไฟล์มี SHA-256 และไม่มี secret ที่ตรวจพบ
- [x] generated normalized ทุกไฟล์ผ่าน JSON parser, duplicate-ID และ integrity validation
- [ ] OpenVAS, Nuclei, Nmap/httpx และ execution labels เชื่อมด้วย `target_id`/`scan_run_id`
- [ ] candidate table มีทั้ง positive, negative และ unknown จากผล execution จริง
- [ ] train/validation/test ไม่มี target หรือ product leakage
- [x] pipeline สร้าง model-ready dataset ซ้ำจาก raw ได้ด้วยคำสั่งเดียว

## บันทึกการตัดสินใจ

| วันที่ | การตัดสินใจ | เหตุผล |
|---|---|---|
| 2026-08-05 | ใช้ไฟล์นี้เป็น handoff หลัก | ลดการสูญเสียบริบทเมื่อเปลี่ยน session |
| 2026-08-05 | แยก raw, normalized, feature และ label | ป้องกัน leakage และตรวจย้อนกลับได้ |
| 2026-08-05 | ไม่ถือ scanner CVE match เป็น exploit success | detection กับ exploitation เป็นคนละหลักฐาน |
| 2026-08-05 | ใช้ target-candidate เป็นหน่วย model-ready | สอดคล้องกับงาน exploit ranking/selection |
| 2026-08-05 | เก็บ unknown แยกจาก false | การไม่พบอาจเกิดจาก coverage หรือ scanner failure |
| 2026-08-05 | ยืนยัน builder ด้วยการสร้างซ้ำและเทียบ SHA-256 | พิสูจน์ว่า model-ready artifacts สร้างซ้ำได้ |
| 2026-08-05 | อัป generated output แยกจาก raw source | ให้ใช้งาน feature/label ได้โดยไม่แก้หรือทำซ้ำ raw |
