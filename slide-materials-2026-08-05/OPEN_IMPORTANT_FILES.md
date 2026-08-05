# ไฟล์สำคัญที่ควรเปิดดู

## 1. Dataset prototype หลัก

```text
chimera-tools-name-date-2026-08-05-multi-vuln-web/derived/training_examples.csv
chimera-tools-name-date-2026-08-05-multi-vuln-web/derived/feature_matrix.csv
```

ใช้ดูตัวอย่างแถวข้อมูลจริงและ feature ที่โมเดลใช้

## 2. Dataset ขยายจาก Vulhub

```text
chimera-tools-name-date-2026-08-05-vulhub-expanded-metadata/derived/training_examples.csv
chimera-tools-name-date-2026-08-05-vulhub-expanded-metadata/derived/feature_matrix.csv
chimera-tools-name-date-2026-08-05-vulhub-expanded-metadata/manifests/index.json
```

ใช้ดูจำนวน labs, training rows, feature columns และ vulnerability family

## 3. README/แผนภาษาไทยของชุดข้อมูล

```text
chimera-tools-name-date-2026-08-05-vulhub-redo/README.md
chimera-tools-name-date-2026-08-05-vulhub-redo/EXPLOIT_DL_FEATURE_PLAN.md
chimera-tools-name-date-2026-08-05-multi-vuln-web/README.md
chimera-tools-name-date-2026-08-05-multi-vuln-web/MANUAL_VS_MODEL_TEST_PLAN_TH.md
chimera-tools-name-date-2026-08-05-multi-vuln-web/DATASET_EXPANSION_STATUS_TH.md
```

ใช้เอาข้อความไปใส่สไลด์และรายงาน

## 4. Custom vulnerable labs

```text
fresh-labs/acme-support-portal
fresh-labs/nova-devops-console
fresh-labs/vulhub-grafana-cve-2024-9264
fresh-labs/vulhub-teamcity-cve-2024-27198
```

ใช้โชว์ว่าเรามี lab สำหรับ demo/testing ไม่ได้มีแค่ metadata

## 5. Scripts สำคัญ

```text
chimera-tools-name-date-2026-08-05-multi-vuln-web/scripts/build_features.py
chimera-tools-name-date-2026-08-05-multi-vuln-web/scripts/train_baseline.py
chimera-tools-name-date-2026-08-05-multi-vuln-web/scripts/live_rank_target.py
```

ใช้โชว์ pipeline ว่ามีการ build feature, train model และ generate live ranking report จริง

