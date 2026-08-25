# Dec Kali Validation Runbook

เอกสารนี้คือวิธีใช้ Kali เพื่อตรวจว่า ML ของ Dec เรียงลำดับ candidate family ได้ถูกไหม โดยอิงจากผล scan จริงใน local Vulhub/Docker lab

## ใช้กับอะไร

ใช้กับชุด:

```text
experiments/dec-ml-scan-2026-08-25
```

ไฟล์ที่สำคัญ:

- `features.csv`: URL/port/fingerprint ที่ scanner เก็บมาแล้ว
- `validation-target-queue.csv`: target ที่ควร validate ก่อน
- `derived/attack-order-top5.csv`: ลำดับ family ที่ ML แนะนำ
- `scripts/kali/dec_validation_runner.py`: runner ฝั่ง Kali สำหรับเก็บ evidence แบบปลอดภัย

## ขอบเขตที่อนุญาต

รันเฉพาะ local lab ที่ผู้ใช้ควบคุมเอง:

- `127.0.0.1`
- Docker/Vulhub container บน Kali
- `/home/kali/reports`
- `/media/sf_kali-share/dataset`

ห้ามสแกน public IP/domain ภายนอก และห้ามใช้ destructive exploit

## วิธีรันแบบเร็ว

ใน Kali ให้เข้าโฟลเดอร์ run-kit:

```bash
cd /media/sf_kali-share/dataset/dec-kali-validation-run-kit
python3 scripts/kali/dec_validation_runner.py \
  --queue validation-target-queue.csv \
  --features features.csv \
  --output-dir /home/kali/reports/dec-validation-manual
```

จากนั้น copy ผลกลับ shared folder:

```bash
mkdir -p /media/sf_kali-share/dataset/dec-validation-manual
cp -a /home/kali/reports/dec-validation-manual/. /media/sf_kali-share/dataset/dec-validation-manual/
```

ไฟล์ที่ Codex ฝั่ง Windows ต้องเอากลับเข้า repo คือ:

```text
validation-results.jsonl
raw-curated/
SCAN-SUMMARY-TH.md
```

## Runner ทำอะไร

ต่อ target หนึ่งตัว runner จะ:

1. อ่าน `target_id`, `weak_label`, URL และ port
2. รัน `nmap -sV -Pn` เฉพาะ port ของ local target
3. ถ้าเป็น HTTP จะเก็บ header/body ด้วย `curl` หรือ Python fallback
4. รัน safe probe ตาม family เช่น Joomla API path, Grafana login, Spring actuator, Redis INFO, Aria2 getVersion
5. ถ้ามี `nikto` จะรันแบบ non-interactive เพิ่ม
6. เขียน `validation-results.jsonl` ตาม schema

ผลลัพธ์ที่เป็นไปได้:

- `validated_positive`: evidence มี fingerprint/probe ตรงกับ expected family
- `validated_negative`: ยังไม่ใช้ใน runner อัตโนมัติ ต้องให้คนตรวจ evidence ก่อน
- `inconclusive`: มีหลักฐาน แต่ยังไม่พอยืนยัน
- `not_run`: ไม่มี service/evidence ที่อ่านได้

## ทำไมยังต้องให้คนดู

runner นี้ออกแบบให้ปลอดภัยและเก็บ evidence ก่อน ไม่ใช่ exploit engine เต็มรูปแบบ ดังนั้นเคสยากอย่าง Spring4Shell, Shiro, Joomla บาง lab อาจได้ `inconclusive` แม้ target จะถูกจริง

จุดที่ควรให้ opencode/คนตรวจเพิ่ม:

- `joomla_CVE-2023-23752`: ต้องดู API/config response ว่าตรง CVE จริงไหม
- `spring_CVE-2022-22965`: ต้องดู framework evidence และ safe PoC ที่ไม่เขียนไฟล์
- `shiro_CVE-2016-4437`: ต้องดู cookie/header/login flow
- `goahead_CVE-2017-17562`: ต้องดู server banner/path เฉพาะ GoAhead

## เอาผลกลับเข้า ML

เมื่อได้ `validation-results.jsonl` แล้ว ให้รันบน Windows/repo:

```powershell
python scripts\import_dec_validation_results.py --input path\to\validation-results.jsonl
python scripts\evaluate_dec_ml_scan_20260825.py --label-mode merged
python scripts\export_dec_attack_order.py --prediction-file experiments\dec-ml-scan-2026-08-25\reports\dec-ml-scan-ranking-merged-predictions.json --suffix merged --top-k 5
python scripts\validate_dec_artifacts.py
```

ถ้า metrics ดีขึ้น แปลว่า validation label ช่วย ML ได้จริง ถ้าแย่ลง ให้ดู failure report ว่า weak label เดิมผิด หรือ feature ยังไม่พอแยก family
