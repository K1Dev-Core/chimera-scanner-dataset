# Model Runbook — วิธีรันระบบจาก dataset ไปเป็น report

เริ่มจากโฟลเดอร์หลัก:

```powershell
cd C:\Users\uSeR\Documents\Codex\2026-08-04\docker-cve-wp2shell-2\work\chimera-scanner-dataset\chimera-tools-name-date-2026-08-05-multi-vuln-web
```

## 1. Build feature

```powershell
python scripts\build_features.py --dataset-root .
```

Output:

```text
derived\training_examples.csv
derived\training_examples.jsonl
derived\feature_matrix.csv
derived\feature_summary.json
```

## 2. Train baseline model

```powershell
python scripts\train_baseline.py --dataset-root .
```

Output:

```text
models\random_forest_exploit_ranker.joblib
derived\baseline_predictions.csv
derived\baseline_metrics.json
```

## 3. Predict ตัวอย่างจาก lab profile

```powershell
python scripts\predict_example.py --dataset-root . --lab-id dvwa
```

## 4. Run live ranking กับ local lab

ตัวอย่าง Acme:

```powershell
python scripts\live_rank_target.py --dataset-root . --profile acme-support --url http://127.0.0.1:27000 --out live-reports\acme-support
```

ตัวอย่าง Nova:

```powershell
python scripts\live_rank_target.py --dataset-root . --profile nova-devops --url http://127.0.0.1:27100 --out live-reports\nova-devops
```

## 5. Run passive report กับ CTF target

ตัวอย่าง target ใหม่:

```powershell
python scripts\generic_live_report.py --url http://lonely-island.picoctf.net:49776/ --out live-reports\picoctf-lonely-island-49776
```

Output:

```text
live-reports\picoctf-lonely-island-49776\chimera_model_report.json
live-reports\picoctf-lonely-island-49776\ranked_families.jsonl
live-reports\picoctf-lonely-island-49776\report.md
```

## 6. หมายเหตุ

สำหรับ public CTF target ให้ใช้ passive fingerprint/ranking เป็นหลัก ไม่ควรรัน scanner หนักแบบ aggressive ถ้าไม่มีขอบเขตที่ชัดเจน

