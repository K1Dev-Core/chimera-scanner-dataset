# บทความสรุปเครื่องมือที่ใช้จริงในการสร้าง Vulnerability Dataset

เอกสารนี้อธิบายเครื่องมือที่ใช้จริงในชุดทดลอง Kali Linux + Docker + Vulhub โดยเน้น 4 คำถามที่ต้องตอบให้ได้สำหรับทุกเครื่องมือ:

1. เครื่องมือนั้นสแกนหาอะไร
2. มันตรวจอย่างไร
3. รายงานที่ได้มีข้อมูลอะไร
4. ควรนำผลส่วนใดไปสร้าง dataset และตีความอย่างไร

ขอบเขตการทดลองคือระบบที่ได้รับอนุญาตเท่านั้น เช่น Vulhub ในเครื่องทดลอง หรือเซิร์ฟเวอร์ที่เจ้าของระบบอนุญาตให้สแกน การสแกนเชิงรุก โดยเฉพาะ sqlmap, Nuclei, OpenVAS และ Metasploit อาจทำให้ระบบช้า เปลี่ยนข้อมูล หรือหยุดทำงานได้

## 1. ภาพรวมระบบทดลอง

งานนี้ไม่ได้ใช้เครื่องมือเพียงตัวเดียวแล้วสรุปว่าเป้าหมาย “มีช่องโหว่” แต่ใช้เครื่องมือหลายชั้นเพื่อสร้างหลักฐานตั้งแต่การค้นหาบริการไปจนถึงการยืนยันช่องโหว่

ลำดับการทำงานที่ใช้คือ:

```text
Docker/Vulhub
    สร้างระบบที่ทราบคำตอบจริงว่าเป็น CVE ใด
        |
        v
Naabu / Nmap
    ตรวจพอร์ตและบริการที่เข้าถึงได้
        |
        v
httpx-toolkit
    ตรวจว่า HTTP ตอบหรือไม่ พร้อมเก็บสถานะและเทคโนโลยี
        |
        v
Nuclei / Nikto / ZAP / Wapiti / OpenVAS
    ตรวจหาจุดอ่อนด้วยวิธีและฐานความรู้ที่แตกต่างกัน
        |
        v
sqlmap / Metasploit
    ตรวจเฉพาะช่องโหว่และยืนยันความเป็นไปได้ในห้องทดลอง
        |
        v
Raw reports -> Normalized JSONL
        |
        v
DefectDojo / Faraday / Reconmap
    จัดเก็บ เชื่อมโยง ลดรายการซ้ำ และบริหารโครงการ
```

จุดสำคัญคือผลจากแต่ละชั้นมีความหมายไม่เท่ากัน การเปิดพอร์ตได้ไม่ใช่หลักฐานว่ามีช่องโหว่ และการพบชื่อซอฟต์แวร์เวอร์ชันเก่าก็ยังไม่ใช่หลักฐานว่าช่องโหว่นั้น exploit ได้จริง

## 2. ระดับของหลักฐานที่ควรใช้ใน Dataset

เพื่อไม่ให้ข้อมูลปนกัน ควรแบ่งผลลัพธ์เป็น 5 ระดับดังนี้

| ระดับ | ความหมาย | ตัวอย่างเครื่องมือ | label ที่แนะนำ |
|---|---|---|---|
| 1. Reachability | ติดต่อ host หรือ port ได้ | Naabu, Nmap | `asset_observation` |
| 2. Fingerprint | ระบุ service, product หรือ technology ได้ | Nmap, httpx-toolkit | `technology_observation` |
| 3. Potential finding | พบเงื่อนไขที่น่าสงสัย แต่ยังไม่ยืนยัน | Nikto, ZAP passive, OpenVAS version check | `potential` |
| 4. Vulnerability match | request/response ตรงกับ template หรือการทดสอบช่องโหว่ | Nuclei, Wapiti, OpenVAS, sqlmap | `detected` |
| 5. Exploit verified | ยืนยันผลกระทบได้ใน lab โดยมีหลักฐาน | Metasploit หรือการตรวจเฉพาะทาง | `verified` |

นอกจากนี้ต้องมีค่า `scanner_result` แยกจาก ground truth ของ Vulhub เช่น:

```json
{
  "target_id": "struts2_s2045",
  "ground_truth_cve": "CVE-2017-5638",
  "tool": "nikto",
  "scanner_result": "potential",
  "detected_cve": null,
  "finding": "Jetty version appears outdated",
  "verification": "not_verified"
}
```

ตัวอย่างนี้หมายความว่า lab ถูกสร้างให้มี CVE-2017-5638 จริง แต่ Nikto ไม่ได้ตรวจพบ CVE นั้นโดยตรง Nikto พบเพียง Jetty เก่าและการตั้งค่า HTTP ที่ไม่แข็งแรง จึงห้ามบันทึกว่า Nikto ตรวจพบ CVE-2017-5638

## 3. Docker และ Vulhub: ตัวสร้าง Ground Truth

### Docker ทำหน้าที่อะไร

Docker ไม่ใช่ vulnerability scanner แต่เป็นระบบรัน container ที่แยกแอปพลิเคชันและ dependency ออกจากเครื่องหลัก ในงานนี้ Docker ใช้เปิดระบบที่มีช่องโหว่แต่ละตัวด้วย image และ configuration ที่ Vulhub เตรียมไว้

ตัวอย่าง:

```bash
cd ~/labs/vulhub/struts2/s2-045
docker compose -f docker-compose.host.yml -p vh_struts2_s2045 up -d
docker compose -f docker-compose.host.yml -p vh_struts2_s2045 ps
```

คำสั่ง `up -d` สร้าง network และ container แล้วรันเบื้องหลัง ส่วน `ps` ใช้ตรวจสถานะและ port mapping เช่น:

```text
127.0.0.11:18080->8080/tcp
```

ความหมายคือ scanner บน Kali ติดต่อ `127.0.0.11:18080` และ Docker ส่ง traffic ต่อไปยัง port `8080` ภายใน container

### Vulhub ทำหน้าที่อะไร

Vulhub เป็นชุด environment สำหรับช่องโหว่ที่ทราบ CVE หรือพฤติกรรมเปราะบางอยู่แล้ว จึงทำหน้าที่เป็น ground truth ของการทดลอง ตัวอย่างเช่น directory `struts2/s2-045` ระบุว่าระบบถูกจัดเตรียมสำหรับ S2-045 หรือ CVE-2017-5638

ข้อมูลจาก Vulhub ที่ควรเก็บในตารางเป้าหมายคือ:

- `target_id` เช่น `struts2_s2045`
- `ground_truth_cve` เช่น `CVE-2017-5638`
- `product` เช่น Apache Struts 2
- `vulhub_path` เช่น `struts2/s2-045`
- `host_ip` และ `host_port`
- `container_image`
- `started_at` และ `stopped_at`
- `compose_project`

เมื่อต้องการปิด lab ให้ใช้ compose project และ compose file เดิม:

```bash
cd ~/labs/vulhub/struts2/s2-045
docker compose -f docker-compose.host.yml -p vh_struts2_s2045 down -v
```

`down -v` จะลบ container, network และ volume ของ project นั้น จึงควรเก็บ report และ metadata ก่อนปิด

## 4. Naabu: ค้นหาพอร์ตแบบรวดเร็ว

### สแกนหาอะไร

Naabu ตรวจว่า TCP port ใดของเป้าหมายตอบสนอง จุดประสงค์หลักคือค้นหา attack surface ระดับ network ไม่ได้ตรวจช่องโหว่ของเว็บโดยตรง

ตัวอย่างคำสั่ง:

```bash
naabu -host "${LAB_HOST}" -p "${LAB_PORT}" -json \
  -o "${RAW_NAABU_DIR}/scan.jsonl"
```

ถ้าเป็นเซิร์ฟเวอร์จริงที่ได้รับอนุญาตและต้องการค้นหาหลายพอร์ต สามารถกำหนดรายการหรือช่วงพอร์ตตาม scope ได้ แต่ในการสร้าง dataset ของ Vulhub เรารู้อยู่แล้วว่า publish พอร์ตใด จึงระบุพอร์ตเพื่อให้ผลทดลองทำซ้ำได้

### ทำงานอย่างไร

Naabu ส่ง packet เพื่อตรวจสถานะ TCP port แล้วดูว่าปลายทางตอบรับการเชื่อมต่อหรือไม่ วิธีตรวจอาจขึ้นกับสิทธิ์ของผู้ใช้และระบบปฏิบัติการ แต่สาระสำคัญคือมันตอบคำถามว่า “มีบริการรับ connection ที่ host:port นี้หรือไม่”

### Report มีอะไร

JSONL ของ Naabu มักประกอบด้วย host, IP, port, protocol และ timestamp แต่ละบรรทัดเป็น observation หนึ่งรายการ จึงเหมาะกับ ingestion pipeline

ตัวอย่างเชิงแนวคิด:

```json
{"host":"127.0.0.11","ip":"127.0.0.11","port":18080,"protocol":"tcp"}
```

### นำไปใช้ใน Dataset อย่างไร

ใช้สร้างตาราง `services` หรือ `open_ports` โดย label ว่า port เปิด ไม่ใช่ vulnerability positive ฟิลด์สำคัญคือ `target_id`, `host`, `port`, `protocol`, `state`, `tool`, `scan_time`

### ข้อจำกัด

port เปิดไม่ได้บอกว่าบริการคืออะไร และ port ปิดหรือไม่ตอบอาจเกิดจาก firewall, rate limit หรือ network path ไม่ได้แปลว่าไม่มีบริการอยู่จริง

## 5. Nmap: ระบุพอร์ต บริการ และลักษณะระบบ

### สแกนหาอะไร

Nmap ตรวจ network service โดยใช้ทั้ง port scan, service/version detection และ NSE scripts ในคำสั่งที่เราใช้:

```bash
nmap -sV -sC -p "${LAB_PORT}" "${LAB_HOST}" \
  -oA "${RAW_NMAP_DIR}/scan"
```

- `-sV` พยายามระบุชื่อและเวอร์ชันของ service
- `-sC` รัน NSE scripts กลุ่ม default
- `-p` จำกัดพอร์ตให้ตรงกับ lab
- `-oA` บันทึกพร้อมกันเป็น `.nmap`, `.gnmap` และ `.xml`

### ทำงานอย่างไร

Nmap เปิดการเชื่อมต่อหรือส่ง probe ที่ออกแบบสำหรับ protocol ต่าง ๆ แล้วเปรียบเทียบ response กับฐาน signature ตัวอย่างเช่น banner, HTTP response, TLS handshake หรือรูปแบบข้อความของ service ผลจึงละเอียดกว่า Naabu

### Report มีอะไร

- `.nmap` อ่านง่ายผ่าน terminal
- `.gnmap` เป็นรูปแบบบรรทัดที่ใช้กับ script รุ่นเก่า
- `.xml` เป็น structured data ที่เหมาะสำหรับ parser และการนำเข้า platform

ข้อมูลสำคัญ ได้แก่ host status, port, protocol, state, service name, product, version, extra info, CPE และผล NSE script

### นำไปใช้ใน Dataset อย่างไร

Nmap เหมาะกับ feature พื้นฐานของ asset เช่น:

```text
port=18080
service=http
product=Jetty
version=9.2.11
state=open
```

ควรเก็บ XML เป็น raw เสมอ เพราะข้อความ terminal สูญเสียโครงสร้างบางส่วน การ normalize ควรสร้างหนึ่ง record ต่อ host-port-service

### ข้อจำกัดและการตีความ

เวอร์ชันที่ตรวจได้เป็น fingerprint ไม่ใช่หลักฐาน CVE โดยตรง บางระบบปิด banner, ใช้ reverse proxy หรือเปลี่ยนข้อความตอบกลับ ทำให้ product/version คลาดเคลื่อนได้ ถ้าจะ map เวอร์ชันไป CVE ต้องเก็บวิธี map และ confidence เพิ่ม

## 6. httpx-toolkit: ตรวจ HTTP และเก็บ Web Fingerprint

### สแกนหาอะไร

httpx-toolkit ของ ProjectDiscovery ใช้ตรวจว่า URL ตอบสนองหรือไม่ พร้อมเก็บ HTTP status, title, web server และเทคโนโลยีที่ตรวจพบ

บน Kali ต้องใช้ชื่อ `httpx-toolkit` เพราะคำสั่ง `httpx` อาจชนกับ Python HTTPX CLI ดังที่พบในการทดลอง

```bash
httpx-toolkit -u "${LAB_URL}" -json -td -sc -title -server \
  -o "${RAW_HTTPX_DIR}/scan.jsonl"
```

- `-u` ระบุ URL
- `-json` ให้ผลแบบ JSONL
- `-td` ตรวจ technology
- `-sc` เก็บ HTTP status code
- `-title` เก็บ title ของหน้า
- `-server` เก็บค่า Server header

### ทำงานอย่างไร

เครื่องมือส่ง HTTP request ไปยังเป้าหมาย อ่าน status line, headers และ HTML body แล้วใช้ลายเซ็นเพื่อระบุเทคโนโลยี เช่น framework, web server หรือ library

### Report มีอะไร

ผลอาจมี URL, input, host, port, scheme, status code, title, content type, content length, webserver, technologies, IP, response time และ timestamp ขึ้นกับรุ่นและ option

### นำไปใช้ใน Dataset อย่างไร

ใช้สร้าง web endpoint inventory และ feature สำหรับ scanner ตัวถัดไป เช่น:

```json
{
  "target_id":"struts2_s2045",
  "url":"http://127.0.0.11:18080",
  "status_code":200,
  "title":"...",
  "webserver":"Jetty(9.2.11.v20150529)",
  "technologies":["Java"]
}
```

ผลนี้ใช้ตอบว่าเว็บมีชีวิตและใช้เทคโนโลยีอะไร แต่ยังไม่ใช่ vulnerability finding

### ข้อจำกัด

technology detection เป็นการเดาจาก header/body signature เว็บที่ซ่อน header หรือมี proxy อาจทำให้ระบุผิด อีกทั้งการได้ `404` หรือ `403` ยังถือว่า HTTP service ตอบอยู่ ไม่ควรบันทึกเป็น unreachable

## 7. Nuclei: ตรวจช่องโหว่ด้วย Template

### สแกนหาอะไร

Nuclei ใช้ตรวจ CVE, misconfiguration, exposed panel, default credential pattern, information exposure และเทคโนโลยีต่าง ๆ ตาม template ที่ติดตั้งอยู่

```bash
nuclei -u "${LAB_URL}" -jsonl \
  -o "${RAW_NUCLEI_DIR}/scan.jsonl"
```

### ทำงานอย่างไร

template ระบุ request ที่ต้องส่งและ matcher ที่ใช้ตัดสินผล เช่น status code, header, ข้อความใน body, DSL expression หรือ out-of-band interaction เครื่องมือส่ง request ตาม template และบันทึก finding เมื่อเงื่อนไข matcher สำเร็จ

ดังนั้น Nuclei ไม่ได้ “คิดค้นวิธีโจมตีเอง” แต่ทำงานตาม knowledge ที่อยู่ใน template ผลการตรวจจึงขึ้นกับ:

- มี template สำหรับช่องโหว่นั้นหรือไม่
- template version เป็นปัจจุบันหรือไม่
- URL และ path ที่ป้อนถูกต้องหรือไม่
- ช่องโหว่ต้องการ authentication หรือเงื่อนไขพิเศษหรือไม่
- matcher แม่นพอหรือไม่

### Report มีอะไร

JSONL มักมี template ID/path, template info, name, severity, tags, matcher name, host, matched URL, request, response, extracted results, IP, timestamp และข้อมูล classification เช่น CVE/CWE/CVSS หาก template กำหนดไว้

### นำไปใช้ใน Dataset อย่างไร

Nuclei เป็นแหล่ง finding ที่ normalize ได้ง่าย ควรสร้างหนึ่ง record ต่อ finding และเก็บ:

```text
tool, template_id, finding_name, severity, cve, cwe,
target_url, matched_at, matcher_name, extracted_results,
request_hash, response_hash, scan_time
```

request/response อาจมี cookie, token หรือข้อมูลส่วนตัว จึงควร redact ก่อนเผยแพร่ dataset

### ผลลบหมายความว่าอะไร

ถ้า Nuclei ไม่พบ CVE ใน Vulhub ไม่ได้แปลว่า lab ไม่มีช่องโหว่ แปลเพียงว่า “การตั้งค่าและ template ชุดนี้ไม่ตรวจพบ” ควรบันทึกเป็น `not_detected` สำหรับ scanner run นั้น ไม่ใช่ ground truth negative

### False positive

template บางตัวอาจ match banner หรือข้อความทั่วไปโดยยังไม่ยืนยันผลกระทบ จึงควรใช้ `confidence` และ `verification_status` แยกจาก severity

## 8. Nikto: ตรวจ Web Server และการตั้งค่าที่ไม่แข็งแรง

### สแกนหาอะไร

Nikto ตรวจเว็บเซิร์ฟเวอร์หาไฟล์หรือ path ที่รู้จัก, default files, dangerous files, server version เก่า, HTTP methods, header ที่ขาด และ configuration ที่ไม่แข็งแรง

```bash
nikto -h "${LAB_URL}" | tee "${RAW_NIKTO_DIR}/scan.txt"
```

`tee` ทำให้เห็นผลใน terminal พร้อมบันทึกลงไฟล์

### ทำงานอย่างไร

Nikto ส่ง request จำนวนมากไปยัง path และรูปแบบที่ฐานทดสอบรู้จัก จากนั้นวิเคราะห์ status, headers และ body มันเป็น signature/check based scanner มากกว่าการ crawl และทดสอบ business logic แบบลึก

### ผลที่เราเห็นจริงจาก Struts2 lab

Nikto รายงานว่า:

- Server คือ `Jetty(9.2.11.v20150529)`
- Cookie `JSESSIONID` ไม่มี `HttpOnly`
- ขาด `Content-Security-Policy`
- ขาด `X-Content-Type-Options`
- ขาด `Referrer-Policy`
- ขาด `Permissions-Policy`
- ขาด `Strict-Transport-Security`
- Jetty ดูเป็นเวอร์ชันเก่า

ผลเหล่านี้เป็น hardening findings และ version observation ไม่ใช่หลักฐานว่า Nikto ตรวจพบ Struts2 S2-045 หรือ CVE-2017-5638

ข้อความ `Failed to check for updates: 403` เป็นข้อผิดพลาดในการตรวจอัปเดตของ Nikto ไม่ใช่ช่องโหว่ของเป้าหมาย ส่วนข้อความถึง error limit ต้องเก็บเป็น scan quality metadata เพราะการสแกนอาจไม่ครบ

### Report มีอะไร

ข้อความมี target, port, server banner, test ID, URL/path, finding description, references, จำนวน request, เวลา และ error หากต้องการนำเข้าระบบอัตโนมัติควรเลือก format ที่มีโครงสร้างในรุ่นที่ใช้งาน หรือเขียน parser โดยเก็บ raw text ไว้ตรวจสอบเสมอ

### นำไปใช้ใน Dataset อย่างไร

หนึ่งบรรทัด finding ควรแยกเป็นหนึ่ง record พร้อม `nikto_test_id`, `path`, `message`, `reference`, `category` และ `scan_complete` อย่าใช้ severity ที่เดาเองโดยไม่มี rule ที่บันทึกเวอร์ชัน

## 9. OWASP ZAP Baseline: Spider และ Passive Scan

### สแกนหาอะไร

ZAP Baseline เหมาะกับการตรวจเว็บแบบไม่โจมตีรุนแรง มัน crawl เว็บและใช้ passive scanner วิเคราะห์ request/response ที่พบ เช่น security headers, cookie flags, information disclosure, mixed content และการตั้งค่าเว็บที่เสี่ยง

คำสั่งที่ใช้เมื่อ ZAP อยู่ใน Docker และเป้าหมายอยู่บน Kali host:

```bash
docker run --rm --network host \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t "${LAB_URL}" | tee "${RAW_ZAP_DIR}/scan.txt"
```

`--network host` สำคัญสำหรับ Linux เพราะ `127.0.0.11` ที่มองจาก container ปกติหมายถึง loopback ของ container เอง ไม่ใช่ Kali host ถ้าไม่ใส่จึงเกิด `Connection refused`

### ทำงานอย่างไร

Baseline script เปิด ZAP daemon, เข้า target, spider เพื่อค้นหน้าและ resource แล้ววิเคราะห์ traffic แบบ passive โดยทั่วไปไม่ใช้ active attack payload แบบ ZAP Full Scan จึงปลอดภัยกว่าแต่ตรวจช่องโหว่เชิง injection ได้น้อยกว่า

### Report มีอะไร

ผลสรุปแบ่งเป็น `WARN`, `FAIL`, `PASS` และอาจแสดง alert name, risk, confidence, URL, parameter, evidence และคำแนะนำ การใช้งานเพื่อ dataset ควร mount output directory และสั่งออกรูปแบบ JSON/XML/HTML เพิ่ม ไม่ควรพึ่ง terminal text เพียงอย่างเดียว

ตัวอย่างแบบมี output file:

```bash
docker run --rm --network host \
  -v "${RAW_ZAP_DIR}:/zap/wrk:rw" \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t "${LAB_URL}" \
  -J scan.json -x scan.xml -r scan.html \
  | tee "${RAW_ZAP_DIR}/scan.txt"
```

### นำไปใช้ใน Dataset อย่างไร

ใช้ alert เป็นหนึ่ง finding โดยเก็บ `plugin_id`, `alert`, `risk`, `confidence`, `url`, `method`, `parameter`, `evidence`, `cwe_id`, `wasc_id`, `solution` และ `reference`

### ข้อจำกัด

Baseline ไม่ได้ยืนยัน RCE, SQL injection หรือช่องโหว่ทุก CVE ผลลบจึงหมายถึง passive scan ไม่พบ alert เท่านั้น หน้า login, JavaScript-heavy app และ endpoint ที่ spider ไปไม่ถึงจะไม่ถูกตรวจอย่างครบถ้วน

## 10. Wapiti: Black-box Web Vulnerability Scanner

### สแกนหาอะไร

Wapiti crawl เว็บแล้วทดสอบ parameter และ form จากภายนอก โดยไม่ต้องมี source code มุ่งตรวจกลุ่มช่องโหว่เว็บ เช่น injection, XSS, file inclusion, command execution pattern, SSRF หรือ misconfiguration ตาม module ที่เปิดใช้

```bash
wapiti -u "${LAB_URL}" -f json \
  -o "${RAW_WAPITI_DIR}/scan.json"
```

### ทำงานอย่างไร

Wapiti เริ่มจากสำรวจ URL, links และ forms แล้วสร้าง request ดัดแปลงค่า parameter ด้วย payload ของแต่ละ attack module จากนั้นเปรียบเทียบ response เพื่อหาสัญญาณว่าช่องโหว่อาจเกิดขึ้น

### Report มีอะไร

JSON report มี metadata ของการสแกน เป้าหมาย รายการ vulnerability/anomaly/additional information รวมทั้ง URL, parameter, HTTP method, payload, evidence, description, level และ remediation ขึ้นกับรุ่น

### นำไปใช้ใน Dataset อย่างไร

แยก vulnerability, anomaly และ informational ออกจากกัน อย่ารวมทุกอย่างเป็น positive label ควรเก็บ `module`, `category`, `level`, `method`, `path`, `parameter`, `payload_redacted`, `evidence` และ `request_id`

### ข้อจำกัด

Wapiti จะตรวจเฉพาะ endpoint ที่ crawler พบและ parameter ที่เข้าถึงได้ ระบบที่ต้อง login หรือมี API flow ซับซ้อนอาจต้องเตรียม session/cookie นอกจากนี้ payload เชิงรุกอาจกระทบข้อมูล จึงใช้เฉพาะ lab หรือระบบที่ได้รับอนุญาต

## 11. sqlmap: ตรวจ SQL Injection เฉพาะ Parameter

### สแกนหาอะไร

sqlmap ตรวจว่า input เช่น query parameter, form field, cookie หรือ header สามารถเปลี่ยนโครงสร้าง SQL query ที่ backend ใช้ได้หรือไม่ ตัวอย่างที่เราทดสอบคือ Django endpoint ที่มี parameter `date`:

```bash
TARGET_URL="http://127.0.0.14:18000/?date=minute"

sqlmap -u "${TARGET_URL}" --batch --level=5 --risk=3 \
  --tamper=space2comment --random-agent --flush-session \
  --output-dir="${RAW_SQLMAP_DIR}" \
  | tee "${RAW_SQLMAP_DIR}/terminal.txt"
```

### ทำงานอย่างไร

sqlmap ระบุจุด input แล้วส่ง payload หลายตระกูล เช่น boolean-based blind, error-based, time-based blind, UNION query และ stacked queries จากนั้นเปรียบเทียบ response content, status, error และ response time กับ baseline

ตัวอย่างเช่น time-based test จะดูว่าการใส่ expression ที่ทำให้ฐานข้อมูลหน่วงเวลาส่งผลต่อ response อย่างสม่ำเสมอหรือไม่ ส่วน boolean-based จะเปรียบเทียบผลของเงื่อนไขจริงและเท็จ

### ความหมายของ Option ที่ใช้

- `--batch` ใช้คำตอบอัตโนมัติ เหมาะกับการรันซ้ำ
- `--level=5` เพิ่มจุดและ payload ที่ตรวจ ทำให้ request มากขึ้น
- `--risk=3` เปิด payload ที่มีความเสี่ยงสูงขึ้น
- `--tamper=space2comment` แปลงช่องว่างใน payload เป็น comment ไม่จำเป็นสำหรับทุกเป้าหมาย
- `--random-agent` เปลี่ยน User-Agent
- `--flush-session` ล้างผล cache เดิม เพื่อไม่ให้ run ใหม่อ้างผลเก่า
- `--output-dir` เก็บ session และ log แยกตาม target

### ผลที่เราเห็นจริง

การทดลอง Django มี heuristic ที่ดูน่าสงสัยในช่วงแรก แต่ผลสุดท้ายระบุแนวทางว่าเป็น `false positive or unexploitable` ดังนั้น label ที่ถูกต้องคือ `inconclusive` หรือ `not_confirmed` ไม่ใช่ `sql_injection=true`

นี่เป็นตัวอย่างสำคัญว่า log ระหว่างทางไม่ใช่ final verdict ต้องอ่าน summary ตอนท้ายและเก็บ exit status, tested parameter, techniques attempted และ final conclusion

### Report และ Dataset

ควรเก็บ terminal log, session directory และ structured CSV/SQLite ภายใน output directoryตามรุ่น ฟิลด์ normalize ได้แก่ parameter location, parameter name, DBMS guess, technique, payload, injectable status, confidence และ reason

### ข้อจำกัดและความเสี่ยง

`level=5` และ `risk=3` ไม่ควรใช้เป็นค่าเริ่มต้นกับ production เพราะ request จำนวนมากและ payload บางชนิดอาจเปลี่ยนข้อมูล ควรเริ่มจากค่าต่ำ กำหนด parameter ด้วย `-p` และใช้สำเนาระบบหรือ maintenance window

## 12. AutoRecon: ตัวประสาน Recon หลายเครื่องมือ

### สแกนหาอะไร

AutoRecon เป็น orchestration tool มันเริ่มจาก port scan แล้วเลือกการตรวจเพิ่มตาม service ที่พบ เช่น Nmap scripts, directory discovery หรือ service-specific enumeration จุดแข็งคือเก็บผล recon หลายชนิดเป็น directory เดียว

```bash
sudo autorecon "${LAB_HOST}" --ports "${LAB_PORT}" \
  -o "${RAW_AUTORECON_DIR}"
```

### ทำงานอย่างไร

AutoRecon เรียกโปรแกรมอื่นตาม plugin และเงื่อนไขของ service ดังนั้นมันไม่ใช่ vulnerability engine ตัวเดียว ผลลัพธ์ขึ้นกับ dependency ที่ติดตั้ง plugin configuration สิทธิ์ และ timeout

### Report มีอะไร

directory output มี command log, stdout/stderr, Nmap output, scan results, notes และไฟล์จาก tools ย่อย โครงสร้างอาจมีไฟล์จำนวนมาก จึงควรเก็บ manifest เพิ่มว่า run นี้เรียกเครื่องมือใด เวอร์ชันอะไร และสำเร็จหรือไม่

### นำไปใช้ใน Dataset อย่างไร

AutoRecon เหมาะกับ raw evidence และ scan orchestration แต่ไม่ควรนับ finding ซ้ำกับ Nmap/Nikto ที่ถูกรันแยก ต้องมี `parent_run_id` และ `producer_tool` เช่น record ที่ AutoRecon สั่ง Nmap ต้องระบุ producer เป็น Nmap และ orchestrator เป็น AutoRecon

### ข้อจำกัด

ใช้เวลานานและสร้างข้อมูลซ้ำได้ง่าย ผล “สำเร็จ” ของ AutoRecon หมายถึง workflow จบ ไม่ได้หมายความว่าพบ vulnerability

## 13. OpenVAS/GVM: Vulnerability Management และ Network Vulnerability Tests

### ส่วนประกอบสำคัญ

ชื่อ OpenVAS มักถูกใช้เรียกระบบรวม แต่ชุด GVM ประกอบด้วยหลายส่วน:

- OpenVAS Scanner ทำ Network Vulnerability Tests หรือ NVTs
- `ospd-openvas` เป็นตัวกลางควบคุม scanner
- `gvmd` จัดการ target, task, report, user และฐานข้อมูล
- `gsad` ให้ Web UI ที่ port 9392
- Greenbone feeds ให้ข้อมูล VT, CVE, SCAP และ CERT

### สแกนหาอะไร

OpenVAS ตรวจ host และ network services ด้วย VT จำนวนมาก เช่น service version, known CVE, weak configuration, TLS, default credential check บางชนิด และพฤติกรรมของ service

ใน UI ต้องสร้าง:

1. Target ระบุ host และ port list
2. Task เลือก target, scan config เช่น Full and fast และ scanner
3. Start task
4. รอ status จาก `New` -> `Queued` -> `Running` -> `Done`

เราใช้ CLI เริ่ม task สำเร็จเมื่อปุ่ม UI ใช้งานไม่ได้:

```bash
TASK_ID="57785d1b-96f3-4d9d-90d5-da374cdbd269"
read -rsp "GVM password: " GVM_PASSWORD; echo

sudo runuser -u _gvm -- gvm-cli \
  --gmp-username admin \
  --gmp-password "${GVM_PASSWORD}" \
  socket --pretty \
  --xml "<start_task task_id=\"${TASK_ID}\"/>"
```

GMP options ต้องอยู่ก่อนคำว่า `socket` ตามรูปแบบ CLI รุ่นที่ติดตั้ง

### ทำงานอย่างไร

scanner เลือก VT จาก scan config ส่ง probe ไปยัง host/service และประเมินผลตาม detection logic ของแต่ละ VT บางรายการอาศัย version detection บางรายการส่ง request เพื่อตรวจพฤติกรรม และบางรายการต้องใช้ credential เพื่อประเมินภายในระบบ

### Report มีอะไร

GVM report มี result ต่อ host/port พร้อมชื่อ VT, severity, threat, QoD, description, impact, solution, affected software, references, CVE, NVT OID และ timestamps

ค่าที่ต้องแยกให้ออก:

- `severity` คือความรุนแรง โดยทั่วไปอิง CVSS
- `QoD` หรือ Quality of Detection คือความเชื่อมั่นในวิธีตรวจ ไม่ใช่ความรุนแรง
- `threat` เป็นกลุ่ม เช่น High, Medium, Low, Log
- `NVT OID` เป็นตัวระบุ test ของ Greenbone

### นำไปใช้ใน Dataset อย่างไร

ควรเก็บ XML report เป็น raw และ normalize หนึ่ง record ต่อ result ฟิลด์หลักคือ:

```text
report_id, task_id, target_id, host, port,
nvt_oid, nvt_name, severity, qod, threat,
cve, cvss_base, description, impact, solution,
detection_method, scan_start, scan_end
```

### สิ่งที่ต้องระวัง

task ที่ status `Queued` ยังไม่มีผลสมบูรณ์ ห้ามนำ report ระหว่างรอไปสรุปเป็น negative และ feed ต้อง sync เสร็จก่อน ไม่เช่นนั้น coverage จะต่ำ ผล version-based ที่ QoD ต่ำควรจัดเป็น potential แล้วใช้เครื่องมือเฉพาะทางยืนยัน

## 14. Metasploit Framework: ยืนยันความเป็นไปได้ของ Exploit

### ทำหน้าที่อะไร

Metasploit ไม่ใช่ scanner หลักสำหรับเก็บ asset inventory แต่เป็น exploitation framework ที่รวม module สำหรับตรวจและใช้ช่องโหว่ เช่น `auxiliary/scanner`, `exploit`, `payload` และ `post`

ใน workflow นี้ใช้หลังจาก scanner ระบุ candidate แล้ว เพื่อยืนยันใน Vulhub ว่าช่องโหว่มีผลจริง ไม่ควรยิง module แบบสุ่มใส่ server จริง

### ทำงานอย่างไร

module กำหนดเงื่อนไข target, request หรือ protocol exchange และวิธีส่ง payload บาง module มีคำสั่ง `check` ซึ่งตรวจความเปราะบางโดยไม่เปิด session เต็ม ถ้ารองรับควรใช้ `check` ก่อน `run` หรือ `exploit`

ขั้นตอนทั่วไปใน lab:

```text
msfconsole
search cve:2017-5638
info <module>
use <module>
show options
set RHOSTS 127.0.0.11
set RPORT 18080
set TARGETURI /
check
run
```

ต้องอ่าน `info` และ `show options` ของ module ที่พบจริง เพราะชื่อ module และ option ต่างกัน ไม่ควรเดาชื่อ module หรือ payload

### Report มีอะไร

Metasploit terminal แสดง module, target, options, check result, exploit status, session opened/failed และ error สามารถใช้ spool บันทึกผล:

```text
spool /home/kali/dataset/raw/metasploit/2026-08-04/struts2_s2045/console.txt
...
spool off
```

### นำไปใช้ใน Dataset อย่างไร

ผล `Vulnerable` จาก `check` และการเปิด session จริงต้องเก็บคนละระดับ:

- `check_code`: safe, detected, appears, vulnerable, unsupported หรือ unknown
- `exploit_attempted`: true/false
- `session_opened`: true/false
- `module_fullname`
- `payload`
- `failure_reason`
- `evidence_reference`

การเปิด shell/session เป็นหลักฐานระดับสูง แต่ไม่ควรเก็บ secret หรือคำสั่ง post-exploitation ที่ไม่จำเป็นกับงานวิจัย

### ข้อจำกัด

exploit ล้มเหลวไม่ได้พิสูจน์ว่าไม่มีช่องโหว่ อาจเกิดจาก module ไม่ตรงเวอร์ชัน, option ผิด, target path ผิด, payload ไม่เข้ากับสถาปัตยกรรม, firewall หรือ mitigation ขณะเดียวกันการมี CVE จริงก็ไม่ได้หมายความว่า Metasploit ต้องมี module รองรับ

## 15. เครื่องมือบริหารข้อมูล: Faraday, DefectDojo และ Reconmap

เครื่องมือสามตัวนี้ไม่ควรถูกนับเป็น scanner result แต่ใช้จัดระเบียบข้อมูลที่ scanner สร้าง

### DefectDojo

DefectDojo เหมาะเป็นคลัง vulnerability finding หลัก มันนำเข้ารายงาน scanner หลายรูปแบบ จัด findings เข้า product, engagement และ test ช่วย deduplicate, triage, assign owner, ติดตามสถานะ และวัด SLA

ข้อมูลที่ได้จาก DefectDojo เป็นข้อมูลหลังการบริหาร เช่น active, verified, false positive, duplicate, mitigated, accepted risk ไม่ใช่ raw detection เพียงอย่างเดียว เหมาะสำหรับ label ที่ผ่านมนุษย์ตรวจแล้ว

สำหรับ dataset ควรเก็บ `source_tool`, `source_finding_id`, `dojo_finding_id`, `active`, `verified`, `false_positive`, `duplicate`, `severity`, `cve`, `date`, `mitigated` และประวัติการเปลี่ยนสถานะ

### Faraday

Faraday รวมข้อมูล penetration testing เป็นโครงสร้าง workspace -> host -> interface/service -> vulnerability ช่วยเชื่อม finding กับ asset และ service ที่เกี่ยวข้อง รองรับการนำเข้าผลเครื่องมือและการทำงานร่วมกัน

จุดเด่นสำหรับ dataset คือความสัมพันธ์เชิง asset เช่น vulnerability นี้อยู่ที่ host ไหน service/port ใด และใครเป็นผู้รายงาน แต่ต้องระวังการนำเข้าผลซ้ำจากหลาย scanner

### Reconmap

Reconmap เน้นบริหารโครงการ security assessment เช่น client, project, scope, task, finding, note และ report เหมาะกับ metadata ว่าทำไมจึงสแกน เป้าหมายอยู่ใน scope ใด และหลักฐานถูกใช้ในรายงานฉบับใด

Reconmap ไม่ได้เพิ่มความแม่นของ detection โดยตรง แต่เพิ่ม project context และ traceability ซึ่งมีประโยชน์เมื่อต้องตอบว่า finding มาจากการทดสอบรอบใดและอยู่ภายใต้การอนุญาตใด

### วิธีเลือกใช้

- ใช้ DefectDojo เป็น vulnerability finding repository และ triage source
- ใช้ Faraday เมื่อต้องการมุมมอง host/service/vulnerability สำหรับงาน pentest
- ใช้ Reconmap สำหรับ scope, task, note และรายงานโครงการ
- ไม่จำเป็นต้องบังคับใช้ทั้งสามเป็นฐานหลักพร้อมกัน เพราะจะเกิดข้อมูลซ้ำ ควรกำหนด system of record หนึ่งตัว

## 16. เครื่องมือที่ไม่ได้ใช้ในรอบ Local Vulhub นี้

Subfinder และ Amass เหมาะกับการค้นหา subdomain และ attack surface ของ domain แต่เป้าหมายรอบนี้เป็น loopback IP เช่น `127.0.0.11` จึงไม่มีประโยชน์ที่จะรันกับ lab เหล่านี้ การสร้างไฟล์ผลว่างจากสองเครื่องมือนี้จะเพิ่ม noise โดยไม่เพิ่มข้อมูล

การไม่ใช้เครื่องมือในกรณีที่ไม่ตรงงานเป็นการตัดสินใจที่ถูกต้อง ไม่ใช่ coverage ที่ขาด หากภายหลังทดสอบ domain ที่ได้รับอนุญาต จึงค่อยเพิ่มขั้น Subfinder/Amass ก่อน Naabu และ httpx-toolkit

## 17. Raw กับ Normalized ต่างกันอย่างไร

### Raw report

Raw คือไฟล์ต้นฉบับจาก scanner ที่ยังไม่เปลี่ยนความหมาย เช่น Nmap XML, Nuclei JSONL, ZAP JSON/XML/HTML, OpenVAS XML และ terminal log มีหน้าที่เป็นหลักฐานและใช้ parse ใหม่ได้ในอนาคต

โครงสร้างที่ใช้:

```text
~/dataset/raw/<tool-name>/<date>/<target>/
```

ห้ามแก้ raw report หลังสร้าง หากต้อง redact ควรเก็บ checksum ของต้นฉบับในพื้นที่ควบคุม และสร้างสำเนา sanitized สำหรับแชร์

### Normalized report

Normalized คือข้อมูลที่แปลงเข้าสู่ schema กลางเพื่อเปรียบเทียบข้าม scanner:

```text
~/dataset/normalized/<tool-name>/<date>/<target>.jsonl
```

หนึ่ง record ที่แนะนำ:

```json
{
  "schema_version":"1.0",
  "run_id":"2026-08-04-struts2_s2045-nuclei-001",
  "target_id":"struts2_s2045",
  "ground_truth_cve":"CVE-2017-5638",
  "tool":"nuclei",
  "tool_version":"...",
  "finding_type":"vulnerability",
  "finding_id":"...",
  "title":"...",
  "severity":"high",
  "confidence":"medium",
  "detected_cve":"CVE-2017-5638",
  "host":"127.0.0.11",
  "port":18080,
  "url":"http://127.0.0.11:18080/...",
  "scanner_result":"detected",
  "verification_status":"not_verified",
  "raw_report":"raw/nuclei/2026-08-04/struts2_s2045/scan.jsonl",
  "scanned_at":"2026-08-04T00:00:00Z"
}
```

## 18. วิธีประเมินว่าเครื่องมือใดตรวจ CVE ได้ดี

สำหรับแต่ละ target ต้องเปรียบเทียบ `ground_truth_cve` กับ `detected_cve` ของแต่ละเครื่องมือ โดยไม่ใช้ hardening finding มาทดแทน CVE

นิยามพื้นฐาน:

- True Positive: scanner ระบุ CVE หรือพฤติกรรมช่องโหว่ตรงกับ ground truth และมีหลักฐานเพียงพอ
- False Positive: scanner ระบุว่ามีช่องโหว่ แต่การตรวจสอบยืนยันว่าไม่มีหรือเงื่อนไขใช้ไม่ได้
- False Negative: target มีช่องโหว่ตาม ground truth แต่ scanner ไม่ตรวจพบภายใต้ configuration ที่กำหนด
- True Negative: target ไม่มีช่องโหว่ที่ทดสอบและ scanner ไม่แจ้งผล ต้องมี clean target/control จึงวัดค่านี้ได้

มีเพียง Vulhub vulnerable labs อย่างเดียวจะวัด precision/false positive rate ได้ไม่ครบ ควรเพิ่ม patched control ที่เป็นผลิตภัณฑ์เดียวกันแต่แก้ช่องโหว่แล้ว และรัน scanner ด้วย configuration เดียวกัน

## 19. คำตอบสั้นสำหรับอธิบายงาน

ถ้าถูกถามว่า “ทำไมใช้หลายเครื่องมือ” ให้ตอบว่า:

> เครื่องมือแต่ละตัวมองระบบคนละชั้น Naabu และ Nmap บอกว่ามีบริการอะไร httpx บอกว่าเว็บตอบและใช้เทคโนโลยีใด Nuclei, Nikto, ZAP, Wapiti และ OpenVAS ใช้วิธีตรวจช่องโหว่คนละแบบ sqlmap ตรวจ SQL injection เฉพาะจุด และ Metasploit ใช้ยืนยันผลกระทบในห้องทดลอง การรวมผลช่วยเปรียบเทียบ coverage และ false positive โดยยังเก็บ raw evidence ไว้ตรวจย้อนหลัง

ถ้าถูกถามว่า “ทำไมผล scanner ไม่ตรงกัน” ให้ตอบว่า:

> เพราะแต่ละเครื่องมือมีฐานความรู้ วิธี crawl, payload, matcher, authentication และเงื่อนไขตรวจต่างกัน ผลลบของเครื่องมือหนึ่งจึงไม่ได้พิสูจน์ว่าไม่มีช่องโหว่ และผลบวกจาก version match ก็ยังต้องพิจารณา confidence หรือยืนยันเพิ่มเติม

ถ้าถูกถามว่า “report ไหนเหมาะกับ dataset” ให้ตอบว่า:

> เก็บ report แบบ structured เช่น JSONL, JSON หรือ XML เป็น raw แล้วแปลงเป็น schema กลาง โดยไม่ทิ้งข้อมูล tool-specific ส่วน terminal text ใช้สำหรับ audit แต่ไม่ควรเป็นแหล่งข้อมูลเดียว

ถ้าถูกถามว่า “อะไรคือคำตอบจริงของข้อมูล” ให้ตอบว่า:

> Ground truth มาจาก environment ของ Vulhub และ version/configuration ที่รัน ส่วน scanner output คือ prediction หรือ observation ต้องเก็บสองส่วนแยกกันเพื่อคำนวณว่าเครื่องมือใดตรวจพบหรือพลาด

## 20. สรุปบทบาทแบบจำง่าย

| เครื่องมือ | คำถามที่ตอบ | ผลหลัก |
|---|---|---|
| Docker/Vulhub | ระบบทดลองคืออะไรและมี CVE ใด | Ground truth + reproducible lab |
| Naabu | พอร์ตใดเปิด | Open port observation |
| Nmap | พอร์ตนั้นเป็นบริการและเวอร์ชันอะไร | Service fingerprint |
| httpx-toolkit | URL ตอบไหม เว็บมีลักษณะอะไร | HTTP/technology fingerprint |
| Nuclei | ตรงกับ template ช่องโหว่ใด | Template-based finding |
| Nikto | เว็บเซิร์ฟเวอร์ตั้งค่าอ่อนหรือมีไฟล์/เวอร์ชันเสี่ยงไหม | Hardening/version findings |
| ZAP Baseline | Traffic ที่ spider พบมี web weakness อะไร | Passive web alerts |
| Wapiti | Parameter/form ตอบสนองต่อ payload ผิดปกติไหม | Black-box active findings |
| sqlmap | Parameter นี้ฉีด SQL ได้ไหม | SQLi technique verdict |
| AutoRecon | Recon หลายขั้นได้ผลอะไร | Aggregated raw recon |
| OpenVAS/GVM | Host/service ตรงกับ VT/CVE หรือ weakness ใด | NVT findings + severity/QoD |
| Metasploit | Candidate นี้ตรวจหรือ exploit ได้จริงไหม | Verification evidence |
| DefectDojo | จะ triage และติดตาม finding อย่างไร | Managed finding status |
| Faraday | finding เชื่อมกับ host/service ใด | Pentest asset graph |
| Reconmap | งานนี้อยู่ใน project/scope/report ใด | Assessment context |

แก่นของงานนี้จึงไม่ใช่การรวมจำนวน alert ให้มากที่สุด แต่เป็นการรักษาความหมายของหลักฐานแต่ละชนิด เก็บ raw report ให้ตรวจย้อนหลังได้ และสร้าง normalized records ที่แยก ground truth, scanner prediction, confidence และผลยืนยันออกจากกันอย่างชัดเจน
