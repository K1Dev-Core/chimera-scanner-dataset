# Scanner Dataset Blueprint

Verified and prepared on 2026-08-03.

## Short answer

If your goal is to build a usable dataset, do **not** force every tool to detect the exact same CVE.

Use two tracks:

1. **CVE-focused track** for tools that naturally emit CVE-like findings
   - Nuclei
   - Greenbone / OpenVAS
   - Metasploit

2. **Web-finding track** for tools that naturally emit rule- or behavior-based findings
   - OWASP ZAP
   - Nikto
   - sqlmap

Platforms like **Faraday**, **DefectDojo**, and **Reconmap** should be treated as **ingestion / normalization targets**, not as primary scanners.

## Best starter CVEs

Pick these three from Vulhub because they are common, well-known, and usually easy to reproduce:

1. `CVE-2017-5638` - Apache Struts2 S2-045 RCE
2. `CVE-2021-44228` - Log4Shell
3. `CVE-2022-22965` - Spring4Shell

These are good for:
- Nuclei
- Greenbone / OpenVAS
- Metasploit

They are **not ideal** for:
- sqlmap
- Nikto
- ZAP

For `sqlmap`, use a dedicated SQL injection lab instead of forcing one of the CVEs above.

## Recommended dataset design

Use one row per finding attempt:

```json
{
  "tool": "nuclei",
  "tool_category": "scanner",
  "scenario_source": "vulhub",
  "scenario": "spring/CVE-2022-22965",
  "target_url": "http://192.168.56.101:8080",
  "ground_truth_type": "cve",
  "ground_truth_id": "CVE-2022-22965",
  "label": "positive",
  "scan_command": "nuclei -u http://192.168.56.101:8080 -jle nuclei.jsonl",
  "report_format": "jsonl",
  "finding_id": "spring4shell-rce",
  "severity": "critical",
  "evidence_summary": "Template matched vulnerable behavior",
  "raw_report_path": "reports/nuclei.jsonl",
  "normalized_fields": {
    "host": "192.168.56.101",
    "port": 8080,
    "protocol": "http"
  }
}
```

## Coverage matrix

| Tool | Best use in dataset | Should map to CVE? | Suggested target |
|---|---|---:|---|
| Nuclei | direct vuln detection | yes | Struts / Log4Shell / Spring4Shell |
| Greenbone | network/service vuln report | yes, when available | same 3 CVEs |
| Metasploit | verification / exploitability | yes | same 3 CVEs |
| ZAP | alert/rule output | usually no | generic vulnerable web app |
| Nikto | server/web findings | usually no | generic vulnerable web app |
| sqlmap | SQLi detection and extraction | no, or separate SQLi CVE only | SQLi lab |
| Faraday | result aggregation | imported | all |
| DefectDojo | result ingestion / dedupe | imported | all |
| Reconmap | engagement/project tracking | imported/manual | all |

## Exact recommendation

If you want one practical starter set:

### Track A: CVE dataset

- `CVE-2017-5638`
- `CVE-2021-44228`
- `CVE-2022-22965`

Run:
- Nuclei
- Greenbone
- Metasploit

### Track B: Web app findings dataset

Use a purposely SQLi-capable lab for:
- sqlmap
- ZAP
- Nikto

If you must stay in Vulhub, choose a web scenario with an injectable parameter. If you only care about dataset quality, a dedicated SQLi training app is cleaner than trying to force SQLi into the same CVE track.

## Example commands

## 1) Nuclei

Official docs support JSONL export.

```bash
nuclei -u http://TARGET:PORT -jle nuclei.jsonl
```

Example finding shape:

```json
{
  "template-id": "spring4shell-rce",
  "info": {
    "name": "Spring4Shell RCE",
    "severity": "critical"
  },
  "host": "http://TARGET:PORT",
  "matched-at": "http://TARGET:PORT/",
  "type": "http"
}
```

## 2) ZAP

ZAP is better stored as alert output, not CVE output.

```bash
zaproxy -cmd -quickurl http://TARGET:PORT -quickout zap-report.json
```

Typical alert shape:

```json
{
  "site": [
    {
      "name": "http://TARGET:PORT",
      "alerts": [
        {
          "riskcode": "2",
          "confidence": "2",
          "name": "X-Frame-Options Header Not Set",
          "cweid": "1021",
          "wascid": "15",
          "instances": [
            {
              "uri": "http://TARGET:PORT/"
            }
          ]
        }
      ]
    }
  ]
}
```

## 3) Nikto

Nikto supports JSON, XML, CSV, HTML, SQL, and text export.

```bash
nikto -h http://TARGET:PORT -o nikto.json -Format json
```

Typical finding shape:

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

## 4) sqlmap

sqlmap is best for a separate SQLi dataset. It can store results in CSV, HTML, SQLITE, and JSONL.

```bash
sqlmap -u "http://TARGET/item.php?id=1" --batch --output-dir sqlmap-output
```

Typical console finding shape:

```text
[INFO] testing if the target URL content is stable
[INFO] GET parameter 'id' appears to be dynamic
[INFO] GET parameter 'id' appears to be injectable
---
Parameter: id (GET)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
---
```

## 5) Greenbone / OpenVAS

Use XML export as the richest machine-readable source.

Typical result shape:

```xml
<result id="...">
  <name>Apache Struts Remote Code Execution Vulnerability</name>
  <host>TARGET</host>
  <port>8080/tcp</port>
  <severity>10.0</severity>
  <nvt>
    <refs>
      <ref type="cve" id="CVE-2017-5638"/>
    </refs>
  </nvt>
</result>
```

## 6) Metasploit

Use this as exploit-verification evidence instead of your only scanner dataset source.

Typical scanner module console shape:

```text
[*] Scanning 1 of 1 hosts
[+] TARGET:PORT - Vulnerable to CVE-2021-44228
[*] Auxiliary module execution completed
```

## Best practical lab plan

### Lab 1: Struts2 / `CVE-2017-5638`

Collect:
- Nuclei JSONL
- Greenbone XML
- Metasploit console output
- Optional ZAP/Nikto baseline web findings

### Lab 2: Log4Shell / `CVE-2021-44228`

Collect:
- Nuclei JSONL
- Greenbone XML
- Metasploit scanner/exploit evidence

### Lab 3: Spring4Shell / `CVE-2022-22965`

Collect:
- Nuclei JSONL
- Greenbone XML
- Metasploit evidence

### Lab 4: SQLi app

Collect:
- sqlmap console + output directory artifacts
- ZAP JSON report
- Nikto JSON report

## Normalization tips

For dataset use these normalized fields across all tools:

- `tool`
- `target`
- `ground_truth_id`
- `finding_name`
- `severity`
- `confidence`
- `evidence`
- `raw_location`
- `label`

Recommended labels:

- `positive` = tool correctly detected planted issue
- `negative` = tool produced no relevant finding
- `partial` = tool found a symptom but not the exact root issue
- `noise` = unrelated finding

## Faraday / DefectDojo / Reconmap role

Use them after collection:

- **Faraday**: centralize multi-tool findings
- **DefectDojo**: dedupe and manage imported reports
- **Reconmap**: track engagements and assets

For dataset work, keep the **raw scanner artifacts** as the source of truth, and treat platform exports as secondary normalized views.

## Suggested first run

If you want the cleanest first dataset with the least pain:

1. Start one Vulhub scenario for `CVE-2017-5638`
2. Run Nuclei
3. Run Metasploit scanner
4. Export Greenbone report
5. Save all three raw outputs
6. Separately stand up one SQLi lab and run sqlmap + ZAP + Nikto

That gives you a much better dataset than forcing all tools to chase the same CVE.

## Sources

- [Vulhub](https://github.com/vulhub/vulhub)
- [Nuclei repo](https://github.com/projectdiscovery/nuclei)
- [Nuclei docs: get started](https://github.com/projectdiscovery/nuclei-docs/blob/main/docs/nuclei/get-started.md)
- [ZAP command line](https://www.zaproxy.org/docs/desktop/addons/quick-start/cmdline/)
- [ZAP report templates](https://www.zaproxy.org/docs/desktop/addons/report-generation/templates/)
- [Nikto README](https://github.com/sullo/nikto/blob/master/README.md)
- [sqlmap usage wiki](https://github.com/sqlmapproject/sqlmap/wiki/usage)
- [Greenbone reports](https://docs.greenbone.net/GSM-Manual/gos-24.10/en/reports.html)
- [Greenbone GMP report example](https://docs.greenbone.net/API/GMP/gmp-22.7.html)
