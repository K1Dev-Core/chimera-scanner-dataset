# Unseen Lab: Nova DevOps Console

Nova DevOps Console เป็น lab ใหม่ที่ไม่ได้อยู่ใน training dataset เดิม ใช้สำหรับวัดว่า model จะช่วย rank ช่องโหว่ของ target ใหม่ได้แค่ไหน

## Target

```text
http://127.0.0.1:27100
```

## Analyzer profile

```text
nova-devops
```

## Intended vulnerability families

- Command injection / RCE-style risk
- SQL injection
- File read / path traversal style risk
- SSRF-style webhook fetcher
- Broken access control / IDOR
- Template injection / RCE-style risk
- Sensitive data exposure

## Flag

Flag อยู่ใน container filesystem:

```text
/flag.txt
```

อย่าเอา endpoint/payload เฉลยไปใส่ในโจทย์ผู้ทดสอบ ให้แจกแค่ URL + scope แล้วใช้เวลาวัดผล

## Run model report

```powershell
python scripts/live_rank_target.py --dataset-root . --profile nova-devops --url http://127.0.0.1:27100 --out live-reports/nova-devops
```
