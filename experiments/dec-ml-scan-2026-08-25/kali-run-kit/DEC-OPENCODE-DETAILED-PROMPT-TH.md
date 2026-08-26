# Prompt ละเอียดสำหรับ opencode ฝั่ง Kali

คุณกำลังช่วยโปรเจกต์ `chimera-scanner-dataset` branch `Dec`

งานรอบนี้คือทำ validation scan เพิ่มให้ชุดทดลอง ML:

```text
dec-ml-scan-2026-08-25
```

เป้าหมายคือทดสอบว่า ML ranking ของเราเรียงลำดับ candidate vulnerability family ได้แม่นขึ้นไหม เมื่อเพิ่ม scanner-derived evidence ที่ใกล้การใช้งานจริงมากขึ้น

## ภาพรวมสิ่งที่ต้องทำ

ให้ทำเป็น loop แบบนี้:

1. อ่าน queue ว่า ML ยังพลาด target ไหน
2. เปิด local Vulhub/Docker lab ทีละ target
3. เก็บ evidence จาก scanner/probe แบบปลอดภัย
4. ตัดสิน validation status ต่อ target
5. เขียนผลเป็น `validation-results.jsonl`
6. เก็บ raw scan แบบ curated
7. copy ผลกลับ shared folder ให้ Codex ฝั่ง Windows นำไป import เข้า ML

งานนี้ไม่ใช่การโจมตีระบบจริง และไม่ใช่การ exploit แบบทำลายข้อมูล เป้าหมายคือเก็บหลักฐานให้ dataset/ML

## ขอบเขตความปลอดภัย

อนุญาตเฉพาะ:

- local Vulhub/Docker lab ที่รันบน Kali
- `127.0.0.1`
- Docker bridge/local container ที่ผู้ใช้ควบคุมเอง
- `/home/kali/reports`
- `/media/sf_kali-share/dataset`

ห้าม:

- สแกน public IP หรือ domain ภายนอก
- brute force username/password/token/key
- persistence
- destructive exploit
- เขียนไฟล์ webshell
- ลบ/แก้ข้อมูลใน container เว้นแต่เป็น safe lab step ที่จำเป็นและจดชัดเจน
- เก็บ cache/runtime/dependency เข้า dataset

ถ้าไม่แน่ใจว่า action นั้น destructive หรือไม่ ให้ข้ามและ mark เป็น `inconclusive`

## โฟลเดอร์เริ่มต้น

เข้าโฟลเดอร์นี้:

```bash
cd /media/sf_kali-share/dataset/dec-kali-validation-run-kit
```

ไฟล์ที่ควรมี:

```text
features.csv
validation-target-queue.csv
attack-order-top5.csv
attack-order-top5-merged.csv
scripts/kali/dec_validation_runner.py
DEC-KALI-VALIDATION-RUNBOOK-TH.md
DEC-KALI-VALIDATION-QUEUE-PROMPT-TH.md
```

ถ้าขาดไฟล์สำคัญ ให้รายงานก่อน ไม่ต้องเดาสุ่ม

## รัน automated safe runner ก่อน

ให้รันคำสั่งนี้ก่อนเสมอ:

```bash
python3 scripts/kali/dec_validation_runner.py \
  --queue validation-target-queue.csv \
  --features features.csv \
  --output-dir /home/kali/reports/dec-validation-manual
```

runner จะพยายามเก็บ:

- `nmap -sV`
- HTTP header/body
- safe probe path เฉพาะ family
- nikto ถ้ามี
- TCP probe สำหรับ Redis/Aria2
- `validation-results.jsonl`
- `SCAN-SUMMARY-TH.md`
- `raw-curated/<target_id>/raw/*`

หลัง runner จบ ให้ตรวจผลด้วยมืออีกครั้ง โดยเฉพาะ target ที่ `inconclusive`

## Queue รอบนี้

อ่านจาก:

```text
validation-target-queue.csv
```

target หลักที่ต้องโฟกัสคือ 3 ตัวที่ ML ยังจัด expected family ไม่เข้า Top-3:

```text
spring_CVE-2022-22965
shiro_CVE-2016-4437
goahead_CVE-2017-17562
```

target ตัวคุม:

```text
joomla_CVE-2023-23752
redis_CVE-2022-0543
aria2_rce
grafana_CVE-2021-43798
tomcat_CVE-2017-12615
nginx_CVE-2017-7529
```

ความหมาย:

- `hard_failure`: ML ยังพลาดมาก ต้องเก็บ evidence เพิ่มก่อน
- `near_miss`: ML พลาดเฉียด ๆ ต้องหา fingerprint เพิ่มให้ขยับเข้า Top-3
- `regression_guard`: target ที่เคยพลาดแต่ตอนนี้ดีขึ้นแล้ว ใช้เช็กว่า pipeline ไม่ถอย
- `positive_control`: target ที่ควรดูง่าย ใช้เช็กว่า tool/pipeline ทำงานถูก

## วิธีเตรียม output folder

ถ้าต้องทำ manual เพิ่ม ให้ใช้โครงนี้:

```bash
OUT=/home/kali/reports/dec-validation-manual
mkdir -p "$OUT"/{raw-curated,derived,logs}
```

ต่อ target ให้ใช้:

```bash
T="$OUT/raw-curated/<target_id>"
mkdir -p "$T/raw"
```

ทุกไฟล์ evidence ของ target นั้นให้ใส่ใน:

```text
$OUT/raw-curated/<target_id>/raw/
```

## วิธีหา host/port ของ lab

ใช้เท่าที่จำเป็น:

```bash
docker ps
ss -ltnp
docker compose ps
docker port <container>
```

ให้ใช้ local endpoint เท่านั้น เช่น:

```text
http://127.0.0.1:8080
http://127.0.0.1:3000
redis://127.0.0.1:6379
rpc://127.0.0.1:6800
```

ถ้า port ใน `features.csv` ไม่ตรงกับ lab ที่กำลังเปิด ให้จดใน `SCAN-SUMMARY-TH.md`

## Evidence พื้นฐานที่ควรเก็บทุก target

สำหรับ target ที่เป็น HTTP:

```bash
nmap -sV -Pn -p "$PORT" "$HOST" -oN "$T/raw/nmap.stdout" -oX "$T/raw/nmap.xml"
curl -k -i -L --max-time 10 "$URL" > "$T/raw/curl_home.txt"
curl -k -L --max-time 10 "$URL" > "$T/raw/curl_home.html"
```

ถ้ามี nikto:

```bash
nikto -nointeractive -ask no -Tuning b -host "$URL" > "$T/raw/nikto.stdout" 2>&1
```

ถ้ามี nuclei และมี template เฉพาะที่ไม่ aggressive:

```bash
nuclei -u "$URL" -severity low,medium,high,critical -jsonl -o "$T/raw/nuclei.jsonl"
```

ถ้า nuclei ใช้นานมากหรือ template ไม่พร้อม ให้ข้ามและจดว่า skipped

## Target-specific evidence

### 1. Spring: `spring_CVE-2022-22965`

ปัญหาปัจจุบัน:

- ML เห็นแค่ port 8080/Tomcat/generic HTTP
- ยังไม่มีหลักฐานที่บอก Spring ชัดพอ

ให้เก็บ:

```bash
curl -k -i --max-time 10 "$URL/actuator" > "$T/raw/spring_actuator.txt"
curl -k -i --max-time 10 "$URL/actuator/env" > "$T/raw/spring_actuator_env.txt"
curl -k -i --max-time 10 "$URL/actuator/health" > "$T/raw/spring_actuator_health.txt"
curl -k -i --max-time 10 "$URL/error" > "$T/raw/spring_error.txt"
```

สิ่งที่ถือว่าเป็น evidence ดี:

- มีคำว่า `spring`
- มี actuator endpoint
- มี Whitelabel Error Page
- header/body/error ที่บอก Spring Boot หรือ framework
- safe PoC response เฉพาะ CVE โดยไม่เขียนไฟล์

ถ้าไม่มีสิ่งเหล่านี้ แต่ service เปิดอยู่ ให้ mark เป็น `inconclusive`

ห้าม:

- เขียน webshell
- แก้ JSP/classpath/file system
- ใช้ payload ที่เปลี่ยน state ของ container

### 2. Shiro: `shiro_CVE-2016-4437`

ปัญหาปัจจุบัน:

- ML เห็นแค่ Login Page กับ port 8080
- ยังแยกจาก web app อื่นไม่ได้

ให้เก็บ:

```bash
curl -k -i --max-time 10 "$URL" > "$T/raw/shiro_home.txt"
curl -k -i --max-time 10 "$URL/login" > "$T/raw/shiro_login.txt"
curl -k -i --max-time 10 -H "Cookie: rememberMe=dec-validation" "$URL" > "$T/raw/shiro_rememberme_cookie_probe.txt"
curl -k -i --max-time 10 "$URL/;JSESSIONID=dec-validation" > "$T/raw/shiro_jsessionid_probe.txt"
```

สิ่งที่ถือว่าเป็น evidence ดี:

- `rememberMe`
- `Set-Cookie`
- `JSESSIONID`
- error/header/body ที่บอก Apache Shiro
- behavior ที่สัมพันธ์กับ Shiro cookie โดยไม่ brute force key

ห้าม:

- brute force Shiro rememberMe key
- ใช้ gadget chain ที่ execute command
- ยิง payload RCE

ถ้าเจอแค่ login page และไม่มี Shiro fingerprint ให้ mark เป็น `inconclusive`

### 3. GoAhead: `goahead_CVE-2017-17562`

ปัญหาปัจจุบัน:

- ML เห็น Home Page + port 8080
- family อื่นที่ใช้ 8080 ชนกันเยอะ

ให้เก็บ:

```bash
curl -k -i --max-time 10 "$URL/" > "$T/raw/goahead_home.txt"
curl -k -i --max-time 10 "$URL/admin" > "$T/raw/goahead_admin.txt"
curl -k -i --max-time 10 "$URL/status" > "$T/raw/goahead_status.txt"
curl -k -i --max-time 10 "$URL/goform/status" > "$T/raw/goahead_goform_status.txt"
nmap -sV -Pn -p "$PORT" "$HOST" -oN "$T/raw/goahead_nmap.stdout" -oX "$T/raw/goahead_nmap.xml"
```

สิ่งที่ถือว่าเป็น evidence ดี:

- `GoAhead`
- `GoAhead-Webs`
- server banner/path ที่บอก GoAhead
- response shape ที่เฉพาะ GoAhead

ถ้าไม่มี banner เฉพาะ ให้ mark เป็น `inconclusive`

### 4. Joomla regression guard: `joomla_CVE-2023-23752`

รอบ ML ล่าสุด Joomla ดีขึ้นแล้ว ใช้ target นี้เช็กว่า pipeline ใหม่ไม่ทำให้ regression

ให้เก็บ:

```bash
curl -k -i --max-time 10 "$URL" > "$T/raw/joomla_home.txt"
curl -k -i --max-time 10 "$URL/api/index.php/v1/config/application?public=true" > "$T/raw/joomla_public_config_probe.json"
curl -k -i --max-time 10 "$URL/administrator/manifests/files/joomla.xml" > "$T/raw/joomla_manifest.xml"
```

evidence ดี:

- `Joomla`
- `api/index.php`
- public config response
- Joomla manifest/version

### 5. Redis positive control: `redis_CVE-2022-0543`

ให้เก็บแบบอ่านอย่างเดียว:

```bash
nmap -sV -Pn -p "$PORT" "$HOST" -oN "$T/raw/redis_nmap.stdout" -oX "$T/raw/redis_nmap.xml"
printf 'INFO\r\n' | nc -w 5 "$HOST" "$PORT" > "$T/raw/redis_info.txt"
```

ห้าม:

- `CONFIG SET`
- `SAVE`
- เขียน key ใหม่
- flush/delete data

### 6. Aria2 positive control: `aria2_rce`

ให้เก็บ version/info:

```bash
nmap -sV -Pn -p "$PORT" "$HOST" -oN "$T/raw/aria2_nmap.stdout" -oX "$T/raw/aria2_nmap.xml"
printf '{"jsonrpc":"2.0","id":"dec","method":"aria2.getVersion"}\n' | nc -w 5 "$HOST" "$PORT" > "$T/raw/aria2_get_version.txt"
```

ห้าม addUri หรือสั่ง download

### 7. Grafana positive control

ให้เก็บ:

```bash
curl -k -i --max-time 10 "$URL/login" > "$T/raw/grafana_login.txt"
curl -k -i --max-time 10 "$URL/api/health" > "$T/raw/grafana_api_health.txt"
```

evidence ดี:

- `Grafana`
- `/login`
- `/api/health`

### 8. Tomcat positive control

ให้เก็บ:

```bash
curl -k -i --max-time 10 "$URL" > "$T/raw/tomcat_home.txt"
curl -k -i --max-time 10 "$URL/docs/" > "$T/raw/tomcat_docs.txt"
curl -k -i --max-time 10 "$URL/manager/html" > "$T/raw/tomcat_manager.txt"
```

ห้าม PUT/เขียนไฟล์ ถ้าไม่จำเป็น

### 9. Nginx positive control

ให้เก็บ:

```bash
curl -k -i --max-time 10 "$URL" > "$T/raw/nginx_home.txt"
nmap -sV -Pn -p "$PORT" "$HOST" -oN "$T/raw/nginx_nmap.stdout" -oX "$T/raw/nginx_nmap.xml"
```

evidence ดี:

- `Server: nginx`
- nmap service nginx

## การเขียน validation-results.jsonl

ไฟล์:

```text
/home/kali/reports/dec-validation-manual/validation-results.jsonl
```

ต้องเป็น JSONL: 1 target ต่อ 1 บรรทัด

schema ต่อ record:

```json
{
  "target_id": "spring_CVE-2022-22965",
  "weak_label": "spring",
  "validation_status": "inconclusive",
  "confidence": "low",
  "evidence_summary": "พบ HTTP/Tomcat บน port 8080 แต่ยังไม่พบ actuator หรือ Spring-specific fingerprint",
  "evidence_files": [
    "raw-curated/spring_CVE-2022-22965/raw/nmap.stdout",
    "raw-curated/spring_CVE-2022-22965/raw/spring_actuator.txt"
  ],
  "tools_used": ["nmap", "curl"],
  "safe_poc_used": false,
  "destructive_action": false,
  "notes": "local Vulhub/Docker lab only"
}
```

ค่า `validation_status`:

- `validated_positive`: มีหลักฐานชัดว่าตรง weak_label/family
- `validated_negative`: หลักฐานชัดว่าคนละ family หรือ label เดิมผิด
- `inconclusive`: สแกนแล้วแต่ยังยืนยันไม่ได้
- `not_run`: ไม่ได้รัน target นี้

ค่า `confidence`:

- `high`: มี safe PoC/response เฉพาะ CVE ชัด
- `medium`: มี fingerprint เฉพาะ family ชัด
- `low`: มีแค่ banner/title/port/basic response
- `none`: ไม่ได้รันหรือไม่มี evidence

`destructive_action` ต้องเป็น `false` เสมอ ถ้าจำเป็นต้องทำอะไร destructive ให้หยุดและถามก่อน

## การเขียน SCAN-SUMMARY-TH.md

ไฟล์:

```text
/home/kali/reports/dec-validation-manual/SCAN-SUMMARY-TH.md
```

ให้สรุปภาษาไทย:

- วันเวลา run
- target ที่รัน
- target ที่ `validated_positive`
- target ที่ `inconclusive`
- target ที่ `not_run`
- tool ที่ใช้
- evidence สำคัญอยู่ไฟล์ไหน
- target ไหนต้องสแกนเพิ่มรอบต่อไป
- มีปัญหาอะไร เช่น tool missing, lab เปิดไม่ได้, port ไม่ตรง

## สิ่งที่ห้ามเก็บเข้า raw-curated

ห้าม copy:

- `.zaphome`
- cache/runtime/dependency
- chromedriver
- `.jar` dependency
- `__pycache__`
- `.pyc`
- AutoRecon raw path ยาว ๆ
- log ใหญ่ที่ไม่มีผล scan
- downloaded payload/tool binary

เก็บเฉพาะ:

- `.txt`
- `.stdout`
- `.xml`
- `.json`
- `.jsonl`
- `.html`
- `.md` summary

ที่เป็นผลจาก scanner/probe จริง

## Copy ผลกลับ shared folder

หลังเสร็จ:

```bash
mkdir -p /media/sf_kali-share/dataset/dec-validation-manual
cp -a /home/kali/reports/dec-validation-manual/. /media/sf_kali-share/dataset/dec-validation-manual/
```

ตรวจว่า shared folder มีไฟล์:

```bash
ls -lah /media/sf_kali-share/dataset/dec-validation-manual
test -f /media/sf_kali-share/dataset/dec-validation-manual/validation-results.jsonl && echo OK_JSONL
test -f /media/sf_kali-share/dataset/dec-validation-manual/SCAN-SUMMARY-TH.md && echo OK_SUMMARY
find /media/sf_kali-share/dataset/dec-validation-manual/raw-curated -type f | head -50
```

## เกณฑ์สำเร็จ

ถือว่าสำเร็จเมื่อ:

- มี `validation-results.jsonl`
- JSONL parse ได้ทุกบรรทัด
- ทุก target ที่ไม่ใช่ `not_run` มี evidence_files ที่มีไฟล์จริง
- มี `SCAN-SUMMARY-TH.md`
- raw-curated ไม่มี cache/runtime/dependency
- ไม่มี public target ใน log
- copy ผลกลับ `/media/sf_kali-share/dataset/dec-validation-manual` แล้ว

## รายงานสุดท้ายที่ต้องตอบกลับ

ตอบเป็นภาษาไทย:

```text
สแกนเสร็จแล้ว

Kali output:
/home/kali/reports/dec-validation-manual

Shared output:
/media/sf_kali-share/dataset/dec-validation-manual

สรุป:
- validated_positive: ...
- inconclusive: ...
- not_run: ...

target ที่ควรสแกนเพิ่มรอบถัดไป:
- ...

ปัญหาที่พบ:
- ...
```

