# Runbook Agent: 10 CVEs พร้อม Raw + Normalized Outputs

เตรียมสำหรับ Kali เมื่อ 2026-08-04

เอกสารนี้ใช้เป็น runbook มาตรฐานสำหรับสแกน Vulhub targets แล้วเก็บทั้ง raw output และ normalized output

## Layout ที่ใช้

```text
~/dataset/raw/<tool-name>/<date>/<target>/*
~/dataset/normalized/<tool-name>/<date>/<target>.jsonl
```

## Targets ในรอบนี้

เลือก 10 targets ที่ไม่ซ้ำกับตัวอย่างเดิม:

| target | Vulhub path | CVE |
| --- | --- | --- |
| `struts2_s2045` | `struts2/s2-045` | CVE-2017-5638 |
| `spring_22965` | `spring/CVE-2022-22965` | CVE-2022-22965 |
| `django_34265` | `django/CVE-2022-34265` | CVE-2022-34265 |
| `apache_41773` | `httpd/CVE-2021-41773` | CVE-2021-41773 |
| `tomcat_12615` | `tomcat/CVE-2017-12615` | CVE-2017-12615 |
| `jackson_7525` | `jackson/CVE-2017-7525` | CVE-2017-7525 |
| `glassfish_1000028` | `glassfish/CVE-2017-1000028` | CVE-2017-1000028 |
| `druid_25646` | `apache-druid/CVE-2021-25646` | CVE-2021-25646 |
| `gogs_18925` | `gogs/CVE-2018-18925` | CVE-2018-18925 |
| `elfinder_32682` | `elfinder/CVE-2021-32682` | CVE-2021-32682 |

## ตัวแปรพื้นฐาน

```bash
RUN_DATE=2026-08-04
DATA_ROOT=~/dataset
RAW_ROOT="${DATA_ROOT}/raw"
NORM_ROOT="${DATA_ROOT}/normalized"

mkdir -p "${RAW_ROOT}" "${NORM_ROOT}" ~/reports
```

## Paths ต่อ target

ตั้งค่า `LAB_NAME`, `LAB_HOST`, `LAB_PORT`, `LAB_URL` ก่อน แล้วสร้าง path ต่อ tool:

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

mkdir -p "${RAW_NMAP_DIR}" "${RAW_HTTPX_DIR}" "${RAW_NAABU_DIR}" "${RAW_NUCLEI_DIR}" \
  "${RAW_WAPITI_DIR}" "${RAW_NIKTO_DIR}" "${RAW_ZAP_DIR}" "${RAW_SQLMAP_DIR}" \
  "${RAW_AUTORECON_DIR}" "${RAW_MSF_DIR}" "${RAW_OPENVAS_DIR}"
```

## เริ่ม lab

หยุด lab เก่าก่อนเพื่อกัน port ชน:

```bash
docker ps
docker compose down -v || true
```

สำหรับ fixed-IP labs ให้เพิ่ม loopback aliases:

```bash
sudo ip addr add 127.0.0.11/8 dev lo || true
sudo ip addr add 127.0.0.12/8 dev lo || true
sudo ip addr add 127.0.0.14/8 dev lo || true
sudo ip addr add 127.0.0.15/8 dev lo || true
sudo ip addr add 127.0.0.16/8 dev lo || true
```

ตัวอย่าง Struts2:

```bash
cd ~/labs/vulhub/struts2/s2-045
docker compose -f docker-compose.host.yml -p vh_struts2_s2045 up -d

LAB_NAME=struts2_s2045
LAB_HOST=127.0.0.11
LAB_PORT=18080
LAB_URL="http://${LAB_HOST}:${LAB_PORT}"
```

## Scanner commands ที่ใช้

### Nmap

```bash
nmap -sV -sC -p "${LAB_PORT}" "${LAB_HOST}" \
  -oN "${RAW_NMAP_DIR}/scan.txt" \
  -oX "${RAW_NMAP_DIR}/scan.xml"
```

### httpx-toolkit

```bash
httpx-toolkit -u "${LAB_URL}" -json -td -sc -title -server -o "${RAW_HTTPX_DIR}/scan.jsonl"
```

### Naabu

```bash
naabu -host "${LAB_HOST}" -p "${LAB_PORT}" -json -o "${RAW_NAABU_DIR}/scan.jsonl"
```

### Nuclei

```bash
nuclei -u "${LAB_URL}" -jsonl -o "${RAW_NUCLEI_DIR}/scan.jsonl"
```

### Wapiti

```bash
wapiti -u "${LAB_URL}" -f json -o "${RAW_WAPITI_DIR}/scan.json"
```

### Nikto

```bash
nikto -h "${LAB_URL}" | tee "${RAW_NIKTO_DIR}/scan.txt"
```

### ZAP Baseline

```bash
docker run --rm --network host ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t "${LAB_URL}" | tee "${RAW_ZAP_DIR}/scan.txt"
```

### AutoRecon

```bash
sudo autorecon "${LAB_HOST}" --ports "${LAB_PORT}" -o "${RAW_AUTORECON_DIR}"
```

หมายเหตุ: output ของ AutoRecon มี path ยาวมากบน Windows รอบปัจจุบันจึงยังไม่ควร push raw tree นี้ตรง ๆ

### sqlmap

ใช้เฉพาะ target ที่มี parameter จริง เช่น Django:

```bash
TARGET_URL="http://127.0.0.14:18000/?date=minute"
sqlmap -u "${TARGET_URL}" --batch --level=5 --risk=3 --tamper=space2comment --random-agent --flush-session | tee "${RAW_SQLMAP_DIR}/scan.txt"
```

### Metasploit

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

## OpenVAS / GVM

สร้าง target และ task ผ่าน GVM UI หรือใช้ `gvm-cli` ถ้า UI start button ค้าง

raw output ที่ควรเก็บ:

```text
${RAW_OPENVAS_DIR}/scan.xml
```

## Copy ออกจาก Kali

shared folder ของ VirtualBox:

```text
/media/sf_kali-share
```

archive และ copy:

```bash
tar czf ~/dataset-${RUN_DATE}.tar.gz ~/dataset
cp ~/dataset-${RUN_DATE}.tar.gz /media/sf_kali-share/
ls -lh /media/sf_kali-share/
```

ฝั่ง Windows:

```text
C:\Users\rapii\Desktop\kali-share\dataset-2026-08-04.tar.gz
```
