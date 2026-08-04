# Nova DevOps Console

Fresh unseen local CTF lab สำหรับทดสอบ Exploit-DL ranking

เว็บนี้ทำให้เหมือน internal DevOps console มีหน้า deployment, search, template preview, healthcheck, webhook fetcher และ config viewer

## Intended vulnerability families

- SQL injection
- Template injection / RCE-style risk
- Command injection / RCE-style risk
- Path traversal / arbitrary file read style risk
- SSRF-style webhook fetcher
- Broken access control / IDOR
- Sensitive data exposure

## Flag

Flag อยู่ใน container filesystem ที่:

```text
/flag.txt
```

อย่าใส่เฉลย/payload ใน report สำหรับผู้ทดสอบ ถ้าจะใช้แข่งให้แจกแค่ URL และ scope

## Safety

รันเฉพาะ localhost เท่านั้น ห้าม deploy ขึ้น public internet
