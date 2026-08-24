# Scanner Suite Note

ระบบถูกออกแบบให้รับข้อมูลจากหลาย tools:

```text
nmap
httpx
nuclei
nikto
wapiti
zap
```

ตำแหน่งประกาศ tools:

```text
chimera-tools-name-date-2026-08-05-multi-vuln-web/manifests/source-run-manifest.json
```

ตำแหน่งเก็บ output:

```text
datasets/tools-name-date/<tool-name>-2026-08-05/<lab-id>/raw/
datasets/tools-name-date/<tool-name>-2026-08-05/<lab-id>/normalized/
```

ข้อมูลที่เอาไปเป็น feature:

```text
has_zap_evidence
has_nuclei_evidence
has_wapiti_evidence
has_nikto_evidence
zap_finding_count
nuclei_finding_count
nikto_finding_count
wapiti_finding_count
observed_tech_count
service_product_count
service_version_count
```

หมายเหตุ:

สำหรับ public CTF target รอบนี้ใช้ passive fingerprint เท่านั้น ส่วน scanner suite เต็มควรใช้กับ local lab หรือ target ที่มี scope ชัดเจน

