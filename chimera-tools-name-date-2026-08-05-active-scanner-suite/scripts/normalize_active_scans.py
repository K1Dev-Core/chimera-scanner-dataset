from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-08-05"
TARGETS = {
    "acme-support": {
        "product": "Acme Support Portal",
        "target_url": "http://127.0.0.1:27000/",
        "docker_url": "http://host.docker.internal:27000/",
        "port": 27000,
        "known_families": ["sqli", "command-injection", "file-inclusion", "broken-access-control", "xss"],
    },
    "nova-devops": {
        "product": "Nova DevOps Console",
        "target_url": "http://127.0.0.1:27100/",
        "docker_url": "http://host.docker.internal:27100/",
        "port": 27100,
        "known_families": ["sqli", "command-injection", "file-inclusion", "ssrf", "broken-access-control"],
    },
}


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def load_json(path: Path):
    if not path.exists() or path.stat().st_size == 0:
        return None
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))


def normalize_nmap(lab_id: str, raw: Path) -> list[dict]:
    rows = []
    xml_path = raw / "nmap.xml"
    if not xml_path.exists() or xml_path.stat().st_size == 0:
        return rows
    root = ET.fromstring(xml_path.read_text(encoding="utf-8", errors="ignore"))
    for port in root.findall(".//port"):
        service = port.find("service")
        state = port.find("state")
        row = {
            "dataset_record_type": "service_fingerprint",
            "tool": "nmap",
            "lab_id": lab_id,
            "product": TARGETS[lab_id]["product"],
            "target_url": TARGETS[lab_id]["target_url"],
            "port": int(port.attrib.get("portid", 0)),
            "protocol": port.attrib.get("protocol", "tcp"),
            "state": state.attrib.get("state") if state is not None else "unknown",
            "service": service.attrib.get("name") if service is not None else "unknown",
            "service_product": service.attrib.get("product", "") if service is not None else "",
            "service_version": service.attrib.get("version", "") if service is not None else "",
            "service_extrainfo": service.attrib.get("extrainfo", "") if service is not None else "",
        }
        rows.append(row)
    return rows


def normalize_httpx(lab_id: str, raw: Path) -> list[dict]:
    path = raw / "httpx.jsonl"
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        rows.append(
            {
                "dataset_record_type": "web_fingerprint",
                "tool": "httpx",
                "lab_id": lab_id,
                "product": TARGETS[lab_id]["product"],
                "target_url": TARGETS[lab_id]["target_url"],
                "url": data.get("url"),
                "status_code": data.get("status_code"),
                "title": data.get("title", ""),
                "webserver": data.get("webserver", ""),
                "tech": data.get("tech", []),
                "content_type": data.get("content_type", ""),
                "content_length": data.get("content_length", 0),
                "words": data.get("words", 0),
                "lines": data.get("lines", 0),
            }
        )
    return rows


def normalize_nuclei(lab_id: str, raw: Path) -> list[dict]:
    path = raw / "nuclei.jsonl"
    rows = []
    if not path.exists():
        return rows
    lines = [line for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    if not lines:
        return [
            {
                "dataset_record_type": "scanner_status",
                "tool": "nuclei",
                "lab_id": lab_id,
                "product": TARGETS[lab_id]["product"],
                "target_url": TARGETS[lab_id]["target_url"],
                "finding_count": 0,
                "status": "completed_no_match",
            }
        ]
    for line in lines:
        data = json.loads(line)
        info = data.get("info", {}) or {}
        rows.append(
            {
                "dataset_record_type": "scanner_finding",
                "tool": "nuclei",
                "lab_id": lab_id,
                "product": TARGETS[lab_id]["product"],
                "target_url": TARGETS[lab_id]["target_url"],
                "template_id": data.get("template-id", ""),
                "severity": info.get("severity", ""),
                "name": info.get("name", ""),
                "matched_at": data.get("matched-at", ""),
            }
        )
    return rows


def normalize_nikto(lab_id: str, raw: Path) -> list[dict]:
    data = load_json(raw / "nikto.json")
    rows = []
    if not data:
        return rows
    for host in data:
        for finding in host.get("vulnerabilities", []):
            rows.append(
                {
                    "dataset_record_type": "scanner_finding",
                    "tool": "nikto",
                    "lab_id": lab_id,
                    "product": TARGETS[lab_id]["product"],
                    "target_url": TARGETS[lab_id]["target_url"],
                    "finding_id": finding.get("id", ""),
                    "method": finding.get("method", ""),
                    "path": finding.get("url", ""),
                    "message": finding.get("msg", ""),
                    "references": finding.get("references", ""),
                    "severity": "info",
                }
            )
    return rows


def normalize_wapiti(lab_id: str, raw: Path) -> list[dict]:
    data = load_json(raw / "wapiti.json")
    rows = []
    if not data:
        return rows
    vulns = data.get("vulnerabilities", {}) or data.get("vulnerability", {}) or {}
    for category, findings in vulns.items():
        if not findings:
            continue
        for finding in findings:
            rows.append(
                {
                    "dataset_record_type": "scanner_finding",
                    "tool": "wapiti",
                    "lab_id": lab_id,
                    "product": TARGETS[lab_id]["product"],
                    "target_url": TARGETS[lab_id]["target_url"],
                    "category": category,
                    "level": finding.get("level", ""),
                    "method": finding.get("method", ""),
                    "path": finding.get("path", finding.get("url", "")),
                    "parameter": finding.get("parameter", ""),
                    "info": finding.get("info", ""),
                }
            )
    if not rows:
        rows.append(
            {
                "dataset_record_type": "scanner_status",
                "tool": "wapiti",
                "lab_id": lab_id,
                "product": TARGETS[lab_id]["product"],
                "target_url": TARGETS[lab_id]["target_url"],
                "finding_count": 0,
                "status": "completed_no_structured_findings",
            }
        )
    return rows


def normalize_zap(lab_id: str, raw: Path) -> list[dict]:
    data = load_json(raw / "zap.json")
    rows = []
    if not data:
        return rows
    sites = data.get("site", [])
    for site in sites:
        for alert in site.get("alerts", []):
            rows.append(
                {
                    "dataset_record_type": "scanner_finding",
                    "tool": "zap",
                    "lab_id": lab_id,
                    "product": TARGETS[lab_id]["product"],
                    "target_url": TARGETS[lab_id]["target_url"],
                    "plugin_id": alert.get("pluginid", ""),
                    "alert": alert.get("alert", ""),
                    "risk": alert.get("riskdesc", alert.get("riskcode", "")),
                    "confidence": alert.get("confidence", ""),
                    "count": alert.get("count", ""),
                    "description": re.sub(r"\s+", " ", alert.get("desc", ""))[:500],
                    "cweid": alert.get("cweid", ""),
                    "wascid": alert.get("wascid", ""),
                }
            )
    return rows


NORMALIZERS = {
    "nmap": normalize_nmap,
    "httpx": normalize_httpx,
    "nuclei": normalize_nuclei,
    "nikto": normalize_nikto,
    "wapiti": normalize_wapiti,
    "zap": normalize_zap,
}


def main() -> None:
    all_rows: list[dict] = []
    summary_rows: list[dict] = []
    tools_root = ROOT / "datasets" / "tools-name-date"
    for tool, normalizer in NORMALIZERS.items():
        for lab_id in TARGETS:
            raw = tools_root / f"{tool}-{DATE}" / lab_id / "raw"
            normalized = tools_root / f"{tool}-{DATE}" / lab_id / "normalized"
            rows = normalizer(lab_id, raw)
            write_jsonl(normalized / f"{tool}-normalized.jsonl", rows)
            all_rows.extend(rows)
            finding_count = sum(1 for row in rows if row.get("dataset_record_type") == "scanner_finding")
            summary_rows.append(
                {
                    "lab_id": lab_id,
                    "product": TARGETS[lab_id]["product"],
                    "target_url": TARGETS[lab_id]["target_url"],
                    "tool": tool,
                    "records": len(rows),
                    "finding_count": finding_count,
                    "raw_path": str(raw.relative_to(ROOT)).replace("\\", "/"),
                    "normalized_path": str((normalized / f"{tool}-normalized.jsonl").relative_to(ROOT)).replace("\\", "/"),
                }
            )
    records_dir = ROOT / "records"
    derived_dir = ROOT / "derived"
    manifests_dir = ROOT / "manifests"
    records_dir.mkdir(exist_ok=True)
    derived_dir.mkdir(exist_ok=True)
    manifests_dir.mkdir(exist_ok=True)
    write_jsonl(records_dir / "all-records.jsonl", all_rows)

    with (derived_dir / "active_scan_summary.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    feature_rows = []
    by_lab: dict[str, list[dict]] = {lab: [] for lab in TARGETS}
    for row in all_rows:
        by_lab.setdefault(row["lab_id"], []).append(row)
    for lab_id, rows in by_lab.items():
        tool_counts = {tool: sum(1 for row in rows if row.get("tool") == tool and row.get("dataset_record_type") == "scanner_finding") for tool in NORMALIZERS}
        nmap_rows = [row for row in rows if row.get("tool") == "nmap"]
        httpx_rows = [row for row in rows if row.get("tool") == "httpx"]
        zap_rows = [row for row in rows if row.get("tool") == "zap"]
        feature_rows.append(
            {
                "lab_id": lab_id,
                "product": TARGETS[lab_id]["product"],
                "target_url": TARGETS[lab_id]["target_url"],
                "port": TARGETS[lab_id]["port"],
                "service_product": " | ".join(sorted({row.get("service_product", "") for row in nmap_rows if row.get("service_product")})) or "none",
                "service_version": " | ".join(sorted({row.get("service_version", "") for row in nmap_rows if row.get("service_version")})) or "none",
                "http_title": " | ".join(sorted({row.get("title", "") for row in httpx_rows if row.get("title")})) or "none",
                "http_tech": " | ".join(sorted({tech for row in httpx_rows for tech in row.get("tech", [])})) or "none",
                "has_nmap_evidence": 1 if nmap_rows else 0,
                "has_httpx_evidence": 1 if httpx_rows else 0,
                "has_nuclei_evidence": 1 if tool_counts["nuclei"] > 0 else 0,
                "has_nikto_evidence": 1 if tool_counts["nikto"] > 0 else 0,
                "has_wapiti_evidence": 1 if tool_counts["wapiti"] > 0 else 0,
                "has_zap_evidence": 1 if tool_counts["zap"] > 0 else 0,
                "nuclei_finding_count": tool_counts["nuclei"],
                "nikto_finding_count": tool_counts["nikto"],
                "wapiti_finding_count": tool_counts["wapiti"],
                "zap_finding_count": tool_counts["zap"],
                "zap_alerts": " | ".join(sorted({row.get("alert", "") for row in zap_rows if row.get("alert")}))[:1000],
                "known_families": " | ".join(TARGETS[lab_id]["known_families"]),
                "label_source": "custom_lab_intended_vulnerability_family_plus_scanner_evidence",
                "label_warning": "Intended lab labels and scanner evidence; still add exploit_success_observed for final training.",
            }
        )
    with (derived_dir / "active_target_features.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(feature_rows[0].keys()))
        writer.writeheader()
        writer.writerows(feature_rows)

    manifest = {
        "name": "chimera-tools-name-date-2026-08-05-active-scanner-suite",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Active scanner collection against local Docker labs only.",
        "tools": list(NORMALIZERS.keys()),
        "targets": TARGETS,
        "counts": {
            "targets": len(TARGETS),
            "tools": len(NORMALIZERS),
            "tool_target_runs": len(summary_rows),
            "normalized_records": len(all_rows),
            "scanner_findings": sum(row["finding_count"] for row in summary_rows),
        },
    }
    (manifests_dir / "index.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (ROOT / "README.md").write_text(
        f"""# Chimera Active Scanner Suite Dataset ({DATE})

ชุดนี้เป็น active scan dataset ที่รันกับ local Docker labs ที่เราควบคุมเอง

## Tools

- nmap
- httpx
- nuclei
- nikto
- wapiti
- zap

## Targets

- Acme Support Portal — `http://127.0.0.1:27000/`
- Nova DevOps Console — `http://127.0.0.1:27100/`

## Output สำคัญ

- `datasets/tools-name-date/<tool>-{DATE}/<lab>/raw/` — output ดิบจาก tool
- `datasets/tools-name-date/<tool>-{DATE}/<lab>/normalized/` — JSONL ที่ normalize แล้ว
- `records/all-records.jsonl` — รวม normalized records ทั้งหมด
- `derived/active_scan_summary.csv` — สรุปจำนวน finding ต่อ tool/target
- `derived/active_target_features.csv` — feature table สำหรับต่อเข้า Exploit-DL
- `manifests/index.json` — manifest ของ dataset

## Summary

- Tool-target runs: {len(summary_rows)}
- Normalized records: {len(all_rows)}
- Scanner findings: {sum(row['finding_count'] for row in summary_rows)}

หมายเหตุ: Nuclei ในรอบนี้ใช้ template scope เบาและอาจไม่มี match ซึ่งยังเป็นข้อมูลเชิงลบที่ใช้เป็น feature ได้
""",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

