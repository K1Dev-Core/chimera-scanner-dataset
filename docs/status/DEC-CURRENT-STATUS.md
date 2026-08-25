# Dec Dataset: สถานะล่าสุดและ Handoff

อัปเดตล่าสุด: 2026-08-25  
Repository: `K1Dev-Core/chimera-scanner-dataset`  
Branch ที่ถูกต้อง: `Dec` เท่านั้น  
ขอบเขตการทดสอบ: local Vulhub/Kali/Docker labs ที่ได้รับอนุญาตเท่านั้น

## อ่านเร็วที่สุด

ถ้าเริ่ม session ใหม่ ให้ทำตามนี้:

1. อยู่ที่ branch `Dec` เท่านั้น
2. ตรวจ `git status -sb`
3. อย่า stage/commit `dataset/raw/autorecon/**` เพราะ Windows มีปัญหา path ยาว
4. ใช้ dataset หลักที่ `generated/dec-vulhub-2026-08-24-fixed-core/`
5. ใช้ผล scan/ML ล่าสุดที่ `experiments/dec-ml-scan-2026-08-25/`
6. ใช้ prompt Kali ล่าสุดที่ `docs/prompts/DEC-KALI-VALIDATION-QUEUE-PROMPT-TH.md`
7. ถ้าจะให้ Kali/opencode รันต่อทันที ใช้ bundle ที่ `experiments/dec-ml-scan-2026-08-25/kali-run-kit/`

## สถานะ Git ล่าสุด

remote `refs/heads/Dec` ล่าสุดที่ยืนยันแล้ว:

```text
9ba433bad57e904976194fcb1f6ea5a303a6cc17
```

commit ล่าสุด:

```text
9ba433b Add Dec Hex next scan queue
dd6ed16 Add Dec Hex target shortlist
1f26ea8 Add Dec Kali validation run kit
1a25640 Add Dec ML attack order export
ce27345 Add Dec validation label fixture checks
```

working tree ยังมี unstaged deletion ของ `dataset/raw/autorecon/2026-08-04/...` จากปัญหา path ยาวบน Windows ให้ปล่อยไว้ก่อนและอย่า commit

## Dataset หลัก

ชุดหลักของ Dec ตอนนี้:

```text
generated/dec-vulhub-2026-08-24-fixed-core/
```

สรุป:

| รายการ | จำนวน |
| --- | ---: |
| targets | 43 |
| observations | 704 |
| findings | 2046 |
| validations | 92 |
| tool_runs | 381 |
| all_records | 3266 |
| target-candidate rows | 602 |
| quality.valid | true |

ไฟล์สำคัญ:

- `records/targets.jsonl`
- `records/findings.jsonl`
- `records/observations.jsonl`
- `records/validations.jsonl`
- `derived/target-features.json`
- `derived/target-candidate-features.json`
- `labels/target-candidate-labels.jsonl`
- `reports/dec-ml-ranking-report-th.md`
- `reports/dec-ml-feature-ablation.json`

## ชุด scan ล่าสุดจาก Kali

ชุดทดลองใหม่:

```text
experiments/dec-ml-scan-2026-08-25/
dataset/raw-curated/dec-ml-scan-2026-08-25/
```

สรุป:

| รายการ | จำนวน |
| --- | ---: |
| target records | 29 |
| scan_success | 29 |
| candidate families | 27 |
| candidate feature rows | 783 |
| weak positive labels | 29 |
| weak negative rows | 754 |

ไฟล์สำคัญ:

- `features.csv` - target-level scanner/fingerprint features
- `observations.jsonl` - observation ระดับ target
- `labels-draft.jsonl` - weak label จากชื่อ Vulhub lab
- `derived/candidate-family-features.csv` - input ML จริงแบบ candidate-level
- `derived/candidate-family-features.jsonl`
- `derived/attack-order-top5.csv` - top-5 candidate family ต่อ target สำหรับคุม validation/attack order
- `derived/attack-order-top5-merged.csv`
- `kali-run-kit/` - bundle สำหรับส่งให้ Kali/opencode ใช้รัน validation scan ต่อ
- `reports/dec-ml-scan-ranking-report-th.md`
- `reports/dec-ml-attack-order-validation-plan-th.md`
- `validation-target-queue.csv`
- `hex-next-target-candidates.csv` - shortlist 20 targets จาก Hex สำหรับสแกนเพิ่มรอบถัดไป
- `hex-next-scan-queue.csv` - queue 10 targets แรกจาก Hex ที่ควรสแกนหลัง validation queue
- `validation-results.schema.json`
- `validation-results.example.jsonl`

## ผล ML ล่าสุด

ทดสอบจาก `scripts/evaluate_dec_ml_scan_20260825.py`

| วิธี | Top-1 | Top-3 | Top-5 | mean attempts |
| --- | ---: | ---: | ---: | ---: |
| ML logistic ranker | 0.759 | 0.862 | 0.897 | 2.586 |
| Scanner heuristic | 0.724 | 0.828 | 0.862 | 2.724 |
| Random expected | 0.037 | 0.111 | 0.185 | 14.000 |

คำอ่าน:

- ML ช่วยเรียง candidate family ได้ดีกว่าสุ่มมาก
- ML ดีกว่า scanner heuristic เล็กน้อย แต่ยังไม่ขาด
- ผลนี้ยังเป็น weak-label validation ไม่ใช่ exploit-success validation
- การเพิ่มผล scan มีผลจริง เพราะทำให้เห็นจุดที่ model สับสน ไม่ใช่ได้คะแนน 1.000 แบบน่าสงสัยเหมือนรอบ fixed-core

## จุดที่ ML ยังพลาด

target ที่ positive หลุดเกิน Top-3:

| target | weak label | ML rank | เหตุผลเบื้องต้น |
| --- | --- | ---: | --- |
| `joomla_CVE-2023-23752` | `joomla` | 17 | scanner evidence ไม่มีคำ Joomla ชัดพอ |
| `spring_CVE-2022-22965` | `spring` | 13 | Spring/Tomcat/8080 ชนกัน |
| `shiro_CVE-2016-4437` | `shiro` | 12 | login/header ยังไม่บอก Shiro ชัด |
| `goahead_CVE-2017-17562` | `goahead` | 4 | พลาดเฉียด Top-3 เพราะ port 8080 ชนหลาย family |

queue สำหรับ validate ต่อ:

```text
experiments/dec-ml-scan-2026-08-25/validation-target-queue.csv
```

## Input ML คืออะไร

ตอนนี้ input ที่ชัดที่สุดคือ:

```text
experiments/dec-ml-scan-2026-08-25/derived/candidate-family-features.csv
```

โครงสร้าง:

- 1 target ถูกขยายเป็นหลาย candidate family
- แถวหนึ่งคือ 1 target + 1 candidate family
- label คือ `positive_family_match` ถ้า candidate family ตรงกับ weak label
- feature มาจาก scanner evidence เช่น title, server, nmap service line, port, protocol, tool coverage

สิ่งที่ไม่ควรใช้เป็น input จริง:

- `target_id`
- ชื่อ CVE ใน target
- `positive_family`
- label หรือ validation result
- field ที่มาจาก ground truth โดยตรง

## Workflow ฝั่ง Kali รอบถัดไป

prompt พร้อมใช้:

```text
docs/prompts/DEC-KALI-VALIDATION-QUEUE-PROMPT-TH.md
```

run kit พร้อมใช้:

```text
experiments/dec-ml-scan-2026-08-25/kali-run-kit/
C:\Users\rapii\Desktop\kali-share\dataset\dec-kali-validation-run-kit
```

ถ้า Kali เห็น shared folder ให้รัน:

```bash
cd /media/sf_kali-share/dataset/dec-kali-validation-run-kit
python3 scripts/kali/dec_validation_runner.py --queue validation-target-queue.csv --features features.csv --output-dir /home/kali/reports/dec-validation-manual
```

ให้ opencode/Kali ทำตาม queue เฉพาะ local lab:

1. เปิด target ทีละตัว
2. เก็บ evidence เพิ่มเฉพาะที่ขาด
3. เขียน `validation-results.jsonl`
4. copy ผลลัพธ์ไป shared folder
5. เอากลับมา import ด้วย:

```powershell
python scripts\import_dec_validation_results.py --input path\to\validation-results.jsonl
```

ผล import จะอยู่ที่:

```text
experiments/dec-ml-scan-2026-08-25/derived/validated-labels.csv
experiments/dec-ml-scan-2026-08-25/derived/validated-labels.jsonl
```

## Scripts สำคัญ

| script | ใช้ทำอะไร |
| --- | --- |
| `scripts/build_dec_dataset_v2.py` | build dataset Dec v2 จาก records/raw เดิม |
| `scripts/evaluate_dec_ml_ranking.py` | evaluate ranking ชุด fixed-core 43 targets |
| `scripts/evaluate_dec_ml_scan_20260825.py` | evaluate scanner-derived features ชุด 29 targets |
| `scripts/export_dec_attack_order.py` | export top-k attack order จาก ML predictions |
| `scripts/import_dec_validation_results.py` | validate/import ผล validation จาก Kali |
| `scripts/kali/dec_validation_runner.py` | เก็บ safe validation evidence จาก local Vulhub queue บน Kali |
| `scripts/validate_dec_artifacts.py` | ตรวจ fixed core, ML scan, candidate rows และ report JSON |

หลัง import validation แล้วให้รัน:

```powershell
python scripts\evaluate_dec_ml_scan_20260825.py --label-mode merged
```

คำสั่งนี้จะสร้างรายงาน `reports/dec-ml-scan-ranking-merged-report-th.md` และใช้ validated label ก่อน ถ้า target ยังไม่มี validation จะ fallback ไป weak label

ก่อน commit/push รอบใหญ่ให้รัน:

```powershell
python scripts\validate_dec_artifacts.py
```

## กติกาข้อมูล

- raw-curated เก็บเฉพาะผล scan จริง ไม่เก็บ cache/runtime/dependency
- label จากชื่อ lab เป็น weak label เท่านั้น
- exploit-success ต้องมาจาก validation แยก
- split train/test ต้องแยกตาม target หรือ family ไม่สุ่มรายแถว
- ห้ามใช้ field ที่เฉลยคำตอบเป็น feature
- ห้ามสแกน public target

## งานถัดไป

1. ส่ง `DEC-KALI-VALIDATION-QUEUE-PROMPT-TH.md` ให้ opencode ฝั่ง Kali
2. รัน validation queue เริ่มจาก Joomla, Spring, Shiro, GoAhead
3. import `validation-results.jsonl` กลับด้วย `scripts/import_dec_validation_results.py`
4. เพิ่ม validated labels เข้า evaluator แล้วแยก metric ระหว่าง weak label กับ validated label
5. เพิ่ม negative controls ที่ port เดียวกันแต่คนละ family เช่น 8080 non-Spring/non-Tomcat
6. เพิ่ม feature เฉพาะ family เช่น cookie, redirect path, endpoint fingerprint, framework marker
7. rerun ML ranking แล้วเทียบ Top-k/attempts ก่อนและหลัง validation
