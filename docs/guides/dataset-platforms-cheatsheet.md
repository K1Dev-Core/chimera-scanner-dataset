# Cheatsheet: Dataset Platforms

เตรียมเมื่อ 2026-08-04

เอกสารนี้สรุปว่า platform และ scanner แต่ละตัวควรอยู่ตรงไหนใน pipeline ของ Chimera Scanner Dataset

## เป้าหมาย

ใช้ platform ดังนี้:

- `DefectDojo`: findings dataset store หลัก
- `Faraday`: enrichment ด้าน host/service/vulnerability
- `Reconmap`: project/report/client context

ใช้ scanner:

- `Nmap`
- `Nuclei`
- `OpenVAS / Greenbone / GVM`
- `OWASP ZAP`
- `Nikto`
- `sqlmap`
- `Metasploit`

ใช้ lab:

- `Vulhub`

## Setup พื้นฐานบน Kali

```bash
sudo apt update
sudo apt install -y ca-certificates curl git gnupg jq wget
```

ติดตั้ง Docker และ security tools:

```bash
sudo apt install -y \
  gvm zaproxy nuclei wapiti subfinder httpx-toolkit naabu \
  autorecon amass metasploit-framework sqlmap nikto nmap seclists
```

เริ่มต้น GVM และ Metasploit database:

```bash
sudo gvm-setup
sudo gvm-check-setup
sudo msfdb init
```

## Clone platform และ lab

```bash
mkdir -p ~/sec-platforms ~/labs ~/reports

cd ~/sec-platforms
git clone --depth 1 https://github.com/infobyte/faraday.git
git clone --depth 1 https://github.com/DefectDojo/django-DefectDojo.git
git clone --depth 1 https://github.com/reconmap/reconmap.git

cd ~/labs
git clone --depth 1 https://github.com/vulhub/vulhub.git
```

## เปิด platform

### Faraday

```bash
cd ~/sec-platforms/faraday
docker compose up -d
docker compose logs faraday-server | grep -i password
```

- UI/API: `http://localhost:5985`
- username: `faraday`

### DefectDojo

```bash
cd ~/sec-platforms/django-DefectDojo
docker compose up -d
docker compose logs initializer | grep "Admin password:"
```

- UI: ดู port จาก `docker compose ps`
- username: `admin`

### Reconmap

```bash
cd ~/sec-platforms/reconmap
docker compose up -d
```

- Dashboard: `http://localhost:5500`
- API: `http://localhost:3000`

## แนวทางเปิด Vulhub labs

ควรแยกแต่ละ lab ด้วย loopback IP/port เพื่อไม่ให้ชนกัน เช่น:

```bash
sudo ip addr add 127.0.0.11/8 dev lo || true
sudo ip addr add 127.0.0.12/8 dev lo || true
sudo ip addr add 127.0.0.13/8 dev lo || true
sudo ip addr add 127.0.0.14/8 dev lo || true
```

ตัวอย่าง target map:

```bash
# Struts2 S2-045
TARGET_IP=127.0.0.11
TARGET_PORT=18080

# Spring4Shell
TARGET_IP=127.0.0.12
TARGET_PORT=28080

# Log4Shell
TARGET_IP=127.0.0.13
TARGET_PORT=18983

# Django SQLi
TARGET_IP=127.0.0.14
TARGET_PORT=18000
```

## Scanner command หลัก

### Nmap

```bash
nmap -sV -O -oX ~/reports/nmap/target1.xml TARGET_IP
```

### Nuclei

```bash
nuclei -u http://TARGET:PORT -json-export ~/reports/nuclei/target1.json
```

### ZAP

```bash
docker run --rm -v "$HOME/reports/zap:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://TARGET:PORT -J zap.json -r zap.html -x zap.xml
```

### Nikto

```bash
nikto -h http://TARGET:PORT -o ~/reports/nikto/target1.json -Format json
```

### sqlmap

```bash
python sqlmap.py -u "http://TARGET/item.php?id=1" --batch --output-dir ~/reports/sqlmap/target1
```

### Metasploit

```text
search cve:2022-22965
use <module_name>
set RHOSTS TARGET_IP
set RPORT TARGET_PORT
run
```

## Import เข้า platform

### Faraday

เหมาะกับ report files เช่น:

- Nmap XML
- Nuclei JSON
- ZAP XML/JSON
- Nikto

### DefectDojo

เหมาะเป็น central findings store:

1. Create Product
2. Create Engagement
3. Import Scan
4. Reimport เมื่อสแกน target เดิมซ้ำ

reimport ช่วยสร้าง lifecycle label เช่น new, untouched, closed, reactivated

### Reconmap

เหมาะกับ project/report context และการผูกผล scan เข้ากับ engagement

## Schema ขั้นต่ำที่แนะนำ

```json
{
  "platform": "defectdojo",
  "tool": "nuclei",
  "project": "spring-lab",
  "target": "http://TARGET:PORT",
  "scenario_id": "spring-CVE-2022-22965",
  "cve_id": "CVE-2022-22965",
  "finding_name": "spring4shell-rce",
  "severity": "critical",
  "status": "active",
  "label": "positive",
  "raw_report_path": "/home/kali/reports/nuclei/target1.json"
}
```

columns ขั้นต่ำ:

- `platform`
- `tool`
- `target`
- `scenario_id`
- `cve_id`
- `finding_name`
- `severity`
- `status`
- `label`
- `raw_report_path`
- `scan_timestamp`

## ลำดับงานที่แนะนำ

1. เปิด `DefectDojo`
2. เปิด `Faraday`
3. เปิด Vulhub lab หนึ่งตัว
4. รัน `Nmap`
5. รัน `Nuclei`
6. รัน `ZAP` หรือ `Nikto`
7. รัน `sqlmap` เฉพาะ SQLi scenario
8. รัน `Metasploit` เพื่อ verification
9. import report เข้า `DefectDojo`
10. import report เข้า `Faraday`
11. เพิ่ม context ใน `Reconmap` ถ้าต้องการ

## สรุปสั้น

- raw scanner artifacts คือ source of truth
- DefectDojo เหมาะเก็บ findings กลาง
- Faraday เหมาะ enrich host/service/vuln
- Reconmap เหมาะเก็บ project context
- อย่า force ทุก scanner ให้ต้อง detect CVE เดียวกัน เพราะจะทำให้ dataset บิดเบี้ยว
