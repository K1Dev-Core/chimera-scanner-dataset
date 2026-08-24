# Prompt สำหรับ opencode ฝั่ง Kali: Dec ML Validation Queue

ใช้ prompt นี้กับ opencode ใน Kali เพื่อทำ validation รอบถัดไปของโปรเจกต์ `chimera-scanner-dataset` branch `Dec`

## ขอบเขตความปลอดภัย

ทำเฉพาะ local lab/Vulhub/Docker ที่ผู้ใช้ควบคุมอยู่เท่านั้น

อนุญาตเป้าหมาย:

- `127.0.0.1`
- container/service ที่เปิดจาก Vulhub บนเครื่อง Kali
- shared folder `/media/sf_kali-share/dataset`
- output folder `/home/kali/reports`

ห้าม:

- สแกน public IP/domain ภายนอก
- brute force credential
- ทำ persistence
- ทำลายข้อมูลใน container
- เก็บ cache/runtime/dependency ขึ้น dataset

เป้าหมายของงานนี้คือเก็บหลักฐานเพื่อปรับ ML dataset ไม่ใช่โจมตีระบบจริง

## เป้าหมายหลัก

เรามี ML ranking จากชุด `dec-ml-scan-2026-08-25` แล้ว แต่ยังใช้ weak label จากชื่อ Vulhub lab

งานของคุณคือ validate target ตาม queue นี้ แล้วสร้างผลลัพธ์เป็น raw-curated + validation JSONL ที่ Codex ฝั่ง Windows เอากลับเข้า repo ได้

queue อยู่ที่:

```text
experiments/dec-ml-scan-2026-08-25/validation-target-queue.csv
```

ถ้าไม่มีไฟล์นี้ใน Kali ให้สร้าง queue ตามนี้:

```csv
priority,target_id,weak_label,ml_positive_rank,queue_type
1,joomla_CVE-2023-23752,joomla,17,hard_failure
2,spring_CVE-2022-22965,spring,13,hard_failure
3,shiro_CVE-2016-4437,shiro,12,hard_failure
4,goahead_CVE-2017-17562,goahead,4,near_miss
5,redis_CVE-2022-0543,redis,1,positive_control
6,aria2_rce,aria2,1,positive_control
7,grafana_CVE-2021-43798,grafana,1,positive_control
8,tomcat_CVE-2017-12615,tomcat,1,positive_control
9,nginx_CVE-2017-7529,nginx,1,positive_control
```

## Output ที่ต้องสร้าง

สร้าง run folder:

```bash
RUN_ID="dec-validation-$(date +%F-%H%M)"
OUT="/home/kali/reports/$RUN_ID"
mkdir -p "$OUT"/{raw-curated,derived,logs}
```

ถ้ามี shared folder:

```bash
SHARED="/media/sf_kali-share/dataset/$RUN_ID"
mkdir -p "$SHARED"
```

ไฟล์ที่ต้องมี:

```text
$OUT/SCAN-SUMMARY-TH.md
$OUT/validation-results.jsonl
$OUT/derived/validation-labels.csv
$OUT/logs/run.log
$OUT/raw-curated/<target_id>/...
```

จากนั้น copy ไป shared folder:

```bash
cp -a "$OUT"/. "$SHARED"/
```

## Schema ของ validation-results.jsonl

เขียน 1 JSON object ต่อ 1 target:

```json
{
  "target_id": "joomla_CVE-2023-23752",
  "weak_label": "joomla",
  "validation_status": "validated_positive",
  "confidence": "medium",
  "evidence_summary": "พบ public config API response ที่ตรงกับ Joomla CVE-2023-23752",
  "evidence_files": [
    "raw-curated/joomla_CVE-2023-23752/raw/curl_headers.txt",
    "raw-curated/joomla_CVE-2023-23752/raw/joomla_public_config_probe.json"
  ],
  "tools_used": ["curl", "nmap", "nikto", "wapiti"],
  "safe_poc_used": true,
  "destructive_action": false,
  "notes": "เป็น local Vulhub lab เท่านั้น"
}
```

ค่า `validation_status` ที่ใช้ได้:

- `validated_positive`: มี evidence ชัดว่าตรง expected family/CVE
- `validated_negative`: evidence ไม่สนับสนุน weak label
- `inconclusive`: สแกนแล้วแต่ยังยืนยันไม่ได้
- `not_run`: ยังไม่ได้รัน

ค่า `confidence`:

- `high`: มี safe PoC/expected response เฉพาะ CVE
- `medium`: fingerprint และ endpoint เฉพาะ family ชัด แต่ยังไม่มี exploit proof
- `low`: มีแค่ banner/title/port

## วิธีทำต่อ target

สำหรับแต่ละ target:

1. เปิด Vulhub lab ของ target นั้นเท่านั้น
2. ตรวจ port ด้วย `docker ps`, `ss -ltnp`, หรือ compose output
3. เก็บ nmap:

```bash
nmap -sV -oX "$T/raw/nmap.xml" -oN "$T/raw/nmap.stdout" "$HOST" -p "$PORT"
```

4. ถ้าเป็น HTTP/HTTPS ให้เก็บ:

```bash
curl -k -i --max-time 10 "$URL" > "$T/raw/curl_headers.txt"
curl -k -L --max-time 10 "$URL" > "$T/raw/curl_home.html"
```

5. เก็บ probe เฉพาะ family ที่ต้อง validate เช่น:

- Joomla: config/API endpoint ที่เกี่ยวกับ CVE-2023-23752
- Spring: header/path ที่บอก Spring และ safe check สำหรับ CVE-2022-22965
- Shiro: cookie/header/login evidence ที่บอก Apache Shiro
- GoAhead: server banner/path ที่บอก GoAhead
- Redis: nmap/banner/INFO แบบไม่แก้ข้อมูล
- Aria2: JSON-RPC version/system info แบบปลอดภัย
- Grafana: title/header/path traversal safe indicator
- Tomcat: title/version/PUT behavior แบบไม่เขียนไฟล์ถ้าไม่จำเป็น
- Nginx: header/version/range behavior แบบปลอดภัย

6. เขียน `validation-results.jsonl`
7. ปิด container ก่อน target ถัดไป เพื่อลด load

## เครื่องมือที่ควรใช้

ใช้เท่าที่มี ถ้าไม่มีให้ข้ามและจดใน summary:

- `nmap`
- `curl`
- `nikto`
- `wapiti`
- `nuclei`
- `jq`
- `python3`

อย่าติดตั้ง dependency ใหญ่ถ้าไม่จำเป็นในรอบนี้ เป้าหมายคือ validate queue ไม่ใช่ setup ทั้ง Kali ใหม่

## สิ่งที่ต้องเขียนใน SCAN-SUMMARY-TH.md

ให้สรุปเป็นภาษาไทย:

- run id
- วันที่
- target ที่รัน
- target ที่ validate positive/negative/inconclusive
- tool ที่ใช้
- target ที่ยังขาด evidence
- path ของ `validation-results.jsonl`
- คำเตือนว่าเป็น local lab เท่านั้น

## เกณฑ์สำเร็จ

งานรอบนี้สำเร็จเมื่อ:

- มี `validation-results.jsonl` parse ได้ทุกบรรทัด
- มี evidence_files ที่มีไฟล์จริงสำหรับทุก target ที่ไม่ใช่ `not_run`
- ไม่มี cache/runtime/dependency ใน raw-curated
- ไม่มี public target ใน log
- copy ผลลัพธ์ไป shared folder แล้ว

หลังจบให้รายงาน path:

```text
Kali output: /home/kali/reports/<RUN_ID>
Shared output: /media/sf_kali-share/dataset/<RUN_ID>
```
