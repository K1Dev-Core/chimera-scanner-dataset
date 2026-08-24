# DEC Update Checklist 2026-08-06

ไฟล์นี้สรุปว่าหลังได้ dataset batch ใหม่ 22 targets แล้ว มีอะไรที่ต้องอัปเดตต่อบ้าง

## สถานะล่าสุด

มี dataset ใหม่จาก Kali:

```text
C:\Users\rapii\Desktop\kali-share\dataset\dec-vulhub-2026-08-05
```

แต่ source batch นี้มี schema issue:

- `records/findings.jsonl` ใช้ `record_type=observation`
- `records/observations.jsonl` มี finding ปนซ้ำ
- `records/all-records.jsonl` รวม records ไม่ครบ

จึงสร้าง fixed copy แล้ว:

```text
C:\Users\rapii\Documents\Codex\2026-08-03\faraday-https-github-com-infobyte-faraday\work\dec-vulhub-2026-08-05-fixed
```

## Fixed Dataset Summary

| Item | Count |
|---|---:|
| Targets | 22 |
| Observations | 565 |
| Findings | 1211 |
| Validations | 41 |
| Tool runs | 195 |
| All records | 2034 |
| Labels | 198 |
| Duplicate record IDs | 0 |
| Quality valid | true |

## ไฟล์ที่อัปเดตแล้วใน workspace

- `outputs/DEC-CURRENT-STATUS.md`
- `outputs/dec-feature-and-tool-recommendations-th.md`
- `outputs/DEC-FAST-SUBAGENT-DATASET-PROMPT.md`
- `outputs/DEC-UPDATE-CHECKLIST-2026-08-06.md`

ลบไฟล์ `outputs/hex-vs-dec-dataset-analysis-th.md` แล้ว เพราะ Hex และ Dec ต้องใช้ schema/แนวคิดร่วมกัน ไม่ควรมีเอกสารเปรียบเทียบแยกเป็น final reference

## สิ่งที่ควรอัปเดตต่อ

1. Copy fixed dataset ไป shared folder:

```powershell
Copy-Item -Recurse -Force `
  "C:\Users\rapii\Documents\Codex\2026-08-03\faraday-https-github-com-infobyte-faraday\work\dec-vulhub-2026-08-05-fixed" `
  "C:\Users\rapii\Desktop\kali-share\dataset\dec-vulhub-2026-08-05-fixed"
```

2. อัป fixed dataset ขึ้น Git branch `Dec` เป็น generated artifact ใหม่

แนะนำ path:

```text
generated/dec-vulhub-2026-08-05-fixed/
```

3. อัป README index ให้ชี้ไฟล์หลัก:

```text
DEC-CURRENT-STATUS.md
dec-feature-and-tool-recommendations-th.md
tool-study-article-th.md
generated/dec-vulhub-2026-08-05-fixed/
```

4. อัปหรือสร้าง builder รุ่นใหม่:

```text
build_dec_dataset_v3.py
```

หน้าที่ builder รุ่นใหม่:

- ingest `dec-vulhub-2026-08-05`
- fix `record_type`
- deduplicate observations/findings
- rebuild `all-records.jsonl`
- rebuild `manifest.json`
- rebuild `quality-report.json`
- rebuild `checksums.sha256`

5. สร้าง data dictionary สั้น ๆ:

```text
docs/dec-data-dictionary-th.md
```

ควรอธิบายคำเหล่านี้:

- target
- observation
- finding
- validation
- tool_run
- candidate
- label
- raw
- normalized
- derived

6. ทำ baseline demo:

- train/test split แบบ grouped by target หรือ product family
- ใช้ `target-candidate-features.json`
- ใช้ `target-candidate-labels.jsonl`
- เริ่มจาก RandomForest หรือ XGBoost ก่อน Deep Learning

7. เพิ่ม OpenVAS export ถ้าต้องการ coverage เพิ่ม

OpenVAS ยังไม่มี output ใน fixed dataset นี้

## ห้ามทำ

- ห้ามใช้ source batch เดิมเป็น final โดยไม่แก้ schema
- ห้ามตีความ `finding` ว่า exploit สำเร็จ
- ห้ามเอา label/ground truth เข้า feature matrix
- ห้ามสุ่ม split เป็นรายแถว เพราะ candidate ของ target เดียวกันจะรั่วข้าม train/test

## คำอธิบายสั้นที่สุด

ตอนนี้ dataset ดีพอสำหรับ demo แรกแล้ว แต่ต้องใช้ตัว `dec-vulhub-2026-08-05-fixed` เป็นหลัก และงานต่อไปคือทำให้ fixed dataset นี้ reproducible ด้วย builder แล้วอัปขึ้น Git


## Update 2026-08-25

มี fixed core package ล่าสุดแล้ว:

```text
C:\Users\rapii\Documents\Codex\2026-08-03\faraday-https-github-com-infobyte-faraday\work\dec-vulhub-2026-08-24-fixed-core-v2
```

สรุป: targets=43, observations=704, findings=2046, validations=92, tool_runs=381, all_records=3266, target-candidate rows=602, quality.valid=true

สิ่งที่ต้องอัป Git ตอนนี้คือ docs ล่าสุดและ `generated/dec-vulhub-2026-08-24-fixed-core/` แบบ core artifacts ไม่รวม raw 550 MB
