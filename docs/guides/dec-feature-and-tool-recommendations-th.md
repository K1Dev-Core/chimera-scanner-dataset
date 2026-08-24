# Feature และเครื่องมือที่แนะนำสำหรับ Dataset Branch Dec

## 1. เป้าหมายของ Dataset

โปรเจค Exploit-DL มีเป้าหมายให้ระบบรับข้อมูลที่สังเกตได้จากเป้าหมายก่อนโจมตี แล้วจัดอันดับ exploit ที่มีโอกาสสำเร็จมากที่สุด จากนั้นจึงทดลอง exploit ในห้องแล็บและบันทึกผลจริงกลับมาเป็นข้อมูลสำหรับประเมินหรือฝึกโมเดลรอบถัดไป

```text
Vulhub target
    -> Recon และ fingerprint
    -> Vulnerability findings
    -> Exploit candidate generation
    -> Feature vector ต่อ target + candidate
    -> Model ranking
    -> Metasploit validation
    -> Outcome label และ feedback
```

หนึ่งแถวของชุดข้อมูลสำหรับโมเดลจัดอันดับจึงควรหมายถึง:

```text
target_id + candidate_exploit
```

ตัวอย่างเช่น target `struts2_s2045` มี candidate หลายตัว ได้แก่ exploit สำหรับ Struts2, Spring และ Tomcat แต่ละ candidate จะมี feature ของเป้าหมายชุดเดียวกันและ feature ความเข้ากันได้ของ candidate ต่างกัน ส่วน label มาจากผล validation ที่แยกเก็บไว้อย่างชัดเจน

## 2. หลักการแบ่งข้อมูล 4 ชั้น

### 2.1 Ground truth

Ground truth คือข้อมูลที่ผู้สร้างแล็บรู้อยู่แล้ว เช่น CVE ที่ Vulhub จำลอง product และ affected version ข้อมูลนี้ใช้ตรวจคำตอบและสร้าง label แต่ห้ามป้อนเข้าโมเดลเมื่อโมเดลมีหน้าที่ทำนาย CVE หรือ exploit family

ฟิลด์แนะนำ:

- `target_id`
- `ground_truth_cve`
- `ground_truth_product`
- `ground_truth_version`
- `ground_truth_family`
- `lab_path`
- `docker_image`
- `is_patched`

### 2.2 Pre-exploit observations

เป็นสิ่งที่เครื่องมือค้นพบก่อนเรียก exploit เช่น port, banner, service, technology และ scanner findings ข้อมูลชั้นนี้เป็นแหล่ง feature หลักของโมเดล

### 2.3 Exploit candidate metadata

เป็นคุณสมบัติของ exploit ที่กำลังพิจารณา เช่น platform, architecture, CVE reference, module rank และการรองรับคำสั่ง `check` แล้วนำมาเปรียบเทียบกับ observation ของเป้าหมาย

### 2.4 Post-exploit outcomes

เป็นผลที่เกิดหลังทดลอง candidate แล้ว เช่น check vulnerable, code execution, session opened, runtime และ error ข้อมูลนี้เป็น label หรือข้อมูลวิเคราะห์ผล ห้ามนำกลับไปเป็น input ของโมเดลในรอบการตัดสินใจเดียวกัน

## 3. Feature ชุดหลักที่แนะนำสำหรับ Dec

### 3.1 Attack surface features

| Feature | ความหมาย | แหล่งข้อมูล |
|---|---|---|
| `open_tcp_port_count` | จำนวน TCP ports ที่เปิด | Naabu, Nmap |
| `open_udp_port_count` | จำนวน UDP ports ที่เปิด | Nmap |
| `http_service_count` | จำนวน HTTP/HTTPS endpoints | HTTPX, Nmap |
| `service_observation_count` | จำนวน service observations ที่ parser อ่านได้ | Nmap |
| `unique_service_count` | จำนวน service names ที่ไม่ซ้ำ | Nmap |
| `unique_product_count` | จำนวน products ที่ไม่ซ้ำ | Nmap |
| `unique_cpe_count` | จำนวน CPE ที่ไม่ซ้ำ | Nmap |

ไม่ควรใช้หมายเลข IP, host port ของ Docker หรือ `target_id` เป็นตัวเลขฝึกโมเดล เพราะโมเดลอาจจำแล็บแทนที่จะเรียนรู้พฤติกรรมของระบบ

### 3.2 Banner และ version features

| Feature | ความหมาย | แหล่งข้อมูล |
|---|---|---|
| `banner_present` | มี banner ดิบหรือไม่ | Nmap, Netcat, WhatWeb |
| `banner_length` | ความยาว banner หลังลบข้อมูลอ่อนไหว | Nmap, WhatWeb |
| `product_detected` | ตรวจพบ product หรือไม่ | Nmap, HTTPX |
| `version_detected` | ตรวจพบ version หรือไม่ | Nmap, HTTPX |
| `version_token_count` | จำนวน token ใน version string | parser |
| `banner_embedding` | vector จาก banner-as-text | tokenizer/encoder |

สำหรับสาย Deep Learning ตามแนวคิดใน PDF ควรเก็บ `raw_banner` ไว้ใน evidence store แล้วสร้างข้อความที่ผ่านการลดรูปเป็น input แยกต่างหาก วิธีนี้ช่วยให้ทดสอบ generalization กับ version ที่ไม่เคยเห็นได้ดีกว่าการ One-Hot version ทุกค่า แต่ต้องลบ IP, hostname, timestamp และ session identifier ก่อน tokenize

### 3.3 Web fingerprint features

| Feature | ความหมาย | แหล่งข้อมูล |
|---|---|---|
| `http_observation_count` | จำนวน HTTP observations | HTTPX |
| `status_2xx_count` | จำนวน endpoint ที่ตอบ 2xx | HTTPX |
| `status_3xx_count` | จำนวน redirect | HTTPX |
| `status_4xx_count` | จำนวน client errors | HTTPX |
| `status_5xx_count` | จำนวน server errors | HTTPX |
| `unique_technology_count` | จำนวน web technologies ที่ไม่ซ้ำ | HTTPX, WhatWeb |
| `title_present` | มี page title หรือไม่ | HTTPX |
| `server_header_present` | มี HTTP Server header หรือไม่ | HTTPX, ZAP |
| `tls_enabled` | endpoint ใช้ TLS หรือไม่ | HTTPX, testssl.sh |
| `redirect_count` | จำนวน redirect ที่พบ | HTTPX, ZAP |

ค่า `open_ports` และ `observed_technologies` แบบข้อความยังเก็บไว้เพื่อ audit ได้ แต่เมื่อมี target เพียง 10 ตัวควรใช้จำนวนหรือ vocabulary ที่ควบคุมแล้วในการทดลองโมเดล เพื่อลดการจำ product โดยตรง

### 3.4 Vulnerability finding features

| Feature | ความหมาย | แหล่งข้อมูล |
|---|---|---|
| `scanner_finding_count` | จำนวน findings หลัง deduplicate | Nuclei, OpenVAS, ZAP, Wapiti, Nikto |
| `critical_count` | findings ระดับ critical | scanners |
| `high_count` | findings ระดับ high | scanners |
| `medium_count` | findings ระดับ medium | scanners |
| `low_count` | findings ระดับ low | scanners |
| `info_count` | findings ระดับ informational | scanners |
| `unknown_severity_count` | findings ที่ map severity ไม่ได้ | parser |
| `cve_finding_count` | findings ที่มี CVE reference | Nuclei, OpenVAS |
| `cwe_finding_count` | findings ที่มี CWE reference | ZAP, Wapiti, Nuclei |
| `generic_hardening_finding_count` | missing headers และ hardening findings | ZAP, Nikto, Nuclei |
| `evidence_tool_count` | จำนวนเครื่องมือที่มีหลักฐานต่อ target | aggregator |
| `scanner_agreement_count` | จำนวนเครื่องมือที่ชี้ไปยัง CVE/family เดียวกัน | aggregator |
| `max_cvss` | CVSS สูงสุดที่รายงาน | Nuclei, OpenVAS |
| `mean_qod` | ค่าเฉลี่ย Quality of Detection | OpenVAS |

ห้ามนับ alerts ดิบอย่างเดียว เพราะ missing header จำนวนมากอาจกลบ CVE match หนึ่งรายการ ควรแยก `CVE-specific`, `CWE-specific` และ `generic-hardening` ออกจากกัน

### 3.5 Candidate compatibility features

นี่คือ feature สำคัญสำหรับงานจัดอันดับ exploit เพราะช่วยตอบว่า exploit ตัวนี้เข้ากับเป้าหมายที่สังเกตได้หรือไม่

| Feature | ความหมาย |
|---|---|
| `candidate_family` | family ของ candidate ใช้เป็น key หรือ categorical feature ที่ควบคุม |
| `candidate_family_evidence_count` | จำนวน finding fields ที่มี evidence ตรงกับ candidate family |
| `candidate_cve_match_count` | จำนวน CVE findings ที่ตรงกับ reference ของ candidate |
| `candidate_cwe_match_count` | จำนวน CWE findings ที่ตรงกับ candidate |
| `candidate_service_match` | service ของ candidate ตรงกับ service ที่พบหรือไม่ |
| `candidate_product_match` | product ที่ candidate รองรับตรงกับ fingerprint หรือไม่ |
| `candidate_platform_match` | OS/platform ตรงกันหรือไม่ |
| `candidate_arch_match` | architecture ตรงกันหรือไม่ |
| `candidate_port_match` | default/required port เปิดอยู่หรือไม่ |
| `candidate_ssl_compatible` | ค่า SSL ของ module เข้ากับ endpoint หรือไม่ |
| `candidate_has_check` | module รองรับ `check` หรือไม่ |
| `candidate_module_rank` | Metasploit module rank ที่ map เป็นค่าควบคุม |
| `candidate_required_option_count` | จำนวน options ที่ต้องระบุก่อนรัน |

`candidate_family_evidence_count` ควรนับจาก field ที่ scanner สร้างจริง เช่น `title`, `category`, `description`, `template_id`, `matcher_name`, `tags`, CVE และ CWE ไม่ควรใช้ ground-truth description ของ Vulhub ในการนับ

### 3.6 Validation และ outcome labels

| Field | ความหมาย | ใช้เป็น |
|---|---|---|
| `check_status` | vulnerable, safe, unsupported, error, unknown | label/analysis |
| `exploit_attempted` | มีการเรียก module จริงหรือไม่ | audit |
| `code_execution_observed` | มี marker command ที่ตรวจสอบได้หรือไม่ | label |
| `session_opened` | Metasploit เปิด session ได้หรือไม่ | label หลัก |
| `exploit_success_observed` | สรุปความสำเร็จตามนิยามโครงการ | label หลัก |
| `attempt_index` | เป็น candidate ลำดับที่เท่าไร | metric |
| `runtime_ms` | เวลาที่ module ใช้ | metric |
| `error_category` | timeout, connection, bad-config, not-vulnerable, crash | analysis |
| `evidence_sha256` | hash ของ console log หรือ RPC response | audit |

แนะนำให้นิยาม label แบบสามค่า:

- `true`: มี session หรือ code-execution marker ตามเกณฑ์ที่กำหนด
- `false`: ทดลองครบและมีหลักฐานว่าไม่สำเร็จ
- `null`: ไม่ได้ทดลอง, module ใช้ไม่ได้ หรือผลยังไม่พอสรุป

`null` ห้ามแปลงเป็น `false` อัตโนมัติ เพราะ "ยังไม่ได้ทดสอบ" ไม่เท่ากับ "ทดสอบแล้วล้มเหลว"

## 4. Feature ชุดขั้นต่ำที่ควรเริ่มใช้

สำหรับ Dataset Dec ที่มี 10 targets ควรเริ่มจากตาราง feature ขนาดเล็กก่อน:

```text
open_tcp_port_count
http_observation_count
service_observation_count
unique_technology_count
scanner_finding_count
critical_count
high_count
medium_count
low_count
info_count
unknown_severity_count
cve_finding_count
generic_hardening_finding_count
evidence_tool_count
candidate_family_evidence_count
candidate_cve_match_count
candidate_service_match
candidate_platform_match
candidate_port_match
candidate_has_check
validation_verified_count
validation_detected_count
validation_not_detected_count
validation_inconclusive_count
```

เมื่อมีอย่างน้อย 30-100 targets และมีหลาย version ต่อ product จึงค่อยทดลอง banner-as-text, technology vocabulary, embeddings และโมเดล Deep Learning อย่างจริงจัง ระยะปัจจุบันควรมี Random Forest หรือ XGBoost เป็น baseline เพื่อพิสูจน์ว่า pipeline และ label ถูกต้องก่อน

## 5. Field ที่ต้องตัดออกจาก Model Matrix

- `target_id`
- raw IP และ host port
- `lab_path`, `docker_image`, container name
- `ground_truth_cve`, `ground_truth_product`, `ground_truth_family`
- `rank`, `rank_score`, `is_recommended`, `family_risk_prior` เมื่อค่าเหล่านี้ใช้สร้าง label
- `session_opened`, `exploit_success_observed` เมื่อกำลังทำนายก่อนยิง exploit
- timestamp และ raw path ที่บอก identity ของแล็บ
- ข้อความจาก README ของ Vulhub ที่เปิดเผย CVE โดยตรง

ข้อมูลเหล่านี้ยังเก็บในไฟล์สำหรับ join และ audit ได้ แต่ training code ต้อง drop ก่อนสร้าง `X`

## 6. เครื่องมือที่ใช้จริงและบทบาทใน Dataset

### 6.1 ชุดหลักที่ควรใช้ทุก target

| เครื่องมือ | สแกนหาอะไร | Report ที่ควรเก็บ | Record/feature หลัก |
|---|---|---|---|
| Naabu | TCP ports ที่เปิดอย่างรวดเร็ว | JSONL | `port_observation`, open port count |
| Nmap | port, protocol, service, product, version, CPE, OS hints | XML และ normal output | `service_observation`, banner/version features |
| HTTPX ของ ProjectDiscovery | HTTP status, title, server, technology, TLS | JSONL | `web_observation`, HTTP features |
| Nuclei | template-based findings, CVE, CWE, severity, matcher | JSONL พร้อม request/response hash | `scanner_finding`, CVE evidence |
| OpenVAS/GVM | network vulnerability tests, CVE, CVSS, QoD | GMP XML | `scanner_finding`, severity/CVE/QoD |
| OWASP ZAP | spider, passive scan และ web alerts | JSON/XML | web findings, CWE, confidence |
| Nikto | web misconfiguration, outdated server และ risky files | JSON/XML/text | hardening findings |

ลำดับที่เหมาะสมคือ Naabu -> Nmap -> HTTPX -> Nuclei/OpenVAS -> ZAP/Nikto เพราะแต่ละขั้นใช้ผลจากขั้นก่อนหน้าเพื่อลดการยิง request ที่ไม่จำเป็น

### 6.2 ใช้เฉพาะกรณีที่เหมาะสม

| เครื่องมือ | ใช้เมื่อ | ข้อมูลที่ได้ |
|---|---|---|
| Wapiti | ต้องการ DAST แบบ black-box เพิ่มจาก ZAP | vulnerability category, URL, parameter, method, payload evidence |
| sqlmap | endpoint มี GET/POST/cookie parameter และต้องยืนยัน SQLi | parameter, injection technique, DBMS, final verdict |
| Metasploit | มี candidate module และต้องการ validation ในแล็บ | check result, module, options, session, runtime, errors |
| AutoRecon | ต้องการ orchestration/recon artifact หลายชนิด | references ไปยัง Nmap, directory discovery และ tool logs |
| Subfinder/Amass | target เป็นโดเมนที่ได้รับอนุญาตและต้องสำรวจ subdomain | domain observation และ discovery source |

AutoRecon ไม่ควรถูกนับซ้ำกับ Nmap ที่มันเรียกภายใน ให้ normalize artifact ต้นทางแล้วอ้าง parent run id แทน

## 7. เครื่องมือที่แนะนำเพิ่มสำหรับโปรเจคนี้

### 7.1 WhatWeb

ใช้เก็บ web technology, server/plugin fingerprints และ raw HTTP hints ในรูป JSON เหมาะกับ feature ที่ HTTPX อาจตรวจไม่ครบ โดยเฉพาะ CMS, framework และ plugin identity

แนะนำให้เก็บ:

- `target`, `http_status`, `plugins`, `version`, `string`, `certainty`
- raw JSON และ normalized `web_observation`

### 7.2 testssl.sh

ใช้เก็บ protocol, cipher, certificate และ TLS vulnerabilities ทำให้แยกความเข้ากันได้ของ candidate ที่ต้องใช้ SSL/TLS ได้ดีขึ้น

แนะนำให้เก็บ JSON และสร้าง feature เช่น `tls_version_count`, `weak_cipher_count`, `cert_expired`, `heartbleed_detected`

### 7.3 Katana หรือ ffuf

ใช้ค้นหา URL paths, forms และ parameters ก่อนส่งต่อให้ ZAP, Wapiti หรือ sqlmap ข้อมูลที่ได้ควรเป็น endpoint inventory ไม่ใช่ vulnerability label

แนะนำให้เก็บ:

- URL ที่ canonicalize แล้ว
- HTTP method
- parameter names
- content type
- status code
- discovery source

ควรจำกัด scope และ rate ในห้องแล็บ เพราะเครื่องมือประเภท content discovery สร้าง request จำนวนมาก

### 7.4 Syft + Trivy หรือ Grype

ใช้กับ Docker image ของ Vulhub เพื่อสร้าง SBOM และตรวจ package/version ภายใน container ข้อมูลนี้เหมาะกับ ground truth enrichment และตรวจความถูกต้องของ lab มากกว่าจะใช้เป็น feature ของ black-box model เพราะในการสแกนเซิร์ฟเวอร์จริงมักอ่าน image ภายในไม่ได้

แนะนำให้เก็บ:

- Syft CycloneDX/SPDX JSON
- Trivy/Grype JSON
- package, version, purl, CPE, CVE, fixed version

### 7.5 SearchSploit/Exploit-DB และ Metasploit module metadata

ใช้สร้างรายชื่อ exploit candidates จาก CVE, product และ platform โดยไม่ต้องเขียน mapping ทุกตัวเอง ข้อมูล candidate ควรแยกจาก scanner findings และ ground truth

แนะนำให้เก็บ:

- exploit/module identifier
- CVE references
- platform, architecture, service/port hints
- module rank
- `check` support
- required options

### 7.6 tcpdump หรือ mitmproxy

ใช้เก็บหลักฐาน dynamic ระหว่าง scanner หรือ exploit กับเป้าหมาย เหมาะกับการตรวจย้อนหลังและทำ sequence feature ในอนาคต

- `tcpdump`: เก็บ PCAP สำหรับ protocol/timing/flow analysis
- `mitmproxy`: เก็บ HTTP request/response flow ในแล็บที่ควบคุมได้

ข้อมูลนี้มีขนาดใหญ่และอาจมี secrets จึงควรเก็บเป็น optional evidence, ทำ redaction และบันทึก hash ไม่ควรใส่ payload ดิบทั้งหมดลง feature table

### 7.7 MLflow และ DVC

สองตัวนี้ไม่ใช่ scanner แต่ช่วยให้ผลงานวิจัยทำซ้ำได้:

- DVC version ชุด raw/normalized/labels โดยไม่ยัดไฟล์ใหญ่ทั้งหมดไว้ใน Git
- MLflow บันทึก experiment, parameters, metrics, artifacts และ model version

Git repository ควรเก็บ schema, manifest, parser, checksums และตัวอย่างข้อมูลขนาดเล็ก ส่วน raw PCAP/report ขนาดใหญ่ควรเก็บใน DVC remote หรือ object storage

## 8. ชุดเครื่องมือที่แนะนำตามระดับ

### Minimum viable dataset

```text
Vulhub + Docker
Naabu + Nmap + HTTPX
Nuclei
Metasploit
Python parser + pandas
```

### ชุดที่แนะนำสำหรับ Dec

```text
Vulhub + Docker
Naabu + Nmap + HTTPX + WhatWeb
Nuclei + OpenVAS
ZAP + Nikto + Wapiti
sqlmap เฉพาะ SQLi target
Metasploit สำหรับ candidate validation
Syft + Trivy สำหรับ lab ground truth
DVC + MLflow สำหรับ data/model versioning
```

### ชุดวิจัยระยะต่อไป

```text
Katana/ffuf สำหรับ endpoint inventory
testssl.sh สำหรับ TLS features
tcpdump/mitmproxy สำหรับ dynamic evidence
patched negative controls
หลาย version ต่อ product
banner-as-text model และ baseline model
```

## 9. รูปแบบโฟลเดอร์ที่แนะนำ

```text
dataset/
  raw/
    <tool>/<scan-date>/<target-id>/...
  normalized/
    targets.jsonl
    observations.jsonl
    findings.jsonl
    candidates.jsonl
    validations.jsonl
  derived/
    target-features.jsonl
    target-candidate-features.jsonl
  labels/
    target-candidate-labels.jsonl
  manifests/
    manifest.json
    checksums.sha256
    quality-report.json
```

ทุก record ควรมี `schema_version`, `record_id`, `dataset_record_type`, `target_id`, `tool`, `source_path`, `scan_timestamp`, `parser_version` และ `parser_status`

## 10. การแบ่ง Train/Test และการวัดผล

แถว candidate ของ target เดียวกันต้องอยู่ split เดียวกัน ควรใช้ `GroupShuffleSplit`, `GroupKFold` หรือ Leave-One-Target-Out โดย group ด้วย target หรือ product family ห้าม random split รายแถว

ตัวชี้วัดหลักของโปรเจคควรเป็น:

- `Success@1`, `Success@3`, `Success@5`
- `MRR` หรืออันดับเฉลี่ยของ exploit ที่สำเร็จตัวแรก
- `average_attempts_to_success`
- อัตรา `session_opened`
- runtime รวมก่อนสำเร็จ
- macro F1/AUC เป็นตัวชี้วัดประกอบ ไม่ใช่คำตอบหลัก

baseline ที่ควรเปรียบเทียบ:

1. สุ่มลำดับ
2. ลำดับคงที่
3. exact CVE/module match
4. severity/evidence heuristic
5. Random Forest หรือ XGBoost
6. banner-as-text Deep Learning model

## 11. ข้อสรุปสำหรับ Branch Dec

Feature ของ Dec ควรตอบสองคำถามแยกกัน: "เป้าหมายมีลักษณะอะไร" และ "candidate นี้เข้ากับลักษณะนั้นเพียงใด" ส่วนผล exploit ต้องอยู่ฝั่ง label ไม่ใช่ feature การออกแบบแบบนี้จะทำให้โมเดลเรียนจากหลักฐานที่หาได้ก่อนโจมตีจริง และช่วยให้ผล Success@k หรือ attempts-to-success มีความหมายทางวิจัย

สำหรับข้อมูล 10 CVEs ปัจจุบัน ให้ใช้ feature counts และ compatibility features เป็น baseline ก่อน เพิ่ม WhatWeb, testssl.sh, Syft/Trivy, DVC และ MLflow เพื่อยกระดับคุณภาพข้อมูล เมื่อมี target และ version มากพอจึงทดลอง Deep Learning จาก banner ดิบและเปรียบเทียบกับ baseline อย่างตรงไปตรงมา
