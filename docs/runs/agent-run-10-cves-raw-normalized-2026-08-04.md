# Agent Runbook: 10 CVEs with Raw + Normalized Outputs

Prepared for Kali on Tuesday, August 4, 2026.

This file replaces the earlier ad hoc runbooks and standardizes output layout as:

```text
~/dataset/raw/<tool-name>/<date>/<target>/*
~/dataset/normalized/<tool-name>/<date>/<target>.jsonl
```

Targets in this runbook:

Excluded because they already appear in your example image:

```text
nginx-ui-cve-2026-27944
n8n-cve-2026-21858
activemq-cve-2026-34197
nextjs-cve-2025-29927
jenkins-cve-2024-23897
geoserver-cve-2024-36401
log4j-cve-2021-44228
drupal-cve-2018-7600
```

Chosen 10 non-duplicate targets for this batch:

```text
1. struts2_s2045   -> Vulhub struts2/s2-045               -> CVE-2017-5638
2. spring_22965    -> Vulhub spring/CVE-2022-22965        -> CVE-2022-22965
3. django_34265    -> Vulhub django/CVE-2022-34265        -> CVE-2022-34265
4. apache_41773    -> Vulhub httpd/CVE-2021-41773         -> CVE-2021-41773
5. tomcat_12615    -> Vulhub tomcat/CVE-2017-12615        -> CVE-2017-12615
6. jackson_7525    -> Vulhub jackson/CVE-2017-7525        -> CVE-2017-7525
7. glassfish_1000028 -> Vulhub glassfish/CVE-2017-1000028 -> CVE-2017-1000028
8. druid_25646     -> Vulhub apache-druid/CVE-2021-25646  -> CVE-2021-25646
9. gogs_18925      -> Vulhub gogs/CVE-2018-18925          -> CVE-2018-18925
10. elfinder_32682 -> Vulhub elfinder/CVE-2021-32682      -> CVE-2021-32682
```

## 0) Base Variables

```bash
RUN_DATE=2026-08-04
DATA_ROOT=~/dataset
RAW_ROOT="${DATA_ROOT}/raw"
NORM_ROOT="${DATA_ROOT}/normalized"

mkdir -p "${RAW_ROOT}" "${NORM_ROOT}"
mkdir -p ~/reports
```

## 1) Raw + Normalized Paths

For one target at a time:

```bash
RAW_NMAP_DIR="${RAW_ROOT}/nmap/${RUN_DATE}/${LAB_NAME}"
RAW_HTTPX_DIR="${RAW_ROOT}/httpx-toolkit/${RUN_DATE}/${LAB_NAME}"
RAW_NAABU_DIR="${RAW_ROOT}/naabu/${RUN_DATE}/${LAB_NAME}"
RAW_NUCLEI_DIR="${RAW_ROOT}/nuclei/${RUN_DATE}/${LAB_NAME}"
RAW_WAPITI_DIR="${RAW_ROOT}/wapiti/${RUN_DATE}/${LAB_NAME}"
RAW_NIKTO_DIR="${RAW_ROOT}/nikto/${RUN_DATE}/${LAB_NAME}"
RAW_ZAP_DIR="${RAW_ROOT}/zaproxy/${RUN_DATE}/${LAB_NAME}"
RAW_SQLMAP_DIR="${RAW_ROOT}/sqlmap/${RUN_DATE}/${LAB_NAME}"
RAW_AUTORECON_DIR="${RAW_ROOT}/autorecon/${RUN_DATE}/${LAB_NAME}"
RAW_MSF_DIR="${RAW_ROOT}/metasploit/${RUN_DATE}/${LAB_NAME}"
RAW_OPENVAS_DIR="${RAW_ROOT}/openvas/${RUN_DATE}/${LAB_NAME}"

mkdir -p \
  "${RAW_NMAP_DIR}" "${RAW_HTTPX_DIR}" "${RAW_NAABU_DIR}" "${RAW_NUCLEI_DIR}" \
  "${RAW_WAPITI_DIR}" "${RAW_NIKTO_DIR}" "${RAW_ZAP_DIR}" "${RAW_SQLMAP_DIR}" \
  "${RAW_AUTORECON_DIR}" "${RAW_MSF_DIR}" "${RAW_OPENVAS_DIR}"

NORM_NMAP="${NORM_ROOT}/nmap/${RUN_DATE}/${LAB_NAME}.jsonl"
NORM_HTTPX="${NORM_ROOT}/httpx-toolkit/${RUN_DATE}/${LAB_NAME}.jsonl"
NORM_NAABU="${NORM_ROOT}/naabu/${RUN_DATE}/${LAB_NAME}.jsonl"
NORM_NUCLEI="${NORM_ROOT}/nuclei/${RUN_DATE}/${LAB_NAME}.jsonl"
NORM_WAPITI="${NORM_ROOT}/wapiti/${RUN_DATE}/${LAB_NAME}.jsonl"
NORM_NIKTO="${NORM_ROOT}/nikto/${RUN_DATE}/${LAB_NAME}.jsonl"
NORM_ZAP="${NORM_ROOT}/zaproxy/${RUN_DATE}/${LAB_NAME}.jsonl"
NORM_SQLMAP="${NORM_ROOT}/sqlmap/${RUN_DATE}/${LAB_NAME}.jsonl"
NORM_AUTORECON="${NORM_ROOT}/autorecon/${RUN_DATE}/${LAB_NAME}.jsonl"
NORM_MSF="${NORM_ROOT}/metasploit/${RUN_DATE}/${LAB_NAME}.jsonl"
NORM_OPENVAS="${NORM_ROOT}/openvas/${RUN_DATE}/${LAB_NAME}.jsonl"

mkdir -p \
  "$(dirname "${NORM_NMAP}")" "$(dirname "${NORM_HTTPX}")" "$(dirname "${NORM_NAABU}")" \
  "$(dirname "${NORM_NUCLEI}")" "$(dirname "${NORM_WAPITI}")" "$(dirname "${NORM_NIKTO}")" \
  "$(dirname "${NORM_ZAP}")" "$(dirname "${NORM_SQLMAP}")" "$(dirname "${NORM_AUTORECON}")" \
  "$(dirname "${NORM_MSF}")" "$(dirname "${NORM_OPENVAS}")"
```

## 2) Stop Old Labs First

```bash
cd ~/labs/vulhub/struts2/s2-045 && docker compose -f docker-compose.host.yml -p vh_struts2_s2045 down -v || true
cd ~/labs/vulhub/spring/CVE-2022-22965 && docker compose -f docker-compose.host.yml -p vh_spring_22965 down -v || true
cd ~/labs/vulhub/django/CVE-2022-34265 && docker compose -f docker-compose.host.yml -p vh_django_34265 down -v || true
cd ~/labs/vulhub/httpd/CVE-2021-41773 && docker compose -f docker-compose.host.yml -p vh_apache_41773 down -v || true
cd ~/labs/vulhub/tomcat/CVE-2017-12615 && docker compose -f docker-compose.host.yml -p vh_tomcat_12615 down -v || true
cd ~/labs/vulhub/jackson/CVE-2017-7525 && docker compose down -v || true
cd ~/labs/vulhub/glassfish/CVE-2017-1000028 && docker compose down -v || true
cd ~/labs/vulhub/apache-druid/CVE-2021-25646 && docker compose down -v || true
cd ~/labs/vulhub/gogs/CVE-2018-18925 && docker compose down -v || true
cd ~/labs/vulhub/elfinder/CVE-2021-32682 && docker compose down -v || true
```

## 3) Add Loopback Aliases for Fixed-IP Targets

```bash
sudo ip addr add 127.0.0.11/8 dev lo || true
sudo ip addr add 127.0.0.12/8 dev lo || true
sudo ip addr add 127.0.0.14/8 dev lo || true
sudo ip addr add 127.0.0.15/8 dev lo || true
sudo ip addr add 127.0.0.16/8 dev lo || true
```

## 4) Start the 5 Fixed-IP Labs We Already Validated

### Struts2 S2-045

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
```

```bash
LAB_NAME=struts2_s2045
LAB_HOST=127.0.0.11
LAB_PORT=18080
LAB_URL="http://${LAB_HOST}:${LAB_PORT}"
```

### Spring4Shell

```bash
cd ~/labs/vulhub/spring/CVE-2022-22965
cat > docker-compose.host.yml <<'EOF'
services:
  spring:
    image: vulhub/spring-webmvc:5.3.17
    ports:
      - "127.0.0.12:28080:8080"
EOF
docker compose -f docker-compose.host.yml -p vh_spring_22965 up -d
```

```bash
LAB_NAME=spring_22965
LAB_HOST=127.0.0.12
LAB_PORT=28080
LAB_URL="http://${LAB_HOST}:${LAB_PORT}"
```

### Django

```bash
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

```bash
LAB_NAME=django_34265
LAB_HOST=127.0.0.14
LAB_PORT=18000
LAB_URL="http://${LAB_HOST}:${LAB_PORT}"
```

### Apache

```bash
cd ~/labs/vulhub/httpd/CVE-2021-41773
cat > docker-compose.host.yml <<'EOF'
services:
  httpd:
    image: vulhub/httpd:2.4.49
    ports:
      - "127.0.0.15:18081:80"
EOF
docker compose -f docker-compose.host.yml -p vh_apache_41773 up -d
```

```bash
LAB_NAME=apache_41773
LAB_HOST=127.0.0.15
LAB_PORT=18081
LAB_URL="http://${LAB_HOST}:${LAB_PORT}"
```

### Tomcat

```bash
cd ~/labs/vulhub/tomcat/CVE-2017-12615
cat > docker-compose.host.yml <<'EOF'
services:
  tomcat:
    image: vulhub/tomcat:8.5
    ports:
      - "127.0.0.16:18082:8080"
EOF
docker compose -f docker-compose.host.yml -p vh_tomcat_12615 up -d
```

```bash
LAB_NAME=tomcat_12615
LAB_HOST=127.0.0.16
LAB_PORT=18082
LAB_URL="http://${LAB_HOST}:${LAB_PORT}"
```

## 5) Start the 5 Additional CVE Labs

These five are added to bring the batch to 10. Start them one at a time with the original compose and inspect the published port after boot.

### Jackson

```bash
cd ~/labs/vulhub/jackson/CVE-2017-7525
docker compose up -d
docker compose ps
```

Set `LAB_NAME`, `LAB_HOST`, `LAB_PORT`, `LAB_URL` from the published host port shown by `docker compose ps`.

### GlassFish

```bash
cd ~/labs/vulhub/glassfish/CVE-2017-1000028
docker compose up -d
docker compose ps
```

Set `LAB_NAME`, `LAB_HOST`, `LAB_PORT`, `LAB_URL` from the published host port shown by `docker compose ps`.

### Apache Druid

```bash
cd ~/labs/vulhub/apache-druid/CVE-2021-25646
docker compose up -d
docker compose ps
```

Set `LAB_NAME`, `LAB_HOST`, `LAB_PORT`, `LAB_URL` from the published host port shown by `docker compose ps`.

### Gogs

```bash
cd ~/labs/vulhub/gogs/CVE-2018-18925
docker compose up -d
docker compose ps
```

Set `LAB_NAME`, `LAB_HOST`, `LAB_PORT`, `LAB_URL` from the published host port shown by `docker compose ps`.

### elFinder

```bash
cd ~/labs/vulhub/elfinder/CVE-2021-32682
docker compose up -d
docker compose ps
```

Set `LAB_NAME`, `LAB_HOST`, `LAB_PORT`, `LAB_URL` from the published host port shown by `docker compose ps`.

## 6) Scanner Commands We Actually Used

For each target, set `LAB_NAME`, `LAB_HOST`, `LAB_PORT`, `LAB_URL`, then set paths from section 1.

### Nmap

Raw:

```bash
nmap -sV -sC -p "${LAB_PORT}" "${LAB_HOST}" \
  -oN "${RAW_NMAP_DIR}/scan.txt" \
  -oX "${RAW_NMAP_DIR}/scan.xml"
```

Normalized:

```bash
jq -n \
  --arg run_date "${RUN_DATE}" \
  --arg tool "nmap" \
  --arg target "${LAB_NAME}" \
  --arg host "${LAB_HOST}" \
  --arg port "${LAB_PORT}" \
  --arg raw_txt "${RAW_NMAP_DIR}/scan.txt" \
  --arg raw_xml "${RAW_NMAP_DIR}/scan.xml" \
  '{run_date:$run_date,tool:$tool,target:$target,host:$host,port:$port,raw_text_path:$raw_txt,raw_xml_path:$raw_xml,parser_status:"raw_only"}' \
  > "${NORM_NMAP}"
```

### httpx-toolkit

Raw:

```bash
httpx-toolkit -u "${LAB_URL}" -json -td -sc -title -server -o "${RAW_HTTPX_DIR}/scan.jsonl"
```

Normalized:

```bash
jq -c \
  --arg run_date "${RUN_DATE}" \
  --arg tool "httpx-toolkit" \
  --arg target "${LAB_NAME}" \
  '{run_date:$run_date,tool:$tool,target:$target,url:(.url // null),host:(.host // null),port:(.port // null),status_code:(.status_code // null),title:(.title // null),server:(.webserver // null),tech:(.tech // []),raw_source:"scan.jsonl"}' \
  "${RAW_HTTPX_DIR}/scan.jsonl" > "${NORM_HTTPX}"
```

### Naabu

Raw:

```bash
naabu -host "${LAB_HOST}" -p "${LAB_PORT}" -json -o "${RAW_NAABU_DIR}/scan.jsonl"
```

Normalized:

```bash
jq -c \
  --arg run_date "${RUN_DATE}" \
  --arg tool "naabu" \
  --arg target "${LAB_NAME}" \
  '{run_date:$run_date,tool:$tool,target:$target,host:(.host // null),ip:(.ip // null),port:(.port // null),protocol:(.protocol // "tcp"),raw_source:"scan.jsonl"}' \
  "${RAW_NAABU_DIR}/scan.jsonl" > "${NORM_NAABU}"
```

### Nuclei

Raw:

```bash
nuclei -u "${LAB_URL}" -jsonl -o "${RAW_NUCLEI_DIR}/scan.jsonl"
```

Normalized:

```bash
jq -c \
  --arg run_date "${RUN_DATE}" \
  --arg tool "nuclei" \
  --arg target "${LAB_NAME}" \
  '{run_date:$run_date,tool:$tool,target:$target,severity:(.info.severity // null),template_id:(."template-id" // null),name:(.info.name // null),matched_at:(."matched-at" // null),type:(.type // null),curl:(."curl-command" // null),extracted:(."extracted-results" // []),raw_source:"scan.jsonl"}' \
  "${RAW_NUCLEI_DIR}/scan.jsonl" > "${NORM_NUCLEI}"
```

### Wapiti

Raw:

```bash
wapiti -u "${LAB_URL}" -f json -o "${RAW_WAPITI_DIR}/scan.json"
```

Normalized:

```bash
jq -n \
  --arg run_date "${RUN_DATE}" \
  --arg tool "wapiti" \
  --arg target "${LAB_NAME}" \
  --arg raw_json "${RAW_WAPITI_DIR}/scan.json" \
  '{run_date:$run_date,tool:$tool,target:$target,raw_json_path:$raw_json,parser_status:"raw_saved"}' \
  > "${NORM_WAPITI}"
```

### Nikto

Raw:

```bash
nikto -h "${LAB_URL}" | tee "${RAW_NIKTO_DIR}/scan.txt"
```

Normalized:

```bash
jq -n \
  --arg run_date "${RUN_DATE}" \
  --arg tool "nikto" \
  --arg target "${LAB_NAME}" \
  --arg raw_txt "${RAW_NIKTO_DIR}/scan.txt" \
  '{run_date:$run_date,tool:$tool,target:$target,raw_text_path:$raw_txt,parser_status:"raw_only"}' \
  > "${NORM_NIKTO}"
```

### ZAP Baseline

Raw:

```bash
docker run --rm --network host ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t "${LAB_URL}" | tee "${RAW_ZAP_DIR}/scan.txt"
```

Normalized:

```bash
jq -n \
  --arg run_date "${RUN_DATE}" \
  --arg tool "zaproxy" \
  --arg target "${LAB_NAME}" \
  --arg raw_txt "${RAW_ZAP_DIR}/scan.txt" \
  '{run_date:$run_date,tool:$tool,target:$target,raw_text_path:$raw_txt,parser_status:"raw_only"}' \
  > "${NORM_ZAP}"
```

### AutoRecon

Raw:

```bash
sudo autorecon "${LAB_HOST}" --ports "${LAB_PORT}" -o "${RAW_AUTORECON_DIR}"
```

Normalized:

```bash
jq -n \
  --arg run_date "${RUN_DATE}" \
  --arg tool "autorecon" \
  --arg target "${LAB_NAME}" \
  --arg raw_dir "${RAW_AUTORECON_DIR}" \
  '{run_date:$run_date,tool:$tool,target:$target,raw_dir:$raw_dir,parser_status:"raw_dir_only"}' \
  > "${NORM_AUTORECON}"
```

### sqlmap

Use this only where there is a real parameter. The one we actually used today was Django:

Raw:

```bash
TARGET_URL="http://127.0.0.14:18000/?date=minute"
sqlmap -u "${TARGET_URL}" --batch --level=5 --risk=3 --tamper=space2comment --random-agent --flush-session | tee "${RAW_SQLMAP_DIR}/scan.txt"
```

Normalized:

```bash
jq -n \
  --arg run_date "${RUN_DATE}" \
  --arg tool "sqlmap" \
  --arg target "${LAB_NAME}" \
  --arg raw_txt "${RAW_SQLMAP_DIR}/scan.txt" \
  '{run_date:$run_date,tool:$tool,target:$target,raw_text_path:$raw_txt,parser_status:"raw_only"}' \
  > "${NORM_SQLMAP}"
```

## 7) Metasploit Verification

Initialize once if needed:

```bash
sudo msfdb init
```

Raw outputs:

```text
${RAW_MSF_DIR}/scan.txt
```

Normalized outputs:

```text
${NORM_MSF}
```

### Struts2

```text
spool ${RAW_MSF_DIR}/scan.txt
search cve:2017-5638
use exploit/multi/http/struts2_content_type_ognl
set RHOSTS 127.0.0.11
set RPORT 18080
set TARGETURI /
check
run
spool off
```

### Spring

```text
spool ${RAW_MSF_DIR}/scan.txt
search cve:2022-22965
use exploit/multi/http/spring_framework_rce_spring4shell
set RHOSTS 127.0.0.12
set RPORT 28080
set TARGETURI /
check
run
spool off
```

### Tomcat

```text
spool ${RAW_MSF_DIR}/scan.txt
search cve:2017-12615
use exploit/multi/http/tomcat_jsp_upload_bypass
set RHOSTS 127.0.0.16
set RPORT 18082
set TARGETURI /
check
run
spool off
```

### Apache

```text
spool ${RAW_MSF_DIR}/scan.txt
search cve:2021-41773
use <module returned by search>
set RHOSTS 127.0.0.15
set RPORT 18081
set TARGETURI /
check
run
spool off
```

Normalize Metasploit after each run:

```bash
jq -n \
  --arg run_date "${RUN_DATE}" \
  --arg tool "metasploit" \
  --arg target "${LAB_NAME}" \
  --arg raw_txt "${RAW_MSF_DIR}/scan.txt" \
  '{run_date:$run_date,tool:$tool,target:$target,raw_text_path:$raw_txt,parser_status:"raw_only"}' \
  > "${NORM_MSF}"
```

## 8) OpenVAS / GVM

Create one target and one task per lab in the GVM UI, or use `gvm-cli` if the UI start button is stuck.

Raw output path:

```text
${RAW_OPENVAS_DIR}/scan.xml
```

Normalized output path:

```text
${NORM_OPENVAS}
```

Export raw XML with:

```bash
REPORT_ID="PUT_REPORT_ID_HERE"
read -rsp "GVM password: " GVM_PASSWORD; echo
sudo runuser -u _gvm -- gvm-cli \
  --gmp-username admin \
  --gmp-password "${GVM_PASSWORD}" \
  socket \
  --xml "<get_reports report_id=\"$REPORT_ID\" details=\"1\" ignore_pagination=\"1\"/>" \
  > "${RAW_OPENVAS_DIR}/scan.xml"
```

Normalize:

```bash
jq -n \
  --arg run_date "${RUN_DATE}" \
  --arg tool "openvas" \
  --arg target "${LAB_NAME}" \
  --arg raw_xml "${RAW_OPENVAS_DIR}/scan.xml" \
  '{run_date:$run_date,tool:$tool,target:$target,raw_xml_path:$raw_xml,parser_status:"raw_xml_only"}' \
  > "${NORM_OPENVAS}"
```

## 9) Copy Out to the Host

VirtualBox shared folder path:

```text
/media/sf_kali-share
```

Archive and copy:

```bash
tar czf ~/dataset-${RUN_DATE}.tar.gz ~/dataset
cp ~/dataset-${RUN_DATE}.tar.gz /media/sf_kali-share/
ls -lh /media/sf_kali-share/
```

Host path:

```text
C:\Users\rapii\Desktop\kali-share\dataset-2026-08-04.tar.gz
```
