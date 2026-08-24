# Pipeline + Code Reference

ไฟล์นี้อธิบายว่า pipeline ของ Chimera / Exploit-DL ทำงานจาก target ไปเป็น dataset, feature, model และ report โดยอ้างอิงไฟล์โค้ดจริง

## Pipeline ภาพรวม

```text
Target URL
  ↓
Passive Fingerprint / Scanner Output
  ↓
Raw + Normalized Records
  ↓
Training Examples
  ↓
Feature Matrix
  ↓
Baseline Model
  ↓
Ranked Report
```

## 1. รับ URL และ fingerprint เป้าหมาย

ไฟล์:

```text
chimera-tools-name-date-2026-08-05-multi-vuln-web/scripts/live_rank_target.py
chimera-tools-name-date-2026-08-05-multi-vuln-web/scripts/generic_live_report.py
```

ส่วนสำคัญ:

```python
def http_fingerprint(url: str, timeout: int = 10) -> dict:
```

และ:

```python
def fetch(url: str) -> dict:
```

ข้อมูลที่ดึง:

```text
status_code
title
server
content_type
content_length
form_count
input_names
links
observed_tech
```

## 2. รัน/เก็บข้อมูลจากหลาย tools

Tool list ถูกประกาศไว้ใน:

```text
chimera-tools-name-date-2026-08-05-multi-vuln-web/manifests/source-run-manifest.json
```

Tools:

```text
nmap
httpx
nuclei
nikto
wapiti
zap
```

โครงสร้าง output:

```text
datasets/tools-name-date/<tool-name>-2026-08-05/<lab-id>/
  raw/
  normalized/
```

ความหมาย:

- `raw/` = output ดิบจาก scanner
- `normalized/` = output ที่ parse ให้เป็น JSONL/record สำหรับนำไปทำ feature

## 3. สร้าง training examples

ไฟล์:

```text
chimera-tools-name-date-2026-08-05-multi-vuln-web/scripts/build_features.py
```

อ่าน records:

```python
targets = read_jsonl(records_dir / "exploit-dl-target-features.jsonl")
ranks = read_jsonl(records_dir / "exploit-rank-candidates.jsonl")
all_records = read_jsonl(records_dir / "all-records.jsonl")
```

สร้าง label เบื้องต้น:

```python
"is_top1": 1 if rank_value == 1 else 0
"is_recommended": 1 if rank_value <= 2 or rank_score >= 0.70 else 0
```

สร้าง scanner evidence feature:

```python
"has_zap_evidence": 1 if "zap" in evidence_sources else 0
"has_nuclei_evidence": 1 if "nuclei" in evidence_sources else 0
"has_wapiti_evidence": 1 if "wapiti" in evidence_sources else 0
"has_nikto_evidence": 1 if "nikto" in evidence_sources else 0
"zap_finding_count": int(counts.get("zap", 0))
"nuclei_finding_count": int(counts.get("nuclei", 0))
"nikto_finding_count": int(counts.get("nikto", 0))
"wapiti_finding_count": int(counts.get("wapiti", 0))
```

Output:

```text
derived/training_examples.csv
derived/training_examples.jsonl
```

## 4. แปลงเป็น feature matrix

ไฟล์:

```text
chimera-tools-name-date-2026-08-05-multi-vuln-web/scripts/build_features.py
```

ใช้ numeric feature:

```text
port
rank_score
family_risk_prior
evidence_source_count
has_zap_evidence
has_nuclei_evidence
zap_finding_count
observed_tech_count
service_product_count
```

ใช้ categorical feature:

```text
product
candidate_exploit_family
observed_tech_text
service_products_text
service_versions_text
evidence_sources_text
```

แปลงข้อความเป็นตัวเลข:

```python
pd.get_dummies(...)
```

Output:

```text
derived/feature_matrix.csv
```

## 5. Train baseline model

ไฟล์:

```text
chimera-tools-name-date-2026-08-05-multi-vuln-web/scripts/train_baseline.py
```

กำหนด input/output:

```python
X = df[NUMERIC_COLS + CAT_COLS]
y = df["is_recommended"].astype(int)
```

โมเดล:

```python
RandomForestClassifier(
    n_estimators=250,
    random_state=42,
    class_weight="balanced"
)
```

Output:

```text
models/random_forest_exploit_ranker.joblib
derived/baseline_predictions.csv
derived/baseline_metrics.json
```

## 6. Predict และออก ranked report

ไฟล์:

```text
chimera-tools-name-date-2026-08-05-multi-vuln-web/scripts/live_rank_target.py
```

ส่วนสำคัญ:

```python
fingerprint = http_fingerprint(args.url)
rows = build_rows(args.profile, args.url, fingerprint)
model = joblib.load(model_path)
rows["predicted_success_probability"] = model.predict_proba(rows)[:, 1]
rows = rows.sort_values("predicted_success_probability", ascending=False)
```

Output:

```text
fingerprint.json
ranked_exploits.csv
ranked_exploits.jsonl
report.md
```

