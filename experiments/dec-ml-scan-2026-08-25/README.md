# Dec ML Scan 2026-08-25

ชุดนี้เป็นผลสแกนจาก Kali/Vulhub ที่เก็บเพิ่มเพื่อทดลอง ML ranking ของโปรเจกต์ Dec

เป้าหมายคือเพิ่มข้อมูล scanner-derived feature ให้โมเดลเห็น service/family ที่หลากหลายขึ้น ไม่ใช่เพิ่ม raw ทั้งก้อนแบบไม่คัด

## สถานะชุดนี้

- จำนวน target records: 29
- scan_success: 29
- raw หลักอยู่ที่ `dataset/raw-curated/dec-ml-scan-2026-08-25/`
- ชุด feature สำหรับทดลองอยู่ในโฟลเดอร์นี้

## ไฟล์สำคัญ

| ไฟล์ | ใช้ทำอะไร |
| --- | --- |
| `SCAN-SUMMARY-TH.md` | สรุปภาษาไทยของรอบสแกน |
| `observations.jsonl` | observation ระดับ target จาก scanner/fingerprint |
| `features.csv` | feature table สำหรับทดลอง ML ranking |
| `features-enriched.csv` | feature table ที่เติม `evidence_text`, `body_fingerprint`, จำนวนไฟล์ evidence และจำนวน finding จาก raw-curated โดยตัด target/CVE leakage ออกก่อนใช้ |
| `feature-inventory.csv` | รายการ feature ทั้งหมด พร้อมระดับข้อมูล ที่มา เหตุผลที่ใช้ และข้อควรระวัง |
| `ML-COMPARISON-EXPLAINED-TH.md` | คำอธิบายภาษาไทยว่า ML วัดผลอย่างไร เปรียบเทียบอะไร และ source code ทำงานยังไง |
| `labels-draft.jsonl` | weak label จากชื่อ Vulhub path |
| `derived/candidate-family-features.csv` | input ML แบบ candidate-level: 1 target x ทุก candidate family |
| `derived/candidate-family-features.jsonl` | ข้อมูลเดียวกับ CSV แต่เหมาะกับ pipeline ที่อ่าน JSONL |
| `derived/candidate-family-features-merged.csv` | input ML โหมด merged: ใช้ validated label ถ้ามี ไม่มีกลับไปใช้ weak label |
| `derived/attack-order-top5.csv` | ลำดับ candidate family 5 อันดับแรกต่อ target สำหรับคุม validation/attack order |
| `derived/attack-order-top5-merged.csv` | attack order จาก prediction โหมด merged |
| `kali-run-kit/` | ชุดไฟล์พร้อมส่งให้ Kali/opencode เพื่อรัน validation scan จาก queue |
| `reports/dec-ml-scan-ranking-report-th.md` | รายงานทดสอบ ML ranking ภาษาไทยจากชุด scan นี้ |
| `reports/dec-ml-scan-ranking-metrics.json` | metric เต็มสำหรับอ่านด้วย script/notebook |
| `reports/dec-ml-scan-ranking-merged-report-th.md` | รายงาน ranking โหมด merged สำหรับใช้หลัง import validation |
| `reports/dec-ml-attack-order-validation-plan-th.md` | แผนทดสอบ attack order และ validation loop รอบถัดไป |
| `validation-target-queue.csv` | target queue สำหรับให้ Kali/opencode validate ต่อ |
| `hex-next-target-candidates.csv` | shortlist 20 targets จาก Hex สำหรับเลือกสแกนเพิ่มรอบถัดไป |
| `hex-next-scan-queue.csv` | queue 10 targets แรกจาก Hex ที่ควรสแกนต่อหลัง validation queue |
| `validation-results.schema.json` | schema ของผล validation ที่ Kali ต้องส่งกลับ |
| `validation-results.example.jsonl` | ตัวอย่าง 1 record สำหรับเช็ก format |
| `validation-results.fixture.jsonl` | fixture สำหรับทดสอบ import/evaluator หลายสถานะ ไม่ใช่ผล scan จริง |
| `derived/validated-labels.csv` | label table ที่ import จาก validation results ตัวอย่าง |
| `derived/fixture/` | output จาก fixture ใช้เป็น regression check |
| `dec-ml-scan-2026-08-25.tar.gz` | archive ของ raw-curated รอบนี้ |

## ควรใช้ยังไง

ใช้ `features.csv` เป็น input ทดลอง ranking model ได้ทันที โดยเริ่มจากคอลัมน์พวกนี้:

- `protocol_kind`
- `port`
- `candidate_family`
- `title`
- `server`
- `x_powered_by`
- `http_status`
- `nmap_service_line`
- `scan_success`
- `has_nmap`
- `has_probe`
- `has_nikto`
- `has_wapiti`

ใช้ `labels-draft.jsonl` เพื่อเทียบว่า target นี้ควรอยู่ family ไหน แต่ต้องจำไว้ว่า label นี้ยังอ่อน เพราะได้จากชื่อ lab/folder ของ Vulhub

ถ้าจะดู input ที่ ML ใช้จริงใน evaluator ให้เปิด `derived/candidate-family-features.csv`:

- 1 target จะถูกขยายเป็นหลายแถวตามจำนวน candidate family
- แต่ละแถวมี `target_id`, `candidate_family`, `positive_family`, `label`
- feature หลักคือคะแนนจาก scanner evidence เช่น `title_alias_score`, `server_alias_score`, `nmap_alias_score`, `port_score`, `protocol_score`
- แถวที่ `candidate_family` ตรงกับ weak label จะเป็น `positive_family_match` ที่เหลือเป็น `negative_family`

รัน evaluator รอบนี้ได้ด้วย:

```powershell
python scripts\enrich_dec_ml_scan_features.py
python scripts\evaluate_dec_ml_scan_20260825.py
```

ค่า default คือ `--label-mode weak` แปลว่าใช้ `labels-draft.jsonl` ทั้งหมด และ evaluator จะใช้ `features-enriched.csv` อัตโนมัติถ้าไฟล์นี้มีอยู่ ถ้าไม่มีกลับไปใช้ `features.csv`

หลังจาก import ผล validation จาก Kali แล้ว ให้รันแบบ merged:

```powershell
python scripts\evaluate_dec_ml_scan_20260825.py --label-mode merged
```

โหมด `merged` จะใช้ validated positive/negative ก่อน ถ้า target ยังไม่มีผล validation จะ fallback ไปใช้ weak label เพื่อให้ยังวัดภาพรวมครบทุก target ได้

สร้างไฟล์ attack order สำหรับคุม Kali/opencode:

```powershell
python scripts\export_dec_attack_order.py --top-k 5
python scripts\export_dec_attack_order.py --prediction-file experiments\dec-ml-scan-2026-08-25\reports\dec-ml-scan-ranking-merged-predictions.json --suffix merged --top-k 5
```

ไฟล์ `derived/attack-order-top5.csv` ช่วยบอกว่าแต่ละ target ควร validate candidate family ใดก่อน พร้อม rank/probability และ queue reason

ผลล่าสุด:

- ML logistic ranker โหมด merged หลัง import Kali validation/tool-scope: Top-1 `0.931`, Top-3 `0.966`, mean attempts `1.172`
- Scanner heuristic โหมด merged หลัง import Kali validation: Top-1 `0.931`, Top-3 `1.000`, mean attempts `1.103`
- Validated-only 8 targets: Top-1 `1.000`, Top-3 `1.000`, mean attempts `1.000`
- Random expected: Top-1 `0.037`, Top-3 `0.111`, mean attempts `14.000`

ความหมายคือ feature enriched + Kali validation evidence ช่วยลดจำนวน candidate ที่ต้องลองจากค่าเฉลี่ยสุ่มประมาณ 14 เหลือประมาณ 1.1-1.2 ในชุด 29 targets และ target ที่ validate แล้ว 8 ตัวเข้าอันดับ 1 ทั้งหมด

จุดที่ ML ยังพลาดเกิน Top-3 หลัง import validation:

- ML logistic ยังมี `appweb_CVE-2018-8715` หลุด Top-3 หลังเพิ่ม GoAhead evidence รอบล่าสุด
- Scanner heuristic ไม่มี failure เกิน Top-3

หมายเหตุ: `spring_CVE-2022-22965` ยังเป็น `inconclusive` ใน validation label เพราะ lab รอบนี้เห็น Tomcat/JSESSIONID แต่ไม่พบ Spring-specific fingerprint เช่น actuator หรือ Whitelabel Error Page ดังนั้นถ้าต้อง validate exploit/family ให้แน่นขึ้น ควรสแกน Spring lab เพิ่มอีกรอบด้วย target ที่มี Spring fingerprint ชัดกว่าเดิม

หมายเหตุเพิ่ม: `appweb_CVE-2018-8715` ควรเข้าสแกนรอบถัดไปเพื่อหา AppWeb-specific fingerprint เพราะตอนนี้ evidence ของ AppWeb ยังไม่แข็งพอเมื่อเทียบกับ GoAhead

prompt สำหรับส่งให้ opencode ฝั่ง Kali อยู่ที่ `docs/prompts/DEC-KALI-VALIDATION-QUEUE-PROMPT-TH.md`

ถ้าต้องการส่งงานให้ Kali แบบง่าย ให้ใช้โฟลเดอร์นี้:

```text
kali-run-kit/
```

ในชุดนี้มี `features.csv`, `validation-target-queue.csv`, `attack-order-top5.csv`, prompt, runbook และ runner ครบแล้ว

คำสั่งบน Kali:

```bash
cd /media/sf_kali-share/dataset/dec-kali-validation-run-kit
python3 scripts/kali/dec_validation_runner.py \
  --queue validation-target-queue.csv \
  --features features.csv \
  --output-dir /home/kali/reports/dec-validation-manual
```

เมื่อได้ไฟล์ `validation-results.jsonl` กลับมาจาก Kali ให้ import ด้วย:

```powershell
python scripts\import_dec_validation_results.py --input path\to\validation-results.jsonl
```

ถ้าผลจาก Kali เป็นทั้งโฟลเดอร์ run ที่มี `validation-results.jsonl` และ `raw-curated/` ให้ใช้ ingest script แทน เพื่อเอาทั้ง label และ evidence กลับเข้า ML loop:

```powershell
python scripts\ingest_dec_kali_validation_run.py --run-dir C:\Users\rapii\Desktop\kali-share\dataset\dec-validation-manual
python scripts\enrich_dec_ml_scan_features.py
python scripts\evaluate_dec_ml_scan_20260825.py --label-mode merged
python scripts\export_dec_attack_order.py --prediction-file experiments\dec-ml-scan-2026-08-25\reports\dec-ml-scan-ranking-merged-predictions.json --suffix merged --top-k 5
```

flow นี้คือดูว่า ML พลาดอะไร แล้วสแกนเพิ่มเฉพาะจุดนั้น จากนั้นค่อยดึง evidence ใหม่กลับมาเป็น feature ใหม่ให้ ML เรียนรู้เพิ่ม

## ยังไม่ควรใช้ยังไง

- อย่าใช้ `candidate_family`, ชื่อ CVE, หรือชื่อ target เป็น feature หลักในการวัดความแม่นจริง เพราะเสี่ยง label leakage
- อย่าถือว่า `labels-draft.jsonl` คือ exploit-success ground truth
- อย่าเทรนรวมกับชุดหลักโดยไม่แยก train/test ตาม family หรือ target group

## งานต่อ

- ทำ validation script สำหรับ target ที่มี probe เช่น Joomla, Grafana, ThinkPHP, Redis, Aria2
- ติดตั้ง ProjectDiscovery `httpx` ตัวจริงแทน Python `httpx`
- จูน `nuclei` ให้เลือก template เฉพาะ CVE เพื่อลด timeout
- normalize ชุดนี้เข้า schema หลักของ Dec ถ้าจะเอาไปรวมกับ 43-target fixed core
