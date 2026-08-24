# สรุปการรัน DEC: dec-vulhub-2026-08-05

- project: Chimera Scanner Dataset / branch `Dec`
- scope: Vulhub local lab เท่านั้น ใช้ `127.0.0.x` ไม่ได้ scan public targets
- reuse old data: ใช่ ใช้ข้อมูลเก่า 10 targets จาก 2026-08-04 และรันใหม่ 12 targets
- total targets ตอนรันแรก: 22 targets
- path บน Kali ตอนสร้าง: `/home/kali/dataset/dec-vulhub-2026-08-05/`

หมายเหตุ: package ปัจจุบันถูก fix schema เพิ่มเติมเมื่อ 2026-08-25 และกลายเป็น core 43 targets

## CVE/target ที่เพิ่มในรอบนี้

- `CVE-2018-7600`
- `CVE-2018-7602`
- `CVE-2020-14882`
- `CVE-2017-10271`
- `CVE-2018-1000861`
- `CVE-2015-8562`
- `CVE-2018-12613`
- `CVE-2019-0193`
- `CVE-2019-17558`
- `CVE-2016-4437`
- `thinkphp_5rce`
- `flask_ssti`

## ผลการรัน tool

| Tool | success | no_finding | failed | timeout | skipped | target_down |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| nmap | 22 | 0 | 0 | 0 | 0 | 0 |
| naabu | 22 | 0 | 0 | 0 | 0 | 0 |
| httpx-toolkit | 22 | 0 | 0 | 0 | 0 | 0 |
| nuclei | 13 | 0 | 0 | 9 | 0 | 0 |
| nikto | 19 | 0 | 0 | 3 | 0 | 0 |
| wapiti | 20 | 0 | 0 | 2 | 0 | 0 |
| zaproxy | 22 | 0 | 0 | 0 | 0 | 0 |
| metasploit | 11 | 0 | 1 | 0 | 4 | 0 |
| sqlmap | 3 | 1 | 0 | 0 | 10 | 0 |
| manual_poc | 11 | 0 | 1 | 0 | 0 | 0 |

## Exploit validation ที่ยืนยันใน lab

- `drupal_7602`: RCE สำเร็จผ่าน cancel-form destination poisoning
- `drupal_7600`: version vulnerable แต่ยังไม่ได้ code execution จาก register-page vector
- `weblogic_14882`: RCE สำเร็จผ่าน console.portal MVEL ShellSession
- `weblogic_10271`: RCE สำเร็จผ่าน wls-wsat XMLDecoder
- `solr_0193`: RCE สำเร็จผ่าน DataImportHandler script transformer
- `solr_17558`: RCE สำเร็จผ่าน Velocity template params.resource.loader
- `phpmyadmin_12613`: LFI ไปสู่ RCE ผ่าน session file inclusion
- `shiro_4437`: RCE ผ่าน rememberMe default AES key deserialization
- `joomla_8562`: RCE ผ่าน HTTP header object injection
- `thinkphp_5rce`: RCE ผ่าน `\think\app/invokefunction`
- `flask_ssti`: SSTI ยืนยันด้วย `{{7*7}}` ได้ `49`
- `jenkins_1000861`: unauthenticated script-console RCE เคยยืนยันก่อนหน้า

## Records ที่ผลิตได้ตอนรันแรก

- targets: 22
- observations: 1776
- findings: 1211
- validations: 41
- tool_runs: 195
- candidate rows: 198
- labels: 198

## Quality gate ตอนรันแรก

```text
valid = true
jsonl_invalid_lines = 0
duplicate_record_ids = 0
missing_label_refs = 0
label_leakage_fields = 0
unredacted_sensitive_values = 0
public_ips = 0
targets = 22
target_candidate_rows = 198
```

## ข้อจำกัดที่ต้องรู้

- `nuclei` timeout บาง target เพราะ template เยอะและ rate ต่ำ
- `nikto` timeout 3 targets
- `wapiti` timeout 2 targets
- `drupal_7600` ยังบันทึกเป็น vulnerable-by-version ไม่ใช่ RCE success
- `sqlmap` มี skip records สำหรับ target ที่ไม่มี parameterized URL
- ไม่มี public IP scan และไม่มี fabricated data

## Schema fix เมื่อ 2026-08-25

- แก้ `records/findings.jsonl` ให้ `record_type` เป็น `finding`
- normalize `scan_status` ของ finding จาก `finding` เป็น `success`
- ลบ duplicated finding rows ออกจาก `records/observations.jsonl`
- เพิ่ม `record_type=tool_run` ใน `records/tool_runs.jsonl`
- rebuild `records/all-records.jsonl`
- count ล่าสุด: targets=43, observations=704, findings=2046, validations=92, tool_runs=381, all_records=3266
- package นี้เป็น core artifact เท่านั้น raw scan files เต็มยังอยู่ใน shared/local raw และ curated raw packages
