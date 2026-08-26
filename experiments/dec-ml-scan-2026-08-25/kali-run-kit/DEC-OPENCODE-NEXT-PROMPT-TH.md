# Prompt ส่งให้ opencode ฝั่ง Kali

ทำงานโปรเจกต์ Dec / chimera-scanner-dataset ฝั่ง Kali ต่อให้หน่อย

## ขอบเขต

- ทำเฉพาะ local Vulhub/Docker lab ที่อยู่บน Kali เท่านั้น
- ห้ามสแกน public IP/domain ภายนอก
- ห้าม brute force, persistence, destructive exploit
- เป้าหมายคือเก็บ evidence เพื่อปรับ ML ranking ไม่ใช่โจมตีระบบจริง

## เริ่มงาน

```bash
cd /media/sf_kali-share/dataset/dec-kali-validation-run-kit

python3 scripts/kali/dec_validation_runner.py \
  --queue validation-target-queue.csv \
  --features features.csv \
  --output-dir /home/kali/reports/dec-validation-manual
```

## Target ที่ต้องโฟกัส

1. `spring_CVE-2022-22965`
   - เก็บ `/actuator`, `/actuator/env`, `/actuator/health`, `/error`
   - เก็บ headers, title, framework error page, nmap service
   - ถ้ามี safe PoC ที่ไม่เขียนไฟล์/ไม่ทำลายข้อมูล ค่อยใช้

2. `shiro_CVE-2016-4437`
   - เก็บ login route, `Set-Cookie`, `rememberMe`, `JSESSIONID`
   - เก็บ header/error ที่บอก Apache Shiro
   - ห้าม brute force หรือเดา key

3. `goahead_CVE-2017-17562`
   - เก็บ server banner, nmap service
   - probe path: `/`, `/admin`, `/status`, `/goform/status`
   - ต้องการหลักฐานว่าเป็น GoAhead ไม่ใช่ generic web port 8080

## Target ตัวคุม

- `joomla_CVE-2023-23752` เป็น regression guard
- `redis_CVE-2022-0543`, `aria2_rce`, `grafana_CVE-2021-43798`, `tomcat_CVE-2017-12615`, `nginx_CVE-2017-7529` เป็น positive control

## Output ที่ต้องมี

```text
/home/kali/reports/dec-validation-manual/validation-results.jsonl
/home/kali/reports/dec-validation-manual/SCAN-SUMMARY-TH.md
/home/kali/reports/dec-validation-manual/raw-curated/<target_id>/raw/*
```

`validation-results.jsonl` ต้องเป็น JSONL 1 target ต่อ 1 บรรทัด และมี field:

```text
target_id, weak_label, validation_status, confidence, evidence_summary,
evidence_files, tools_used, safe_poc_used, destructive_action, notes
```

ค่า `validation_status`:

- `validated_positive`: evidence ชัดว่าตรง family/CVE
- `inconclusive`: มีหลักฐานแต่ยังยืนยันไม่ได้
- `not_run`: ยังไม่ได้รัน
- `validated_negative`: evidence ขัดกับ weak label

ค่า `confidence`:

- `high`: มี safe PoC หรือ response เฉพาะ CVE ชัด
- `medium`: fingerprint family ชัด
- `low`: มีแค่ banner/title/port
- `none`: ไม่ได้รันหรือไม่มี evidence

## ห้ามเก็บเข้า raw-curated

- cache/runtime/dependency
- `.zaphome`
- `chromedriver`
- `*.jar` dependency
- `__pycache__`
- `*.pyc`
- AutoRecon raw path ยาว ๆ

## Copy ผลกลับ shared folder

```bash
mkdir -p /media/sf_kali-share/dataset/dec-validation-manual
cp -a /home/kali/reports/dec-validation-manual/. /media/sf_kali-share/dataset/dec-validation-manual/
```

## สรุปหลังจบ

เขียนสรุปภาษาไทย:

- รัน target ไหนบ้าง
- target ไหน `validated_positive` / `inconclusive` / `not_run`
- ใช้ tool อะไร
- evidence สำคัญอยู่ไฟล์ไหน
- path output คืออะไร

