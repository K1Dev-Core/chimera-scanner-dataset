# Blueprint สำหรับ Scanner Dataset

ตรวจและเตรียมไว้เมื่อ 2026-08-03

## คำตอบสั้น ๆ

ถ้าเป้าหมายคือทำ dataset ที่ใช้ได้จริง ไม่ควรบังคับให้ทุก tool ต้องหา CVE เดียวกันให้เจอทั้งหมด เพราะ tool แต่ละตัวถูกออกแบบมาคนละแบบ

ควรแบ่งเป็น 2 track:

| track | เหมาะกับ tool | ใช้ทำอะไร |
| --- | --- | --- |
| CVE-focused | `Nuclei`, `Greenbone/OpenVAS`, `Metasploit` | หา/ยืนยันช่องโหว่ที่โยงกับ CVE ได้ชัด |
| Web-finding | `OWASP ZAP`, `Nikto`, `sqlmap` | เก็บ web finding, misconfiguration, SQLi, header issue |

`Faraday`, `DefectDojo`, และ `Reconmap` ควรมองเป็นระบบรับข้อมูล/normalize/reporting ไม่ใช่ scanner หลัก

## CVE ที่เหมาะเริ่มต้น

แนะนำจาก Vulhub เพราะ reproducible และรู้จักกันดี:

1. `CVE-2017-5638` Apache Struts2 S2-045 RCE
2. `CVE-2021-44228` Log4Shell
3. `CVE-2022-22965` Spring4Shell

เหมาะกับ `Nuclei`, `Greenbone/OpenVAS`, `Metasploit`

ไม่เหมาะมากกับ `sqlmap`, `Nikto`, `ZAP` ถ้าต้องการให้ detect CVE เดียวกันตรง ๆ เพราะสามตัวนี้มักรายงานจากพฤติกรรมหรือ rule ทั่วไปมากกว่า

## โครงสร้าง record ที่แนะนำ

ใช้หนึ่งแถวต่อหนึ่ง finding attempt:

```json
{
  "tool": "nuclei",
  "tool_category": "scanner",
  "scenario_source": "vulhub",
  "scenario": "spring/CVE-2022-22965",
  "target_url": "http://TARGET:PORT",
  "ground_truth_type": "cve",
  "ground_truth_id": "CVE-2022-22965",
  "label": "positive",
  "finding_id": "spring4shell-rce",
  "severity": "critical",
  "evidence_summary": "Template matched vulnerable behavior",
  "raw_report_path": "reports/nuclei.jsonl"
}
```

## Matrix การใช้ tool

| Tool | ใช้ดีที่สุดกับอะไร | ควร map เป็น CVE ไหม |
| --- | --- | --- |
| Nuclei | direct vuln detection | ใช่ |
| Greenbone/OpenVAS | network/service vuln report | ใช่ ถ้ามี CVE reference |
| Metasploit | verification/exploitability | ใช่ |
| ZAP | alert/rule output | ส่วนใหญ่ไม่ |
| Nikto | server/web findings | ส่วนใหญ่ไม่ |
| sqlmap | SQL injection detection | ใช้กับ SQLi track แยก |
| Faraday | result aggregation | เป็น imported view |
| DefectDojo | ingestion/dedupe | เป็น findings store |
| Reconmap | project/engagement context | เป็น context |

## แผน practical starter

Track A: CVE dataset

- `CVE-2017-5638`
- `CVE-2021-44228`
- `CVE-2022-22965`

รัน:

- `Nuclei`
- `Greenbone/OpenVAS`
- `Metasploit`

Track B: Web app findings

- ใช้ lab ที่มี SQLi หรือ web vulnerability ชัดเจน
- รัน `sqlmap`, `ZAP`, `Nikto`

## Fields ที่ควร normalize

- `tool`
- `target`
- `ground_truth_id`
- `finding_name`
- `severity`
- `confidence`
- `evidence`
- `raw_location`
- `label`

label ที่แนะนำ:

- `positive` tool เจอ issue ที่ตั้งใจปลูกไว้
- `negative` ไม่พบ finding ที่เกี่ยวข้อง
- `partial` เจอ symptom แต่ยังไม่ยืนยัน root cause
- `noise` finding ไม่เกี่ยวกับโจทย์

## บทบาทของ platform

- `Faraday`: รวม multi-tool findings
- `DefectDojo`: dedupe/import/reimport และ lifecycle ของ finding
- `Reconmap`: project, engagement, asset context

สำหรับ dataset ให้ถือ raw scanner artifacts เป็น source of truth และใช้ export จาก platform เป็นมุมมองรอง

## ลำดับงานที่แนะนำ

1. เปิด Vulhub scenario หนึ่งตัว เช่น Struts2
2. รัน `Nuclei`
3. รัน `Metasploit` เพื่อ verify
4. export `Greenbone/OpenVAS` report
5. เก็บ raw output ทั้งหมด
6. เปิด SQLi lab แยกเพื่อรัน `sqlmap`, `ZAP`, `Nikto`

แนวทางนี้ให้ dataset คุณภาพดีกว่าการบังคับให้ทุก scanner ไล่หา CVE เดียวกันทั้งหมด
