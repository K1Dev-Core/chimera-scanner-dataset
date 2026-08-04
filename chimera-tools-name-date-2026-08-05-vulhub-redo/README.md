# Chimera Scanner Dataset - Vulhub Redo (2026-08-05)

ชุดนี้เป็น dataset จากการสแกน vulnerable lab ของ Vulhub สำหรับโปรเจกต์ **Exploit-DL: ระบบช่วยเลือก exploit อัตโนมัติด้วย Machine Learning / Deep Learning**

รอบนี้เน้นเก็บข้อมูลแบบ “หนึ่ง lab ต่อหนึ่ง CVE/product” เพื่อใช้เป็นฐานสำหรับเรียนรู้ความสัมพันธ์ระหว่าง fingerprint ของ target กับ CVE หรือ product ที่เกี่ยวข้อง

พูดง่าย ๆ คือ เราเอาผลจาก tools เช่น `naabu`, `nmap`, `httpx`, `nuclei`, `nikto` มาแปลงเป็นข้อมูลที่ model ใช้ต่อได้ เช่น port, service, version, web title, tech stack และ scanner signal

## ขอบเขตของ dataset

- Source: local Docker labs จาก Vulhub
- Run ID: `202608041930-vulhub-expanded`
- จำนวน lab: 8
- Tools: `naabu`, `nmap`, `httpx`, `nuclei`, `nikto`
- Scope: เก็บ fingerprint/report จาก scanner เท่านั้น ยังไม่ได้รัน exploit validation

## โครงสร้างไฟล์

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

## ไฟล์ที่ควรเริ่มดู

- `records/exploit-dl-features.jsonl`  
  feature หลักของชุดนี้ แต่ละแถวคือข้อมูลจาก target/service/web surface ที่ scanner เจอ

- `records/exploit-labels.jsonl`  
  label เบื้องต้นจาก lab identity เช่น lab นี้ถูกสร้างมาเพื่อจำลอง CVE อะไร

- `datasets/tools-name-date/.../raw/`  
  รายงานดิบจากแต่ละ tool เผื่ออยาก parse เพิ่มหรือกลับไปตรวจหลักฐาน

## เรื่อง label ต้องเข้าใจตรงนี้ก่อน

label ในชุดนี้เป็น **weak label / candidate label** จากชื่อ lab และ CVE ของ Vulhub

ตัวอย่างเช่น ถ้า lab ชื่อ `geoserver-cve-2024-36401` เราถือว่า target นี้มี candidate label เป็น `CVE-2024-36401`

แต่ label แบบนี้ยังไม่ใช่คำตอบว่า “exploit สำเร็จจริง” เพราะยังไม่มีการยิง exploit แล้วบันทึกผลสำเร็จ/ล้มเหลว

ถ้าจะเอาไปทำ model ที่จัดอันดับ exploit แบบจริงจัง ควรเพิ่มข้อมูลเหล่านี้ในรอบถัดไป:

- `exploit_id`
- `exploit_family`
- `exploit_success_observed`
- `exploit_runtime_seconds`
- `exploit_error`

## ใช้ dataset นี้ทำอะไรได้ดี

- ทดลองแปลง scanner report เป็น feature
- ทำ baseline model จาก service/version/web fingerprint
- ทดลองจับคู่ product/version กับ CVE label
- ใช้เป็น seed dataset ก่อนเพิ่ม exploit validation

## ข้อจำกัด

- ยังไม่มี exploit success label จริง
- จำนวน lab ยังน้อยสำหรับ Deep Learning จริงจัง
- ไม่ควรวัดผลแบบ production/research-grade จากชุดนี้อย่างเดียว

ถ้าโจทย์คือ demo ระบบ “สไนเปอร์เลือก exploit ก่อนหลัง” ให้ใช้ dataset ชุด `multi-vuln-web` ร่วมด้วย เพราะชุดนั้นมี target ที่มีหลาย exploit family ให้จัดอันดับในเว็บเดียว
