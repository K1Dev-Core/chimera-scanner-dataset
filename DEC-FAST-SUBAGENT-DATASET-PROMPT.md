# DEC Fast Sub-Agent Dataset Prompt

อัปเดต: 2026-08-05  
โปรเจค: Chimera Scanner Dataset / Dec branch  
ขอบเขต: Vulhub local lab และระบบที่ได้รับอนุญาตเท่านั้น

## อัปเดตหลังรัน batch ใหม่

อัปเดต 2026-08-06:

- มี batch ใหม่ `dec-vulhub-2026-08-05` รวม 22 targets แล้ว
- source batch ใน shared folder มีข้อมูลเพิ่มจริง แต่พบ schema issue
- fixed copy ที่ควรใช้ต่ออยู่ที่:

```text
C:\Users\rapii\Documents\Codex\2026-08-03\faraday-https-github-com-infobyte-faraday\work\dec-vulhub-2026-08-05-fixed
```

fixed copy ล่าสุด:

```text
targets=22
observations=565
findings=1211
validations=41
tool_runs=195
all_records=2034
target_candidate_labels=198
duplicate_record_ids=0
quality.valid=true
```

ถ้า agent ทำงานต่อจากตอนนี้ ห้ามรัน batch ใหม่ทันที ให้ตรวจ fixed copy ก่อน แล้วทำงานที่เหลือ:

1. copy fixed dataset กลับไป shared folder หรือเตรียมอัปขึ้น Git
2. อัป builder ให้ทำ schema fix/dedup ซ้ำได้อัตโนมัติ
3. อัป README/data dictionary/status
4. ทำ baseline train/test split และ model demo
5. เพิ่ม OpenVAS export หากต้องการ coverage เพิ่ม



## อัปเดต 2026-08-25

มี fixed core package ล่าสุดจาก batch 43 targets แล้ว ให้ใช้เป็นตัวหลักก่อนรันงานต่อ:

```text
C:\Users\rapii\Documents\Codex\2026-08-03\faraday-https-github-com-infobyte-faraday\work\dec-vulhub-2026-08-24-fixed-core-v2
```

Counts: targets=43, observations=704, findings=2046, validations=92, tool_runs=381, all_records=3266, candidate_rows=602

งานต่อจากนี้ควรเป็นการสร้าง builder ที่ reproduce fixed core ได้, ทำ train/test split, baseline model และอัป OpenVAS หากต้องการ coverage เพิ่ม

## ใช้ไฟล์นี้ทำอะไร

ไฟล์นี้คือ prompt สำหรับให้ agent ทำงานเก็บ dataset ต่อแบบเร็ว มีระบบ และทำซ้ำได้ โดยต้องใช้ข้อมูลเก่าก่อน ถ้าของเก่าใช้ไม่ได้หรือคุณภาพไม่ผ่านค่อยรันใหม่

เป้าหมายไม่ใช่ทำให้ทุก scanner เจอ CVE ทุกตัว แต่คือเก็บ scanner signal ให้ครบ:

- เครื่องมือเจออะไร
- เครื่องมือไม่เจออะไร
- เครื่องมือรันพังตรงไหน
- target start ไม่ขึ้นหรือไม่
- validation exploit ทำงานจริงหรือไม่
- raw และ normalized เชื่อมกลับกันได้หรือไม่

ผลลัพธ์สุดท้ายต้องเอาไปใช้เป็น dataset สำหรับ demo แรกของโปรเจค cyber / Exploit-DL ได้

## ข้อจำกัดด้านความปลอดภัย

- สแกนเฉพาะ Vulhub local lab
- ห้ามสแกน public IP, domain จริง หรือระบบที่ไม่ได้รับอนุญาต
- ห้ามยิง exploit นอก lab
- ห้ามเก็บ password, cookie, token, session id, authorization header แบบ raw ใน normalized output
- ถ้า raw มีข้อมูล sensitive ให้เก็บไว้เฉพาะในเครื่อง lab และ normalized ต้อง redact
- ห้ามสร้างข้อมูลปลอมเพื่อให้จำนวนดูดีขึ้น

## ก่อนเริ่ม ให้ติดตั้งหรือเตรียม Skill/Capability

ถ้าใช้ Codex หรือ agent platform ที่มี skill/sub-agent ให้เตรียม capability เหล่านี้ก่อนเริ่ม:

| Capability | ใช้ทำอะไร | แหล่งที่แนะนำ |
|---|---|---|
| Multi-agent tools | แบ่งงานเป็น coordinator, scanner, normalizer, QA | Codex `tool_search` ค้นหา `Multi-agent tools` |
| ctf-web | เข้าใจ web vuln, SQLi, SSTI, SSRF, auth, request/response evidence | `C:/Users/rapii/Desktop/Skill agent/02_CTF_Labs/ctf-skills/ctf-skills-main/ctf-web` |
| ctf-auto-enrich | สรุปหลักฐาน, reproduce step, ทำ handoff หลังสแกน | `C:/Users/rapii/.codex/skills/ctf-auto-enrich` |
| ctf-writeup | เขียนรายงานผลการทดลองแบบเป็นระบบ | `C:/Users/rapii/Desktop/Skill agent/02_CTF_Labs/ctf-skills/ctf-skills-main/ctf-writeup` |
| ctf-forensics | ตรวจ raw log, artifact, PCAP หรือหลักฐานที่ต้อง parse เพิ่ม | `C:/Users/rapii/Desktop/Skill agent/02_CTF_Labs/ctf-skills/ctf-skills-main/ctf-forensics` |
| ctf-malware | ใช้เฉพาะกรณี target เกี่ยวกับ exploit payload/log ที่ต้องวิเคราะห์เชิง IOC | `C:/Users/rapii/Desktop/Skill agent/02_CTF_Labs/ctf-skills/ctf-skills-main/ctf-malware` |
| github | ใช้ push ผลลัพธ์ขึ้น branch `Dec` เมื่อ dataset ผ่าน QA | Codex GitHub skill/plugin ถ้ามี |

ถ้า agent ไม่มี skill เหล่านี้ ให้ทำงานต่อด้วย command-line workflow ปกติ แต่ต้องรักษา schema, raw, normalized และ quality gate ตามไฟล์นี้

## Path หลักบน Kali

```bash
SOURCE_VULHUB="$HOME/labs/vulhub"
REPORT_ROOT="$HOME/reports"
DATASET_ROOT="/media/sf_kali-share/dataset"
RUN_DATE="$(date +%F)"
RUN_ID="dec-vulhub-${RUN_DATE}"
RUN_ROOT="${DATASET_ROOT}/${RUN_ID}"
```

สร้างโฟลเดอร์:

```bash
mkdir -p \
  "${RUN_ROOT}/raw" \
  "${RUN_ROOT}/normalized" \
  "${RUN_ROOT}/logs" \
  "${RUN_ROOT}/metadata" \
  "${RUN_ROOT}/records" \
  "${RUN_ROOT}/derived" \
  "${RUN_ROOT}/labels" \
  "${REPORT_ROOT}"
```

## Strategy หลัก

### Phase 1: ใช้ของเก่าก่อน

ให้ agent ตรวจ dataset เก่าก่อน:

```bash
OLD_DATASET="/media/sf_kali-share/dataset"
find "${OLD_DATASET}" -maxdepth 5 -type f | sort > "${REPORT_ROOT}/old-dataset-inventory.txt"
```

ตรวจขั้นต่ำ:

- มี raw output หรือไม่
- มี normalized output หรือไม่
- JSONL parse ได้หรือไม่
- มี target metadata หรือไม่
- มี command/provenance หรือไม่
- มี sensitive value หลุดหรือไม่
- มี target ซ้ำกับชุดตัวอย่างที่ห้ามซ้ำหรือไม่
- มี CVE ซ้ำกับ batch เดิมโดยไม่จำเป็นหรือไม่

ถ้าข้อมูลเก่าใช้ได้ ให้ reuse raw แล้ว normalize ใหม่ได้  
ถ้าข้อมูลเก่าใช้ไม่ได้ ให้บันทึกเหตุผลใน `logs/reuse-decision.md` แล้วรันใหม่

### Phase 2: ถ้าต้องรันใหม่

รันเพิ่มอีก 12 CVE เพื่อให้รวมกับของเดิมได้ประมาณ 20-22 targets สำหรับ demo แรก

ไม่จำเป็นต้องรันทุก scanner สำเร็จทุก target แต่ทุกความล้มเหลวต้องถูกบันทึกเป็น record

## จำนวน CVE ที่แนะนำ

สำหรับ demo แรก:

```text
ขั้นต่ำ: 20 targets รวมของเดิม
แนะนำ: 22 targets
รอบนี้ควรเพิ่ม: 12 targets
```

เหตุผล:

- 10 targets เดิมยังน้อยไปสำหรับ demo ที่ดูน่าเชื่อถือ
- ถ้าเพิ่มอีก 12 แล้วบางตัว fail จะยังเหลือ usable targets ประมาณ 15-20
- ทำ candidate families 8 แบบ จะได้ประมาณ 160-176 target-candidate rows
- พอทำ demo แรกของ ranking/classification ได้

## CVE ที่แนะนำให้เพิ่ม

เลือก target ที่ไม่ซ้ำกับตัวอย่างเดิม และหลากหลาย product:

```text
drupal/CVE-2018-7600
weblogic/CVE-2020-14882
weblogic/CVE-2017-10271
jenkins/CVE-2018-1000861
joomla/CVE-2015-8562
phpmyadmin/CVE-2018-12613
solr/CVE-2019-0193
solr/CVE-2019-17558
thinkphp/5-rce
flask/ssti
shiro/CVE-2016-4437
tomcat/CVE-2017-12615
```

ถ้า `tomcat/CVE-2017-12615` มีในชุดเก่าแล้ว ให้เปลี่ยนเป็น:

```text
drupal/CVE-2019-6340
```

ถ้า path ไหนไม่มีใน Vulhub local ให้ agent หา replacement จาก Vulhub local ด้วย:

```bash
find ~/labs/vulhub -maxdepth 3 -iname '*CVE*' | sort
```

replacement ต้องบันทึกเหตุผลใน `metadata/target-selection.md`

## Sub-Agent Plan

ถ้า platform รองรับ sub-agent ให้แบ่งแบบนี้เพื่อทำงานเร็ว:

### Agent 1: Coordinator

หน้าที่:

- อ่านไฟล์นี้
- ตรวจ dataset เก่า
- เลือก targets สุดท้าย
- กำหนด IP/port ไม่ซ้ำ
- รวมผลจาก sub-agent อื่น
- ตัดสินใจ reuse หรือ rerun
- สร้าง final summary

ห้าม:

- normalize เองแบบลวก ๆ
- แก้ raw output
- สแกน public target

### Agent 2: Lab Runner

หน้าที่:

- ตรวจ Vulhub path
- เขียน compose override
- start/stop Docker project
- health check
- บันทึก target metadata

output:

```text
metadata/targets.jsonl
logs/lab-runner.log
```

### Agent 3: Recon Scanner

หน้าที่:

- nmap
- naabu
- httpx/httpx-toolkit
- service detection
- tech/title/status/header observation

output:

```text
raw/nmap/<target>/
raw/naabu/<target>/
raw/httpx-toolkit/<target>/
normalized/nmap/<target>.jsonl
normalized/naabu/<target>.jsonl
normalized/httpx-toolkit/<target>.jsonl
```

### Agent 4: Vulnerability Scanner

หน้าที่:

- nuclei
- nikto
- wapiti
- ZAP baseline
- OpenVAS/GVM ถ้าพร้อม

output:

```text
raw/nuclei/<target>/
raw/nikto/<target>/
raw/wapiti/<target>/
raw/zaproxy/<target>/
raw/openvas/<target>/
normalized/<tool>/<target>.jsonl
```

### Agent 5: Validation Scanner

หน้าที่:

- metasploit เฉพาะ module ที่ตรง CVE
- sqlmap เฉพาะ URL ที่มี parameter
- เก็บผลเป็น validation ไม่ใช่ finding ธรรมดา

output:

```text
raw/metasploit/<target>/
raw/sqlmap/<target>/
normalized/metasploit/<target>.jsonl
normalized/sqlmap/<target>.jsonl
records/validations.jsonl
```

### Agent 6: Normalizer + QA

หน้าที่:

- รวม raw เป็น records
- redact sensitive data
- ตรวจ JSONL
- ตรวจ duplicate record_id
- ตรวจ no public IP
- ตรวจ label leakage
- สร้าง manifest, checksums, quality-report

output:

```text
records/targets.jsonl
records/observations.jsonl
records/findings.jsonl
records/validations.jsonl
records/all-records.jsonl
derived/target-features.jsonl
derived/target-candidate-features.jsonl
labels/target-candidate-labels.jsonl
manifest.json
quality-report.json
checksums.sha256
DEC-RUN-SUMMARY-${RUN_DATE}.md
```

## Optimization Rules

เพื่อให้เร็วแต่ยังคุมคุณภาพ:

- update template/tools ครั้งเดียวก่อนเริ่ม ไม่ update ในทุก target
- pull Docker images ล่วงหน้าเท่าที่ทำได้
- รัน target พร้อมกันไม่เกิน 2-3 ตัว เพื่อไม่ให้เครื่องค้าง
- รัน recon เร็วก่อนเสมอ: `curl`, `httpx`, `naabu`
- ถ้า target health check ไม่ผ่านภายใน 120 วินาที ให้ mark `target_down` แล้วไปต่อ
- ตั้ง timeout ต่อ tool
- Nuclei ใช้ rate limit และ timeout
- Wapiti/ZAP/OpenVAS เป็นกลุ่มช้า ให้รันหลังจากได้ recon แล้ว
- OpenVAS ถ้า queue นานเกิน threshold ให้ mark `timeout` และ export status เท่าที่มี
- ห้ามให้ scanner failure ทำ pipeline ทั้ง batch หยุด
- normalize ทีละ target แล้วค่อย aggregate รวม

ค่าตั้งต้น:

```bash
HEALTH_TIMEOUT_SEC=120
FAST_TOOL_TIMEOUT_SEC=180
WEB_TOOL_TIMEOUT_SEC=600
OPENVAS_TIMEOUT_SEC=3600
MAX_PARALLEL_TARGETS=3
NUCLEI_RATE_LIMIT=20
```

## Scan Status ที่ต้องใช้

```text
success       = tool รันสำเร็จและมี output ที่ parse ได้
no_finding    = tool รันสำเร็จแต่ไม่พบ finding
failed        = tool รันล้มเหลว
timeout       = tool เกินเวลาที่กำหนด
skipped       = ข้ามอย่างมีเหตุผล เช่น ไม่มี parameter สำหรับ sqlmap
target_down   = target start ไม่ขึ้นหรือ health check ไม่ผ่าน
```

อย่าลบ failed/no_finding/skipped เพราะเป็นข้อมูลสำคัญของ dataset

## Fields ที่ต้องเก็บทุก Tool Run

```text
run_id
target_id
target_name
cve
tool_name
tool_version
command
started_at
finished_at
duration_sec
exit_code
scan_status
failure_reason
stdout_raw_file
stderr_raw_file
raw_report_file
normalized_file
raw_sha256
```

## Normalized Record Schema

ทุก record เป็น JSON object 1 บรรทัดใน JSONL:

```json
{
  "record_id": "string",
  "schema_version": "dec.dataset.v2",
  "run_id": "string",
  "record_type": "target|observation|finding|validation|tool_run",
  "target_id": "string",
  "target_name": "string",
  "cve": "string",
  "tool_name": "string",
  "scan_status": "success|no_finding|failed|timeout|skipped|target_down",
  "severity": "info|low|medium|high|critical|unknown",
  "confidence": "confirmed|high|medium|low|unknown",
  "evidence_type": "banner|http_response|template_match|scanner_alert|exploit_validation|port_scan|tool_error",
  "title": "string",
  "description": "string",
  "host": "string",
  "port": 0,
  "url": "string",
  "service": "string",
  "technology": [],
  "template_id": "string",
  "module_id": "string",
  "plugin_id": "string",
  "raw_file": "string",
  "raw_sha256": "string"
}
```

ถ้า field ไม่มีค่า ให้ใช้ `null`, `[]`, หรือ `"unknown"` ตามชนิดข้อมูล ห้ามเดาให้ดูดี

## Feature ที่แนะนำสำหรับ Demo แรก

ระดับ target:

```text
open_port_count
web_port_count
http_status_family
server_header_family
technology_flags
has_login_page
has_upload_endpoint
has_parameterized_url
nuclei_finding_count_by_severity
nikto_issue_count
zap_alert_count_by_risk
wapiti_vulnerability_count
service_product_family
scanner_coverage_count
scanner_failure_count
```

ระดับ target + exploit candidate:

```text
candidate_family
candidate_product_match_score
candidate_cve_match_score
candidate_service_match_score
candidate_port_match_score
candidate_technology_match_score
candidate_scanner_signal_score
candidate_validation_available
```

ห้ามใช้ feature ที่เฉลย label เช่น:

```text
known_vulnerable
exploit_succeeded
session_opened
ground_truth_positive
label
```

## Label สำหรับ Demo แรก

แยก label ไว้ใน:

```text
labels/target-candidate-labels.jsonl
```

label แนะนำ:

```text
positive_family_match
negative_family_mismatch
unknown
validated_exploit_succeeded
validated_no_session
validated_not_vulnerable
```

สำหรับ demo แรกใช้ `positive_family_match` ได้ แต่ต้องเขียนใน README ชัดว่าเป็น weak label จาก Vulhub ground truth ไม่ใช่ exploit success label ทั้งหมด

## Commands ที่ Agent ควรรันก่อนสแกน

```bash
mkdir -p "$REPORT_ROOT" "$RUN_ROOT"

docker --version | tee "${REPORT_ROOT}/docker-version.txt"
docker compose version | tee "${REPORT_ROOT}/docker-compose-version.txt"

nmap --version | tee "${REPORT_ROOT}/nmap-version.txt" || true
naabu -version | tee "${REPORT_ROOT}/naabu-version.txt" || true
httpx -version | tee "${REPORT_ROOT}/httpx-version.txt" || httpx-toolkit -version | tee "${REPORT_ROOT}/httpx-version.txt" || true
nuclei -version | tee "${REPORT_ROOT}/nuclei-version.txt" || true
nikto -Version | tee "${REPORT_ROOT}/nikto-version.txt" || true
wapiti --version | tee "${REPORT_ROOT}/wapiti-version.txt" || true
msfconsole -v | tee "${REPORT_ROOT}/metasploit-version.txt" || true
sqlmap --version | tee "${REPORT_ROOT}/sqlmap-version.txt" || true
gvm-cli --version | tee "${REPORT_ROOT}/gvm-cli-version.txt" || true

nuclei -update-templates | tee "${REPORT_ROOT}/nuclei-template-update.txt" || true
```

## Commands สำหรับบันทึกไฟล์ Prompt นี้บน Kali

ถ้าไฟล์นี้อยู่ใน shared folder แล้ว ให้ copy เข้า reports:

```bash
cp /media/sf_kali-share/DEC-FAST-SUBAGENT-DATASET-PROMPT.md /home/kali/reports/
```

ถ้าอยู่ใน repo บน Windows ให้ copy ผ่าน shared folder ก่อน แล้วค่อยใช้คำสั่งด้านบน

## Quality Gate

ห้ามถือว่างานเสร็จจนกว่า `quality-report.json` ผ่านเงื่อนไข:

```text
valid = true
jsonl_invalid_lines = 0
duplicate_record_ids = 0
missing_label_refs = 0
label_leakage_fields = 0
unredacted_sensitive_values = 0
public_ips = 0
targets >= 20 สำหรับ demo แรก
target_candidate_rows >= 160 สำหรับ demo แรก
```

ถ้ายังไม่ผ่าน ให้เขียน `DEC-RUN-SUMMARY-${RUN_DATE}.md` ว่าไม่ผ่านเพราะอะไร และต้องแก้ต่ออย่างไร

## Git Handoff

หลัง QA ผ่าน ให้เตรียม commit ไป branch `Dec`:

```bash
git status
git add generated/ outputs/ README.md
git commit -m "Add Dec reproducible scanner dataset run"
git push origin Dec
```

ถ้า Git มี conflict หรือ branch ไม่ตรง ให้หยุดและรายงาน ไม่ใช้ force push

## Final Report ที่ต้องตอบกลับ

เมื่อ agent ทำงานเสร็จ ต้องสรุป:

- ใช้ข้อมูลเก่าหรือรันใหม่
- targets ทั้งหมดกี่ตัว
- CVE ที่เพิ่มมีอะไร
- tool ไหนสำเร็จ/ไม่เจอ/failed/timeout
- จำนวน records: targets, observations, findings, validations
- dataset path
- quality-report valid หรือไม่
- ข้อจำกัดที่ยังเหลือ
- commit hash ถ้ามีการ push Git

## ข้อความสั้นสำหรับเริ่ม Agent

```text
อ่าน DEC-FAST-SUBAGENT-DATASET-PROMPT.md แล้วทำ dataset ต่อจากของเก่าก่อน ถ้าของเก่าใช้ไม่ได้ให้รัน Vulhub เพิ่ม 12 CVE ตามรายการ แบ่งงานด้วย sub-agent ถ้ามี capability เก็บ raw + normalized ทุก tool และทุกสถานะ success/no_finding/failed/timeout/skipped ห้ามสแกน public target ห้ามสร้างข้อมูลปลอม สุดท้ายต้องสร้าง manifest, quality-report, checksums และสรุปผลพร้อม path
```
