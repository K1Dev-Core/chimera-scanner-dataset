# สรุป Import รอบ dec-tool-scope-2569-08-26-0058

## Input

ผล scan จาก Kali:

```text
C:\Users\rapii\Desktop\kali-share\dataset\dec-tool-scope-2569-08-26-0058
```

Kali output:

```text
/home/kali/reports/dec-tool-scope-2569-08-26-0058
```

Shared output:

```text
/media/sf_kali-share/dataset/dec-tool-scope-2569-08-26-0058
```

## ผลที่ได้

- scanned targets: 5
- validated_positive: 4
- inconclusive: 1
- not_run: 0
- validated_negative: 0

Target ที่ validated:

- `grafana_CVE-2021-43798`
- `aria2_rce`
- `joomla_CVE-2023-23752`
- `redis_CVE-2022-0543`

Target ที่ยัง inconclusive:

- `spring_CVE-2022-22965`

## Tool run count จริง

- `naabu`: 5
- `httpx-toolkit`: 5
- `nuclei`: 4
- `nikto`: 3
- `curl`: 5
- `manual_poc`: 1
- `nmap`: 0
- `wapiti`: 0
- `zaproxy`: 0
- `metasploit`: 0
- `sqlmap`: 0

## ข้อสังเกตจาก Codex

- รอบนี้ timebox ใน summary เป็น 10 นาที ไม่ใช่ 1 ชั่วโมง จึงยังถือว่าเป็น quick tool-scope smoke run
- `nmap` ถูก skip เพราะ raw socket permission แต่รอบถัดไปควรลอง `nmap -sT -sV -Pn` ก่อน ถ้าไม่ได้จริงค่อย fallback เป็น skip
- `zaproxy` ยัง skip ได้ เพราะไม่ได้ติดตั้งและไม่ควรเสียเวลาติดตั้งในรอบสั้น
- `metasploit` ยังไม่ได้ใช้ ทั้งที่เป็น core validation engine ของโปรเจกต์ ควรเพิ่มในรอบถัดไปกับ target ที่เหมาะ
- graph มี edge ของ Spring ที่ชี้ `SUPPORTS_FAMILY spring` จาก Tomcat evidence แต่ status ยัง `inconclusive` จึงควรใช้ข้อความแบบ uncertainty มากกว่า support เต็มในรอบถัดไป

## ผลต่อ ML

หลัง import รอบนี้และ merge กับ validation รอบก่อน:

- validated label rows: 9
- validated_positive: 8
- inconclusive: 1
- merged Top-1: `0.931`
- merged ML Top-3: `0.966`
- merged ML mean attempts: `1.172`
- merged heuristic Top-3: `1.000`
- failure report: `appweb_CVE-2018-8715`

ผล heuristic ยังแข็ง แต่ ML logistic มี failure ใหม่ 1 ตัวหลัง GoAhead evidence แข็งขึ้น คือ `appweb_CVE-2018-8715` เพราะ AppWeb ยังไม่มี fingerprint เฉพาะพอแยกจากเว็บ port 8080

## งานรอบถัดไปสำหรับ opencode

โฟกัส:

1. `shiro_CVE-2016-4437`
2. `goahead_CVE-2017-17562`
3. `tomcat_CVE-2017-12615`
4. `nginx_CVE-2017-7529`
5. `spring_CVE-2022-22965`
6. `appweb_CVE-2018-8715`

ข้อกำหนด:

- ใช้ `nmap -sT -sV -Pn` ก่อน mark nmap failed
- ใช้ Metasploit search/info/check กับ target ที่เหมาะ เช่น Tomcat, Shiro, GoAhead, Spring โดยห้าม destructive payload
- ถ้า Metasploit ไม่มี safe check ให้เก็บ `metasploit_search.txt` และ `metasploit_module_info.txt` แล้ว mark `inconclusive`
- อย่าใช้ `sqlmap` ถ้าไม่มี parameter หรือ SQLi signal ชัด
- ถ้าเขียน graph ให้แยก signal ที่ `validated_positive` กับ `inconclusive` ให้ชัด
- เพิ่ม AppWeb-specific scan เช่น banner/header/error/default page เพื่อลดการสับสนกับ GoAhead
