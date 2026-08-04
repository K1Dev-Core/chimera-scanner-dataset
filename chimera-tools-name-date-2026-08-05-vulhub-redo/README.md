# Chimera Scanner Dataset - Vulhub Redo (2026-08-05)

ชุดข้อมูลนี้เป็นรอบสแกน vulnerable lab จาก Vulhub สำหรับโปรเจกต์ **Exploit-DL: ระบบเลือก Exploit อัตโนมัติด้วย Machine Learning / Deep Learning**

แนวคิดง่าย ๆ คือ เราเอาผลสแกนจากหลายเครื่องมือ เช่น `nmap`, `httpx`, `nuclei`, `nikto` มาแปลงเป็นข้อมูลที่โมเดลอ่านได้ เช่น port, service, version, title, technology, CVE signal แล้วใช้เป็นฐานสำหรับทำนายว่า target แบบนี้ควรลอง exploit/CVE อะไรก่อน

## ขอบเขตของชุดข้อมูล

- แหล่งข้อมูล: Docker lab ในเครื่องจาก Vulhub
- Run ID: `202608041930-vulhub-expanded`
- จำนวน lab: 8
- Tools: `naabu`, `nmap`, `httpx`, `nuclei`, `nikto`
- ความปลอดภัย: เก็บข้อมูลจากการสแกน/fingerprint เท่านั้น ยังไม่ได้ยิง exploit จริง

## โครงสร้างโฟลเดอร์

```text
datasets/
  labs/<lab-id>/lab.json
  tools-name-date/<tool-name>-2026-08-05/<lab-id>/
    raw/          # output ดิบจาก tool
    normalized/   # output ที่ parse ให้อ่านง่ายขึ้น

records/
  all-records.jsonl
  exploit-dl-features.jsonl
  exploit-labels.jsonl

manifests/
  index.json
  source-run-manifest.json
  checksums.sha256
```

## ไฟล์ที่ควรเริ่มอ่าน

- `records/exploit-dl-features.jsonl`  
  ตาราง feature หลักของรอบนี้ แต่ละแถวคือข้อมูล target/service/web surface หนึ่งจุด

- `records/exploit-labels.jsonl`  
  label เบื้องต้นจากชื่อ lab/CVE ของ Vulhub เช่น target นี้ตั้งใจจำลอง CVE อะไร

- `datasets/tools-name-date/.../raw/`  
  รายงานดิบจากแต่ละ tool เผื่ออยากกลับไป parse เพิ่มเอง

## คำเตือนเรื่อง label

label ในชุดนี้เป็น **weak label / candidate label** จากตัวตนของ lab เช่น lab ชื่อ `CVE-2024-36401` จึงถือว่าเป็น positive candidate ของ CVE นั้น

แต่ยังไม่ใช่คำตอบว่า “ยิง exploit สำเร็จจริง” เพราะรอบนี้ยังไม่ได้รัน exploit validation

ถ้าจะใช้ทำโมเดลจริงจัง ขั้นต่อไปควรเพิ่ม field:

- `exploit_id`
- `exploit_family`
- `exploit_success_observed`
- `exploit_runtime_seconds`
- `exploit_error`

## ใช้ทำอะไรได้ตอนนี้

เหมาะสำหรับ:

- ทดลองแปลง scanner report เป็น feature
- ทำ baseline model จาก service/version/web fingerprint
- ทดลองจับคู่ target fingerprint กับ CVE/product label
- ใช้เป็น seed dataset ก่อนเพิ่ม exploit validation

ยังไม่เหมาะสำหรับ:

- สรุปว่าโมเดลยิง exploit สำเร็จจริง
- วัด performance แบบ research-grade
- train deep learning ขนาดใหญ่ เพราะจำนวนข้อมูลยังน้อย
