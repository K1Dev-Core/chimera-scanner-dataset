# สถานะการเพิ่ม Dataset สำหรับ Exploit-DL

ไฟล์นี้สรุปแบบภาษาคนว่า ตอนนี้ dataset ของ Chimera/Exploit-DL ไปถึงไหนแล้ว และควรทำอะไรต่อก่อนเข้าสู่ขั้น `Fingerprint → Feature → Model` แบบจริงจัง

## คำตอบสั้น ๆ

ตอนนี้ข้อมูล **พอเริ่มทำ baseline ได้แล้ว** แต่ยัง **ไม่พอสำหรับ Deep Learning ที่แม่นจริง**

เหตุผลคือข้อมูลปัจจุบันยังมีจำนวน target น้อย และ label หลักยังเป็น `weak label` จาก prior/metadata/scanner evidence ไม่ใช่ผลจากการลอง exploit ใน lab แล้วบันทึกว่า `success/fail` จริง

สิ่งที่มีตอนนี้เหมาะกับ:

- demo pipeline ว่า scan แล้วแปลงเป็น feature ได้
- train baseline เช่น RandomForest
- ทดลอง ranking ว่าโมเดลช่วย prioritize ได้ไหม
- เขียนบทที่อธิบายข้อจำกัดของ weak label

สิ่งที่ยังต้องเพิ่มถ้าอยากให้โมเดล “สไนเปอร์” ขึ้น:

- lab เพิ่มอีกอย่างน้อย 30–100 target
- negative samples หรือ target ที่ไม่มีช่องโหว่ family นั้น
- label จากผล validation จริง เช่น `exploit_success_observed=true/false`
- product/version/CVE feature ที่ละเอียดกว่าเดิม
- split dataset แบบไม่รั่ว เช่น แยกตาม product หรือ CVE year

## ข้อมูลที่มีอยู่แล้ว

ชุด `multi-vuln-web` มีเว็บหลายช่องโหว่ เช่น Juice Shop, WebGoat, DVWA, bWAPP, Mutillidae และมี unseen lab ที่สร้างเอง เช่น Acme/Nova รวมถึง hard lab แบบ Grafana

จุดแข็ง:

- เหมาะกับ demo
- มีหลาย exploit family เช่น SQLi, XSS, command injection, SSRF, broken access control
- มี script สร้าง feature และ train baseline แล้ว

จุดอ่อน:

- จำนวน target ยังน้อย
- lab บางตัวเป็น training-style มากเกินไป ไม่เหมือนระบบจริง
- label ยังไม่ใช่ success/fail จาก exploit validation
- model ตอนนี้ bias ไปทาง SQLi/command-injection เพราะข้อมูลเดิมให้น้ำหนักสองกลุ่มนี้เยอะ

## Lab batch ใหม่ที่เตรียมไว้

เพิ่ม manifest ไว้ที่:

```text
records/staged-vulhub-expansion-labs.json
```

ชุดนี้เน้น product จริงและ CVE ใหม่กว่าเดิม:

- Langflow CVE-2025-3248
- pgAdmin CVE-2025-2945
- Cacti CVE-2025-24367
- 1Panel CVE-2024-39907
- TeamCity CVE-2024-27198
- GeoServer CVE-2024-36401
- Confluence CVE-2023-22527
- Metabase CVE-2023-38646
- RocketMQ CVE-2023-33246
- Redis CVE-2022-0543
- GitLab CVE-2021-22205
- Grafana CVE-2024-9264

หมายเหตุ: รอบล่าสุด Docker Desktop daemon บนเครื่องยัง start ไม่สำเร็จ เลยยังสแกน batch นี้จริงไม่ได้ แต่เตรียม script สำหรับรันต่อไว้แล้ว

## วิธีรัน batch เพิ่มเมื่อ Docker พร้อม

เปิด PowerShell แล้วรัน:

```powershell
cd C:\Users\uSeR\Documents\Codex\2026-08-04\docker-cve-wp2shell-2\work\chimera-scanner-dataset\chimera-tools-name-date-2026-08-05-multi-vuln-web

powershell -ExecutionPolicy Bypass -File scripts\scan_staged_vulhub_expansion.ps1 -DatasetRoot .
```

output จะอยู่ใต้:

```text
live-reports\vulhub-expansion-<date-time>\
```

## การแปลงเป็น Feature

แนวคิดหลักคือเปลี่ยนข้อมูลดิบจาก scanner ให้เป็นแถวตัวเลข:

```text
target fingerprint -> feature row -> candidate exploit rows -> model ranking
```

ตัวอย่าง feature ที่ควรเก็บ:

- port open เช่น `port_80_open`, `port_443_open`, `port_8080_open`
- service/product/version จาก nmap
- HTTP title/status/server/tech จาก httpx
- nuclei template/severity/CVE ถ้ามี
- scanner evidence count ต่อ family
- product family เช่น `grafana`, `jenkins`, `redis`, `tomcat`
- auth context เช่น `pre-auth`, `post-auth`, `unknown`

## Label ที่ควรออกแบบ

ขั้นต่ำควรมี:

```text
target_id
candidate_exploit_family
candidate_cve
rank_score
label_source
exploit_success_observed
```

สำหรับตอนนี้:

```text
exploit_success_observed = null
label_source = weak_label / lab_prior / scanner_evidence
```

รอบถัดไปควรเพิ่ม:

```text
exploit_success_observed = true/false
validation_method = safe_local_validation
attempt_order
time_to_confirm_seconds
```

## สรุปสำหรับโปรเจกต์

ถ้าจะเดินต่อให้ตรงหัวข้อ “ระบบเลือก Exploit อัตโนมัติด้วย Deep Learning” ผมแนะนำลำดับนี้:

1. เพิ่ม dataset จาก Vulhub batch ใหม่ให้ได้อย่างน้อย 30 lab
2. normalize ทุก scanner output ให้เป็น schema เดียว
3. สร้าง feature matrix แบบ numeric + one-hot/text feature
4. ทำ label แบบ weak label ก่อน เพื่อ demo ranking
5. เพิ่ม validation loop เฉพาะ local lab เพื่อเก็บ success/fail จริง
6. train baseline model เช่น RandomForest/LightGBM
7. ค่อยต่อ Deep Learning เมื่อข้อมูลเยอะพอ

พูดตรง ๆ: ตอนนี้ “เริ่มได้แล้ว” แต่ถ้าอยากให้โมเดลดูเก่งจริง ไม่ใช่เดาจาก prior ต้องเพิ่ม data + label จริงก่อน
