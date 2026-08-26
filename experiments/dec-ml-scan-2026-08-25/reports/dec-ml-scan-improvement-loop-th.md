# Dec ML Scan Improvement Loop

เอกสารนี้สรุปวิธีทำงานรอบถัดไปของ Dec ML scan ให้เป็นวงจรที่ใช้จริงได้ ไม่ใช่แค่เทรนให้คะแนนสวย

## สถานะล่าสุด

หลังเพิ่ม `features-enriched.csv` จาก raw-curated evidence แล้ว ML ดีขึ้นจาก Top-1 `0.759` เป็น `0.862` และ mean attempts ลดจาก `2.586` เป็น `1.793`

หลัง opencode ฝั่ง Kali สแกน validation เพิ่มและ import ผลกลับมาแล้ว โหมด merged ดีขึ้นอีกเป็น Top-1 `0.931`, Top-3 `1.000`, mean attempts `1.103`

ก่อน validation scan ตัวที่ยังพลาด Top-3 เหลือ 3 target:

- `spring_CVE-2022-22965`
- `shiro_CVE-2016-4437`
- `goahead_CVE-2017-17562`

หลัง validation scan:

- `shiro_CVE-2016-4437`: validated_positive จาก `rememberMe=deleteMe`
- `goahead_CVE-2017-17562`: validated_positive จาก `Document Error` / `Access Error`
- `spring_CVE-2022-22965`: inconclusive เพราะยังไม่พบ Spring-specific fingerprint
- failure report โหมด merged เหลือ `[]`

## ทำไมต้องสแกนเพิ่ม

ML ไม่ได้รู้เองว่า target คืออะไร มันดู feature จาก scanner เช่น title, server header, nmap service, body fingerprint, evidence text, port และ protocol ถ้า scanner เก็บหลักฐานไม่พอ target หลายตัวจะหน้าตาเหมือนกัน โดยเฉพาะกลุ่ม web port `8080`

ดังนั้นการเพิ่มผล scan มีผลมาก ถ้าเพิ่มถูกจุด:

- Spring ต้องมี evidence ที่บอก Spring/actuator/framework มากกว่าแค่ Tomcat/8080
- Shiro ต้องมี evidence เรื่อง `rememberMe`, cookie, login flow หรือ Shiro-specific behavior
- GoAhead ต้องมี banner/path ที่บอก GoAhead ไม่ใช่แค่หน้า Home Page

## Loop ที่ใช้

1. รัน ML เพื่อหา target ที่พลาด
2. สร้าง scan queue จาก failure report
3. ยิง safe scan/probe บน Kali เฉพาะ local Vulhub/Docker lab
4. เก็บผลเป็น raw-curated ไม่เอา cache/runtime/dependency
5. import validation label กลับเข้า experiment
6. enrich feature จาก evidence ใหม่
7. evaluate ML ใหม่
8. ถ้ายังพลาด ให้กลับไปข้อ 2

## คำศัพท์

- `feature`: ข้อมูลที่ป้อนให้ ML ใช้ตัดสิน เช่น port, title, server, nmap service, keyword จาก evidence
- `candidate family`: ประเภท/ตระกูลช่องโหว่ที่ ML ต้องจัดอันดับ เช่น spring, shiro, goahead
- `weak label`: label จากชื่อ lab หรือ metadata ยังไม่ใช่ผลยืนยันจริง
- `validated label`: label ที่ยืนยันจากผล scan/probe แล้ว
- `positive control`: target ที่ ML ทำถูกอยู่แล้ว ใช้เช็กว่า pipeline ไม่พังหลังแก้
- `regression guard`: target ที่เคยพลาดแต่แก้แล้ว ใช้เช็กว่า feature รอบใหม่ไม่ทำให้กลับไปพลาด
- `raw-curated`: raw scan ที่คัดเฉพาะหลักฐานจริง ไม่เก็บ cache, runtime, dependency หรือไฟล์ขยะ

## รอบ scan ถัดไป

ถ้าจะสแกนเพิ่ม ให้โฟกัส Spring ก่อน เพราะเป็นตัวเดียวที่ validation ยัง inconclusive:

- หา Spring lab ที่มี actuator เปิด
- หา response ที่มี `spring`, `spring boot`, `Whitelabel Error Page`
- ใช้ nuclei/template เฉพาะ Spring fingerprint แบบ safe
- หลีกเลี่ยง payload ที่เขียนไฟล์หรือเปลี่ยน state

queue เดิมอยู่ที่:

```text
experiments/dec-ml-scan-2026-08-25/validation-target-queue.csv
```

และ run-kit:

```text
experiments/dec-ml-scan-2026-08-25/kali-run-kit
```

เมื่อ Kali เปิดได้ ให้รัน:

```bash
cd /media/sf_kali-share/dataset/dec-kali-validation-run-kit
python3 scripts/kali/dec_validation_runner.py \
  --queue validation-target-queue.csv \
  --features features.csv \
  --output-dir /home/kali/reports/dec-validation-manual
mkdir -p /media/sf_kali-share/dataset/dec-validation-manual
cp -a /home/kali/reports/dec-validation-manual/. /media/sf_kali-share/dataset/dec-validation-manual/
```

หลังจากนั้นฝั่ง Windows ค่อย import กลับเข้า ML และ evaluate ใหม่
