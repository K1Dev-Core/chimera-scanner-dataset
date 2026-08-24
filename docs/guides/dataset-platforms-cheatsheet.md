# Dataset Platforms Cheatsheet

Prepared on 2026-08-04.

## Goal

Use:

- `DefectDojo` as the main findings dataset store
- `Faraday` as host/service/vulnerability enrichment
- `Reconmap` as project/report/client context

Use scanners:

- `Nmap`
- `Nuclei`
- `OpenVAS / Greenbone / GVM`
- `OWASP ZAP`
- `Nikto`
- `sqlmap`
- `Metasploit`

Use labs:

- `Vulhub`

## 1) Base setup on Kali

```bash
sudo apt update
sudo apt install -y ca-certificates curl git gnupg jq wget
```

### Docker

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

ARCH="$(dpkg --print-architecture)"
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: trixie
Components: stable
Architectures: ${ARCH}
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Open a new shell after adding yourself to the docker group.

### Security tools

```bash
sudo apt install -y \
  gvm zaproxy nuclei wapiti subfinder httpx-toolkit naabu \
  autorecon amass metasploit-framework sqlmap nikto nmap seclists
```

Note:

- On current Kali, install `OpenVAS` through the `gvm` package.
- Kali's docs explicitly note that the tool was previously named `OpenVAS`.

### Optional initialization

```bash
sudo gvm-setup
sudo gvm-check-setup
sudo msfdb init
```

## 2) Clone everything

```bash
mkdir -p ~/sec-platforms ~/labs ~/reports

cd ~/sec-platforms
git clone --depth 1 https://github.com/infobyte/faraday.git
git clone --depth 1 https://github.com/DefectDojo/django-DefectDojo.git
git clone --depth 1 https://github.com/reconmap/reconmap.git

cd ~/labs
git clone --depth 1 https://github.com/vulhub/vulhub.git
```

If GitHub is flaky:

```bash
git config --global http.version HTTP/1.1
```

## 3) Start the platforms

### Faraday

```bash
cd ~/sec-platforms/faraday
docker compose up -d
docker compose logs faraday-server | grep -i password
docker compose ps
```

Access:

- UI/API: `http://localhost:5985`
- username: `faraday`

### DefectDojo

```bash
cd ~/sec-platforms/django-DefectDojo
docker compose up -d
docker compose logs initializer | grep "Admin password:"
docker compose ps
```

Access:

- UI: usually `http://localhost:8080` or the published port in `docker compose ps`
- username: `admin`

### Reconmap

```bash
cd ~/sec-platforms/reconmap
docker compose up -d
docker compose ps
```

Access, per docs:

- Dashboard: `http://localhost:5500`
- API: `http://localhost:3000`

## 4) Start example CVE labs with Vulhub

### Run all recommended labs together with different host IPs and ports

Important:

- `compose.override.yml` is **not** the right tool for replacing the original `ports:` list here.
- In Docker Compose merge behavior, list values such as `ports:` are appended, so the original `8080:8080` or `8000:8000` mapping remains and can still collide with other labs.
- Use a dedicated host-facing compose file instead.

This approach keeps each lab on a different loopback IP and port on the Kali host, which is the simplest practical way to give each lab a separate local endpoint.

If your system does not already accept these loopback aliases, add them first:

```bash
sudo ip addr add 127.0.0.11/8 dev lo || true
sudo ip addr add 127.0.0.12/8 dev lo || true
sudo ip addr add 127.0.0.13/8 dev lo || true
sudo ip addr add 127.0.0.14/8 dev lo || true
```

Then run everything:

```bash
cd ~/labs/vulhub/struts2/s2-045
cat > docker-compose.host.yml <<'EOF'
version: '2'
services:
  struts2:
    image: vulhub/struts2:2.3.30
    ports:
      - "127.0.0.11:18080:8080"
EOF
docker compose -f docker-compose.host.yml -p vh_struts2_s2045 up -d

cd ~/labs/vulhub/spring/CVE-2022-22965
cat > docker-compose.host.yml <<'EOF'
services:
  spring:
    image: vulhub/spring-webmvc:5.3.17
    ports:
      - "127.0.0.12:28080:8080"
EOF
docker compose -f docker-compose.host.yml -p vh_spring_22965 up -d

cd ~/labs/vulhub/log4j/CVE-2021-44228
cat > docker-compose.host.yml <<'EOF'
version: '2'
services:
  solr:
    image: vulhub/solr:8.11.0
    ports:
      - "127.0.0.13:18983:8983"
      - "127.0.0.13:15005:5005"
EOF
docker compose -f docker-compose.host.yml -p vh_log4j_44228 up -d

cd ~/labs/vulhub/django/CVE-2022-34265
cat > docker-compose.host.yml <<'EOF'
services:
  web:
    image: vulhub/django:4.0.5
    working_dir: /app
    volumes:
      - .:/app
    ports:
      - "127.0.0.14:18000:8000"
    depends_on:
      - db
    command: bash /app/docker-entrypoint.sh
  db:
    image: postgres:13-alpine
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=CVE_2022_34265
EOF
docker compose -f docker-compose.host.yml -p vh_django_34265 up -d
```

Check all running containers:

```bash
docker ps
```

Access URLs:

- Struts2 S2-045: `http://127.0.0.11:18080`
- Spring4Shell: `http://127.0.0.12:28080`
- Log4Shell: `http://127.0.0.13:18983`
- Django SQLi: `http://127.0.0.14:18000`

Stop all:

```bash
cd ~/labs/vulhub/struts2/s2-045 && docker compose -f docker-compose.host.yml -p vh_struts2_s2045 down -v
cd ~/labs/vulhub/spring/CVE-2022-22965 && docker compose -f docker-compose.host.yml -p vh_spring_22965 down -v
cd ~/labs/vulhub/log4j/CVE-2021-44228 && docker compose -f docker-compose.host.yml -p vh_log4j_44228 down -v
cd ~/labs/vulhub/django/CVE-2022-34265 && docker compose -f docker-compose.host.yml -p vh_django_34265 down -v
```

## Lab A: Struts2 S2-045 / CVE-2017-5638

```bash
cd ~/labs/vulhub/struts2/s2-045
docker compose up -d
docker compose ps
docker compose logs -f
```

## Lab B: Spring4Shell / CVE-2022-22965

```bash
cd ~/labs/vulhub/spring/CVE-2022-22965
docker compose up -d
docker compose ps
docker compose logs -f
```

## Lab C: Django SQLi / CVE-2022-34265

```bash
cd ~/labs/vulhub/django/CVE-2022-34265
docker compose up -d
docker compose ps
docker compose logs -f
```

## Stop a lab

```bash
docker compose down -v
```

## 5) Create folders for reports

```bash
mkdir -p \
  ~/reports/nmap \
  ~/reports/nuclei \
  ~/reports/zap \
  ~/reports/nikto \
  ~/reports/sqlmap \
  ~/reports/msf \
  ~/reports/gvm
```

## 6) Scanner commands

### Nmap

```bash
nmap -sV -O -oX ~/reports/nmap/target1.xml TARGET_IP
```

More verbose:

```bash
nmap -sV -O -A -oA ~/reports/nmap/target1 TARGET_IP
```

Expected XML shape:

```xml
<host>
  <address addr="192.168.56.101" addrtype="ipv4"/>
  <ports>
    <port protocol="tcp" portid="80">
      <state state="open"/>
      <service name="http" product="Apache httpd" version="2.4.49"/>
    </port>
  </ports>
</host>
```

### Nuclei

Single target:

```bash
nuclei -u http://TARGET:PORT -json-export ~/reports/nuclei/target1.json
```

Multiple URLs:

```bash
nuclei -list urls.txt -json-export ~/reports/nuclei/bulk.json
```

CVE-focused:

```bash
nuclei -u http://TARGET:PORT -tags cve -severity critical,high -json-export ~/reports/nuclei/cves.json
```

Expected JSON shape:

```json
{
  "template-id": "spring4shell-rce",
  "info": {
    "name": "Spring4Shell RCE",
    "severity": "critical"
  },
  "host": "http://TARGET:8080",
  "matched-at": "http://TARGET:8080/",
  "type": "http"
}
```

### OpenVAS / Greenbone / GVM

Install:

```bash
sudo apt install -y gvm
```

Initial setup:

```bash
sudo gvm-setup
sudo gvm-check-setup
```

If `gvm-check-setup` complains about missing CA certificates, Kali's current docs show this fix:

```bash
sudo runuser -u _gvm -- gvm-manage-certs -a -f
sudo gvm-check-setup
```

Start services:

```bash
sudo gvm-start
```

Current Kali docs show the default web UI at:

```text
https://127.0.0.1:9392
```

Stop services:

```bash
sudo gvm-stop
```

Recommended dataset workflow:

1. Open Greenbone Security Assistant at `https://127.0.0.1:9392`
2. Log in with the admin account created during setup
3. Create a Target
4. Create a Task
5. Run the scan
6. Open the finished Report
7. Export as XML

What to keep for the dataset:

- `report.xml`
- target IP / hostname
- scan date
- severity
- CVE references
- NVT / finding title

Expected XML shape:

```xml
<result id="...">
  <name>Apache Struts Remote Code Execution Vulnerability</name>
  <host>192.168.56.101</host>
  <port>8080/tcp</port>
  <severity>10.0</severity>
  <nvt>
    <name>Apache Struts Remote Code Execution Vulnerability</name>
    <refs>
      <ref type="cve" id="CVE-2017-5638"/>
    </refs>
  </nvt>
</result>
```

Interpretation:

- `name` = finding title
- `host` = scanned asset
- `port` = affected service
- `severity` = numeric severity
- `ref type="cve"` = direct CVE label for supervised data

### ZAP

Docker baseline scan:

```bash
mkdir -p ~/reports/zap
docker run --rm -v "$HOME/reports/zap:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://TARGET:PORT -J zap.json -r zap.html -x zap.xml
```

Docker full scan:

```bash
docker run --rm -v "$HOME/reports/zap:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-full-scan.py -t http://TARGET:PORT -J full.json -r full.html -x full.xml
```

Expected JSON shape:

```json
{
  "site": [
    {
      "name": "http://TARGET:PORT",
      "alerts": [
        {
          "name": "X-Frame-Options Header Not Set",
          "riskcode": "2",
          "confidence": "2",
          "cweid": "1021"
        }
      ]
    }
  ]
}
```

### Nikto

```bash
nikto -h http://TARGET:PORT -o ~/reports/nikto/target1.json -Format json
```

HTML:

```bash
nikto -h http://TARGET:PORT -o ~/reports/nikto/target1.html -Format htm
```

Expected JSON shape:

```json
{
  "host": "TARGET",
  "port": 80,
  "vulnerabilities": [
    {
      "id": "headers",
      "msg": "X-Content-Type-Options header is not set",
      "url": "http://TARGET:PORT/"
    }
  ]
}
```

### sqlmap

Basic:

```bash
python sqlmap.py -u "http://TARGET/item.php?id=1" --batch --output-dir ~/reports/sqlmap/target1
```

POST request from raw request:

```bash
python sqlmap.py -r request.txt --batch --output-dir ~/reports/sqlmap/request1
```

Expected console evidence:

```text
[INFO] GET parameter 'id' appears to be injectable
---
Parameter: id (GET)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
---
```

### Metasploit

Start console:

```bash
msfconsole -q
```

Inside Metasploit:

```text
search cve:2022-22965
use <module_name>
show options
set RHOSTS TARGET_IP
set RPORT TARGET_PORT
run
```

You can save commands in a resource file, for example `spring4shell.rc`:

```text
search cve:2022-22965
use <module_name>
set RHOSTS TARGET_IP
set RPORT TARGET_PORT
run
exit -y
```

Run it:

```bash
msfconsole -q -r spring4shell.rc | tee ~/reports/msf/spring4shell.txt
```

Expected text evidence:

```text
[+] TARGET:PORT - The target appears to be vulnerable
[*] Command shell session 1 opened
```

## 7) Import results into Faraday

Faraday is best when you already have report files.

### Reports that import well

- Nmap XML
- Nuclei JSON
- ZAP XML/JSON
- Nikto

### Through Web UI

1. Open `http://localhost:5985`
2. Create a workspace
3. Go to Vulnerabilities
4. `+ Add Vulnerability`
5. `Import from file`
6. Upload report

### Notes

If a report is not detected, Faraday docs suggest renaming with plugin hints like:

```bash
mv target1.xml target1_faraday_Nmap.xml
mv nuclei.json nuclei_faraday_Nuclei.json
```

## 8) Import results into DefectDojo

DefectDojo is the best central findings store for dataset work.

### Through Web UI

1. Open DefectDojo
2. Create Product
3. Create Engagement
4. Import Scan
5. Select scan type
6. Upload report

### Recommended scan types

- Nmap Scan
- Nuclei Scan
- ZAP Scan
- Nikto Scan

### Reimport workflow

Use reimport when you rescan the same target over time.

This gives you:

- newly created findings
- left untouched findings
- closed findings
- reactivated findings

That is excellent for dataset labels.

## 9) Import results into Reconmap

Reconmap is useful for project context and reporting.

### Start platform

```bash
cd ~/sec-platforms/reconmap
docker compose up -d
```

### UI flow

1. Open dashboard on `http://localhost:5500`
2. Create a project
3. Go to Scans
4. Choose a scan or import a scan result
5. Attach results to the selected project

According to current docs, Reconmap can parse outputs such as:

- Nmap XML
- Subfinder
- Testssl
- SARIF JSON
- CycloneDX JSON

## 10) Suggested dataset schema

```json
{
  "platform": "defectdojo",
  "tool": "nuclei",
  "project": "spring-lab",
  "target": "http://192.168.56.101:8080",
  "scenario_id": "spring-CVE-2022-22965",
  "cve_id": "CVE-2022-22965",
  "finding_name": "spring4shell-rce",
  "severity": "critical",
  "status": "active",
  "label": "positive",
  "raw_report_path": "/home/kali/reports/nuclei/target1.json"
}
```

### Minimum columns I recommend

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

### Extra columns from Faraday

- `host`
- `service`
- `port`
- `protocol`
- `product`
- `version`

### Extra columns from Reconmap

- `project_name`
- `client_name`
- `task_name`
- `report_revision`

## 11) Recommended v1 dataset plan

### Main source of truth

- `DefectDojo`

### Enrichment

- `Faraday`

### Context

- `Reconmap`

### Labs

- `struts2/s2-045`
- `spring/CVE-2022-22965`
- `django/CVE-2022-34265`

### Scanners

- `Nmap`
- `Nuclei`
- `ZAP`
- `Nikto`
- `sqlmap`
- `Metasploit`

## 12) Useful cleanup and status commands

### Docker

```bash
docker ps
docker compose ps
docker compose logs -f
docker compose down
docker compose down -v
```

### Check ports

```bash
ss -tulpn
```

### Check platform containers

```bash
cd ~/sec-platforms/faraday && docker compose ps
cd ~/sec-platforms/django-DefectDojo && docker compose ps
cd ~/sec-platforms/reconmap && docker compose ps
```

## 13) Recommended order of work

1. Start `DefectDojo`
2. Start `Faraday`
3. Start one Vulhub lab
4. Run `Nmap`
5. Run `Nuclei`
6. Run `ZAP` or `Nikto`
7. Run `sqlmap` only on SQLi scenarios
8. Run `Metasploit` for verification
9. Import into `DefectDojo`
10. Import into `Faraday`
11. Add project/report context in `Reconmap`

## 14) Fixed workflow where you only change IP and port

If you want the simplest repeatable process, treat every target as only:

- `TARGET_IP`
- `TARGET_PORT`

Then run the same sequence every time.

### Target map for the recommended local labs

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

### Recommended order per target

1. `Nmap`
2. `Nuclei`
3. `OpenVAS / GVM`
4. `ZAP`
5. `Nikto`
6. `sqlmap` only if the app has a query parameter or POST parameter
7. `Metasploit` only for verification
8. Import reports into `DefectDojo`
9. Import reports into `Faraday`
10. Optionally attach project context in `Reconmap`

### Reusable shell template

Change only `TARGET_IP`, `TARGET_PORT`, and `TARGET_NAME`:

```bash
TARGET_IP=127.0.0.11
TARGET_PORT=18080
TARGET_NAME=struts2_s2045
TARGET_URL="http://${TARGET_IP}:${TARGET_PORT}"

mkdir -p ~/reports/{nmap,nuclei,zap,nikto,sqlmap,msf}

# 1) Nmap
nmap -sV -O -oX ~/reports/nmap/${TARGET_NAME}.xml "${TARGET_IP}"

# 2) Nuclei
nuclei -u "${TARGET_URL}" -json-export ~/reports/nuclei/${TARGET_NAME}.json

# 3) ZAP
docker run --rm -v "$HOME/reports/zap:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t "${TARGET_URL}" -J "${TARGET_NAME}.json" -r "${TARGET_NAME}.html"

# 4) Nikto
nikto -h "${TARGET_URL}" -o ~/reports/nikto/${TARGET_NAME}.json -Format json
```

### Add sqlmap only for SQLi-style apps

For GET parameter targets:

```bash
TARGET_IP=127.0.0.14
TARGET_PORT=18000
TARGET_NAME=django_34265
SQLMAP_URL="http://${TARGET_IP}:${TARGET_PORT}/?date=minute"

python sqlmap.py -u "${SQLMAP_URL}" --batch --output-dir ~/reports/sqlmap/${TARGET_NAME}
```

### Add Metasploit only for exploit verification

```bash
msfconsole -q
```

Then inside:

```text
search cve:2022-22965
use <module_name>
set RHOSTS 127.0.0.12
set RPORT 28080
run
```

### Import order after scanning

#### DefectDojo first

- import `Nmap XML`
- import `Nuclei JSON`
- import `ZAP JSON/XML`
- import `Nikto JSON`
- reimport on later scans to create lifecycle labels

#### Faraday second

- import `Nmap XML`
- import `Nuclei JSON`
- import `ZAP`

#### Reconmap last

- attach scan outputs to the relevant project if you need project/report metadata

### One target at a time examples

#### Struts2

```bash
TARGET_IP=127.0.0.11
TARGET_PORT=18080
TARGET_NAME=struts2_s2045
TARGET_URL="http://${TARGET_IP}:${TARGET_PORT}"

nmap -sV -O -oX ~/reports/nmap/${TARGET_NAME}.xml "${TARGET_IP}"
nuclei -u "${TARGET_URL}" -json-export ~/reports/nuclei/${TARGET_NAME}.json
docker run --rm -v "$HOME/reports/zap:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t "${TARGET_URL}" -J "${TARGET_NAME}.json" -r "${TARGET_NAME}.html"
nikto -h "${TARGET_URL}" -o ~/reports/nikto/${TARGET_NAME}.json -Format json
```

#### Spring4Shell

```bash
TARGET_IP=127.0.0.12
TARGET_PORT=28080
TARGET_NAME=spring_22965
TARGET_URL="http://${TARGET_IP}:${TARGET_PORT}"

nmap -sV -O -oX ~/reports/nmap/${TARGET_NAME}.xml "${TARGET_IP}"
nuclei -u "${TARGET_URL}" -json-export ~/reports/nuclei/${TARGET_NAME}.json
docker run --rm -v "$HOME/reports/zap:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t "${TARGET_URL}" -J "${TARGET_NAME}.json" -r "${TARGET_NAME}.html"
nikto -h "${TARGET_URL}" -o ~/reports/nikto/${TARGET_NAME}.json -Format json
```

#### Log4Shell

```bash
TARGET_IP=127.0.0.13
TARGET_PORT=18983
TARGET_NAME=log4j_44228
TARGET_URL="http://${TARGET_IP}:${TARGET_PORT}"

nmap -sV -O -oX ~/reports/nmap/${TARGET_NAME}.xml "${TARGET_IP}"
nuclei -u "${TARGET_URL}" -json-export ~/reports/nuclei/${TARGET_NAME}.json
docker run --rm -v "$HOME/reports/zap:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t "${TARGET_URL}" -J "${TARGET_NAME}.json" -r "${TARGET_NAME}.html"
nikto -h "${TARGET_URL}" -o ~/reports/nikto/${TARGET_NAME}.json -Format json
```

#### Django SQLi

```bash
TARGET_IP=127.0.0.14
TARGET_PORT=18000
TARGET_NAME=django_34265
TARGET_URL="http://${TARGET_IP}:${TARGET_PORT}"

nmap -sV -O -oX ~/reports/nmap/${TARGET_NAME}.xml "${TARGET_IP}"
nuclei -u "${TARGET_URL}" -json-export ~/reports/nuclei/${TARGET_NAME}.json
docker run --rm -v "$HOME/reports/zap:/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t "${TARGET_URL}" -J "${TARGET_NAME}.json" -r "${TARGET_NAME}.html"
nikto -h "${TARGET_URL}" -o ~/reports/nikto/${TARGET_NAME}.json -Format json
python sqlmap.py -u "${TARGET_URL}/?date=minute" --batch --output-dir ~/reports/sqlmap/${TARGET_NAME}
```

## Sources

- Faraday Docker install docs
- Faraday import docs
- Faraday plugin docs
- DefectDojo install docs
- DefectDojo reimport docs
- DefectDojo deduplication docs
- Reconmap features docs
- Reconmap deployment docs
- Reconmap command result processing docs
- Vulhub docs
- Nuclei docs
- ZAP Docker docs
- Nikto README
- sqlmap usage wiki
- Nmap output docs
- Metasploit module usage docs
