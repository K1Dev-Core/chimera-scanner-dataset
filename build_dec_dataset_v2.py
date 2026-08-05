#!/usr/bin/env python3
"""Build a leakage-aware v2 dataset from the Dec scanner collection.

The source dataset is read-only. The destination is created from scratch and
contains compact, true JSONL records. Raw HTTP request/response bodies are not
copied; their SHA-256 hashes preserve evidence identity without duplicating
payloads or secrets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


SCHEMA_VERSION = "2.0.0"
RUN_DATE = "2026-08-04"

TARGETS: dict[str, dict[str, Any]] = {
    "apache_41773": {
        "cve": "CVE-2021-41773",
        "product": "Apache HTTP Server",
        "vulnerability_family": "path-traversal",
    },
    "django_34265": {
        "cve": "CVE-2022-34265",
        "product": "Django",
        "vulnerability_family": "sql-injection",
    },
    "druid_25646": {
        "cve": "CVE-2021-25646",
        "product": "Apache Druid",
        "vulnerability_family": "command-injection",
    },
    "elfinder_32682": {
        "cve": "CVE-2021-32682",
        "product": "elFinder",
        "vulnerability_family": "command-injection",
    },
    "glassfish_1000028": {
        "cve": "CVE-2017-1000028",
        "product": "GlassFish",
        "vulnerability_family": "path-traversal",
    },
    "gogs_18925": {
        "cve": "CVE-2018-18925",
        "product": "Gogs",
        "vulnerability_family": "path-traversal",
    },
    "jackson_7525": {
        "cve": "CVE-2017-7525",
        "product": "Jackson Databind",
        "vulnerability_family": "unsafe-deserialization",
    },
    "spring_22965": {
        "cve": "CVE-2022-22965",
        "product": "Spring Framework",
        "vulnerability_family": "command-injection",
    },
    "struts2_s2045": {
        "cve": "CVE-2017-5638",
        "product": "Apache Struts 2",
        "vulnerability_family": "command-injection",
    },
    "tomcat_12615": {
        "cve": "CVE-2017-12615",
        "product": "Apache Tomcat",
        "vulnerability_family": "unrestricted-file-upload",
    },
}

CANDIDATE_FAMILIES = sorted(
    {
        "command-injection",
        "path-traversal",
        "sql-injection",
        "unsafe-deserialization",
        "unrestricted-file-upload",
        "cross-site-scripting",
        "server-side-request-forgery",
        "authentication-bypass",
    }
)

FAMILY_KEYWORDS = {
    "command-injection": ("rce", "remote code", "command", "code execution", "ognl"),
    "path-traversal": ("traversal", "file inclusion", "arbitrary file", "file read", "lfi"),
    "sql-injection": ("sql", "sqli", "database injection"),
    "unsafe-deserialization": ("deserial", "jackson", "object injection"),
    "unrestricted-file-upload": ("file upload", "upload", "put method"),
    "cross-site-scripting": ("cross-site scripting", "xss"),
    "server-side-request-forgery": ("server-side request forgery", "ssrf"),
    "authentication-bypass": ("auth bypass", "authentication bypass", "unauthenticated"),
}


def sha256_text(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def stable_id(*parts: Any) -> str:
    joined = "\x1f".join("" if p is None else str(p) for p in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:24]


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def jsonl_objects(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                value["_line_number"] = line_number
                yield value


def common(record_type: str, target_id: str, tool: str, source: Path, root: Path, discriminator: Any) -> dict[str, Any]:
    source_path = rel(source, root)
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": f"dec-{RUN_DATE}",
        "record_id": stable_id(record_type, target_id, tool, source_path, discriminator),
        "dataset_record_type": record_type,
        "target_id": target_id,
        "tool": tool,
        "observed_at": None,
        "source_path": source_path,
        "parser_status": "parsed",
    }


def target_from_path(path: Path) -> str | None:
    for part in path.parts:
        if part in TARGETS:
            return part
    return None


def parse_httpx(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted((root / "raw" / "httpx-toolkit").glob("*/*/scan.jsonl")):
        target_id = target_from_path(path)
        if not target_id:
            continue
        for item in jsonl_objects(path):
            rec = common("web_observation", target_id, "httpx-toolkit", path, root, item.get("_line_number"))
            rec.update(
                {
                    "observed_at": item.get("timestamp"),
                    "url": item.get("url"),
                    "host": item.get("host_ip") or item.get("host"),
                    "port": int(item["port"]) if str(item.get("port", "")).isdigit() else None,
                    "scheme": item.get("scheme"),
                    "status_code": item.get("status_code"),
                    "title": item.get("title"),
                    "server": item.get("webserver"),
                    "technologies": item.get("tech") or [],
                    "cpe": item.get("cpe") or [],
                    "content_length": item.get("content_length"),
                    "confidence": "observed",
                }
            )
            records.append(rec)
    return records


def parse_naabu(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted((root / "raw" / "naabu").glob("*/*/scan.jsonl")):
        target_id = target_from_path(path)
        if not target_id:
            continue
        for item in jsonl_objects(path):
            rec = common("port_observation", target_id, "naabu", path, root, item.get("_line_number"))
            rec.update(
                {
                    "observed_at": item.get("timestamp"),
                    "host": item.get("ip"),
                    "port": item.get("port"),
                    "protocol": item.get("protocol"),
                    "tls": item.get("tls"),
                    "state": "open",
                    "confidence": "observed",
                }
            )
            records.append(rec)
    return records


def parse_nmap(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted((root / "raw" / "nmap").glob("*/*/scan.xml")):
        target_id = target_from_path(path)
        if not target_id:
            continue
        try:
            tree = ET.parse(path)
        except ET.ParseError:
            continue
        for host_index, host_node in enumerate(tree.findall("host")):
            address = host_node.find("address")
            host = address.get("addr") if address is not None else None
            for port_node in host_node.findall("./ports/port"):
                state_node = port_node.find("state")
                service_node = port_node.find("service")
                state = state_node.get("state") if state_node is not None else None
                service = dict(service_node.attrib) if service_node is not None else {}
                port = int(port_node.get("portid", "0"))
                rec = common("service_observation", target_id, "nmap", path, root, f"{host_index}:{port_node.get('protocol')}:{port}")
                rec.update(
                    {
                        "host": host,
                        "port": port,
                        "protocol": port_node.get("protocol"),
                        "state": state,
                        "service": service.get("name"),
                        "product": service.get("product"),
                        "version": service.get("version"),
                        "extra_info": service.get("extrainfo"),
                        "cpe": [node.text for node in port_node.findall("./service/cpe") if node.text],
                        "confidence": "observed",
                    }
                )
                records.append(rec)
    return records


def parse_nuclei(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted((root / "raw" / "nuclei").glob("*/*/scan.jsonl")):
        target_id = target_from_path(path)
        if not target_id:
            continue
        for item in jsonl_objects(path):
            info = item.get("info") or {}
            classification = info.get("classification") or {}
            cves = classification.get("cve-id") or []
            cwes = classification.get("cwe-id") or []
            if isinstance(cves, str):
                cves = [cves]
            if isinstance(cwes, str):
                cwes = [cwes]
            rec = common("scanner_finding", target_id, "nuclei", path, root, item.get("_line_number"))
            rec.update(
                {
                    "observed_at": item.get("timestamp"),
                    "finding_id": stable_id(target_id, "nuclei", item.get("template-id"), item.get("matched-at"), item.get("matcher-name")),
                    "title": info.get("name"),
                    "category": item.get("type"),
                    "severity": str(info.get("severity") or "unknown").lower(),
                    "template_id": item.get("template-id"),
                    "matcher_name": item.get("matcher-name"),
                    "url": item.get("url"),
                    "matched_at": item.get("matched-at"),
                    "host": item.get("ip") or item.get("host"),
                    "port": int(item["port"]) if str(item.get("port", "")).isdigit() else None,
                    "cve": [str(v).upper() for v in cves],
                    "cwe": [str(v).upper() for v in cwes],
                    "cvss_score": classification.get("cvss-score"),
                    "cvss_metrics": classification.get("cvss-metrics"),
                    "tags": info.get("tags") or [],
                    "references": info.get("reference") or [],
                    "description": info.get("description"),
                    "remediation": info.get("remediation"),
                    "matcher_status": item.get("matcher-status"),
                    "interaction_observed": bool(item.get("interaction")),
                    "request_sha256": sha256_text(item.get("request")),
                    "response_sha256": sha256_text(item.get("response")),
                    "evidence_level": "scanner-match",
                    "confidence": "tool-reported",
                }
            )
            records.append(rec)
    return records


def flatten_wapiti_groups(document: dict[str, Any]) -> Iterable[tuple[str, str, dict[str, Any]]]:
    for section in ("vulnerabilities", "anomalies", "additionals"):
        groups = document.get(section) or {}
        if not isinstance(groups, dict):
            continue
        for category, findings in groups.items():
            if isinstance(findings, dict):
                findings = [findings]
            if not isinstance(findings, list):
                continue
            for finding in findings:
                if isinstance(finding, dict):
                    yield section, category, finding


def parse_wapiti(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted((root / "raw" / "wapiti").glob("*/*/scan.json")):
        target_id = target_from_path(path)
        if not target_id:
            continue
        try:
            document = json.loads(read_text(path))
        except json.JSONDecodeError:
            continue
        for index, (section, category, item) in enumerate(flatten_wapiti_groups(document)):
            rec = common("scanner_finding", target_id, "wapiti", path, root, index)
            rec.update(
                {
                    "finding_id": stable_id(target_id, "wapiti", category, item.get("path"), item.get("parameter"), index),
                    "title": category,
                    "category": section,
                    "severity": str(item.get("level") or "unknown").lower(),
                    "url": item.get("path"),
                    "method": item.get("method"),
                    "parameter": item.get("parameter"),
                    "module": item.get("module"),
                    "description": item.get("info"),
                    "wstg": item.get("wstg") or [],
                    "request_sha256": sha256_text(item.get("http_request")),
                    "evidence_level": "scanner-match",
                    "confidence": "tool-reported",
                }
            )
            records.append(rec)
    return records


NIKTO_FINDING = re.compile(r"^\+ \[([^]]+)\]\s*(.*)$")


def parse_nikto(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted((root / "raw" / "nikto").glob("*/*/scan.txt")):
        target_id = target_from_path(path)
        if not target_id:
            continue
        for line_number, line in enumerate(read_text(path).splitlines(), 1):
            match = NIKTO_FINDING.match(line)
            if not match:
                continue
            plugin_id, message = match.groups()
            url_match = re.search(r"See:\s*(https?://\S+)", message)
            path_match = re.match(r"([^:]+):\s*(.*)", message)
            rec = common("scanner_finding", target_id, "nikto", path, root, line_number)
            rec.update(
                {
                    "finding_id": stable_id(target_id, "nikto", plugin_id, message),
                    "title": (path_match.group(2) if path_match else message).strip(),
                    "category": "web-server-check",
                    "severity": "unknown",
                    "plugin_id": plugin_id,
                    "path": path_match.group(1).strip() if path_match else None,
                    "reference": url_match.group(1).rstrip(".") if url_match else None,
                    "evidence_level": "scanner-match",
                    "confidence": "tool-reported",
                }
            )
            records.append(rec)
    return records


def parse_scan_summaries(root: Path) -> list[dict[str, Any]]:
    records = []
    for tool in ("zaproxy", "autorecon"):
        tool_root = root / "raw" / tool
        for target_id in TARGETS:
            candidates = list(tool_root.glob(f"*/{target_id}/**/*"))
            files = [p for p in candidates if p.is_file()]
            if not files:
                continue
            source = files[0]
            rec = common("scan_summary", target_id, tool, source, root, "summary")
            rec.update(
                {
                    "source_file_count": len(files),
                    "source_bytes": sum(p.stat().st_size for p in files),
                    "finding_count_parsed": 0,
                    "parser_status": "raw-retained-no-structured-findings",
                    "confidence": "coverage-only",
                }
            )
            records.append(rec)
    return records


def metasploit_verdict(text: str) -> dict[str, Any]:
    lower = text.lower()
    module_matches = re.findall(r"(?:use|exploit/)\s*(exploit/[\w/]+)", text, re.IGNORECASE)
    module = module_matches[-1] if module_matches else None
    check_vulnerable = None
    if "the target is vulnerable" in lower or "appears to be vulnerable" in lower:
        check_vulnerable = True
    if "not vulnerable" in lower or "not exploitable" in lower:
        check_vulnerable = False
    session_opened = bool(re.search(r"(?:meterpreter|command shell) session \d+ opened", lower))
    code_execution_observed = "successfully executed the injected code" in lower
    exploit_attempted = any(token in lower for token in ("exploit completed", "run -j", "run\n", "exploit\n"))
    exploit_success = session_opened or code_execution_observed
    if exploit_success:
        verdict = "verified"
    elif check_vulnerable is True:
        verdict = "detected"
    elif check_vulnerable is False:
        verdict = "not-detected"
    else:
        verdict = "inconclusive"
    return {
        "module": module,
        "check_vulnerable": check_vulnerable,
        "exploit_attempted": exploit_attempted,
        "session_opened": session_opened,
        "code_execution_observed": code_execution_observed,
        "exploit_success_observed": exploit_success,
        "verdict": verdict,
    }


def parse_metasploit(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted((root / "raw" / "metasploit").glob("*/*/scan.txt")):
        target_id = target_from_path(path)
        if not target_id:
            continue
        text = read_text(path)
        rec = common("validation_result", target_id, "metasploit", path, root, "final")
        rec.update(metasploit_verdict(text))
        rec.update({"evidence_sha256": sha256_text(text), "confidence": "validation-output"})
        records.append(rec)
    return records


def parse_sqlmap(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted((root / "raw" / "sqlmap").glob("*/*/scan.txt")):
        target_id = target_from_path(path)
        if not target_id:
            continue
        text = read_text(path)
        lower = text.lower()
        confirmed = "is vulnerable" in lower and "does not appear to be injectable" not in lower
        false_or_unexploitable = "false positive or unexploitable" in lower
        not_injectable = "does not appear to be injectable" in lower or "all tested parameters do not appear to be injectable" in lower
        verdict = "verified" if confirmed else "not-detected" if not_injectable else "inconclusive"
        rec = common("validation_result", target_id, "sqlmap", path, root, "final")
        rec.update(
            {
                "parameter_injection_confirmed": confirmed,
                "false_positive_or_unexploitable": false_or_unexploitable,
                "verdict": verdict,
                "evidence_sha256": sha256_text(text),
                "confidence": "validation-output",
            }
        )
        records.append(rec)
    return records


def build_targets(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    urls: dict[str, str] = {}
    hosts: dict[str, str] = {}
    ports: dict[str, int] = {}
    for item in observations:
        target_id = item["target_id"]
        if item.get("url"):
            urls[target_id] = item["url"]
        if item.get("host"):
            hosts[target_id] = item["host"]
        if item.get("port"):
            ports[target_id] = item["port"]
    records = []
    for target_id, truth in TARGETS.items():
        records.append(
            {
                "schema_version": SCHEMA_VERSION,
                "record_id": stable_id("target", target_id),
                "dataset_record_type": "target_ground_truth",
                "target_id": target_id,
                "lab_source": "Vulhub",
                "target_url": urls.get(target_id),
                "host": hosts.get(target_id),
                "port": ports.get(target_id),
                "ground_truth_cve": truth["cve"],
                "ground_truth_product": truth["product"],
                "ground_truth_family": truth["vulnerability_family"],
                "ground_truth_source": "Vulhub lab selection",
                "exploit_success_observed": None,
                "model_feature_policy": "exclude-ground-truth-fields",
            }
        )
    return records


def severity_bucket(value: Any) -> str:
    value = str(value or "unknown").lower()
    return value if value in {"critical", "high", "medium", "low", "info"} else "unknown"


def build_target_features(observations: list[dict[str, Any]], findings: list[dict[str, Any]], validations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_target_obs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_target_findings: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_target_validations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in observations:
        by_target_obs[item["target_id"]].append(item)
    for item in findings:
        by_target_findings[item["target_id"]].append(item)
    for item in validations:
        by_target_validations[item["target_id"]].append(item)

    rows = []
    for target_id in TARGETS:
        obs = by_target_obs[target_id]
        fnd = by_target_findings[target_id]
        val = by_target_validations[target_id]
        severities = Counter(severity_bucket(item.get("severity")) for item in fnd)
        technologies = sorted({str(t) for item in obs for t in item.get("technologies", [])})
        open_ports = sorted({item.get("port") for item in obs if item.get("state") == "open" and item.get("port") is not None})
        tools = sorted({item.get("tool") for item in obs + fnd + val if item.get("tool")})
        cve_findings = sum(1 for item in fnd if item.get("cve"))
        generic_hardening = sum(
            1
            for item in fnd
            if any(token in str(item.get("title", "")).lower() for token in ("missing security header", "cookie", "clickjacking", "mime"))
        )
        rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "record_id": stable_id("target-features", target_id),
                "dataset_record_type": "target_feature_row",
                "target_id": target_id,
                "open_tcp_port_count": len(open_ports),
                "http_observation_count": sum(1 for item in obs if item["dataset_record_type"] == "web_observation"),
                "service_observation_count": sum(1 for item in obs if item["dataset_record_type"] == "service_observation"),
                "unique_technology_count": len(technologies),
                "scanner_finding_count": len(fnd),
                "critical_count": severities["critical"],
                "high_count": severities["high"],
                "medium_count": severities["medium"],
                "low_count": severities["low"],
                "info_count": severities["info"],
                "unknown_severity_count": severities["unknown"],
                "cve_finding_count": cve_findings,
                "generic_hardening_finding_count": generic_hardening,
                "evidence_tool_count": len(tools),
                "validation_verified_count": sum(1 for item in val if item.get("verdict") == "verified"),
                "validation_detected_count": sum(1 for item in val if item.get("verdict") == "detected"),
                "validation_not_detected_count": sum(1 for item in val if item.get("verdict") == "not-detected"),
                "validation_inconclusive_count": sum(1 for item in val if item.get("verdict") == "inconclusive"),
                "open_ports": open_ports,
                "observed_technologies": technologies,
                "feature_note": "Ground-truth CVE/product/family intentionally excluded.",
            }
        )
    return rows


def family_evidence(findings: list[dict[str, Any]], family: str) -> int:
    keywords = FAMILY_KEYWORDS[family]
    count = 0
    for item in findings:
        haystack = " ".join(
            str(item.get(key) or "")
            for key in ("title", "category", "description", "template_id", "matcher_name", "tags")
        ).lower()
        if any(keyword in haystack for keyword in keywords):
            count += 1
    return count


def build_candidate_rows(target_features: list[dict[str, Any]], findings: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    findings_by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in findings:
        findings_by_target[item["target_id"]].append(item)
    feature_rows = []
    labels = []
    for target_row in target_features:
        target_id = target_row["target_id"]
        base = {k: v for k, v in target_row.items() if k not in {"record_id", "dataset_record_type", "feature_note"}}
        for family in CANDIDATE_FAMILIES:
            candidate_id = stable_id("candidate", target_id, family)
            row = {
                **base,
                "record_id": candidate_id,
                "dataset_record_type": "target_candidate_feature_row",
                "candidate_family": family,
                "candidate_family_evidence_count": family_evidence(findings_by_target[target_id], family),
                "feature_note": "Do not join labels before train/test splitting by target or product group.",
            }
            feature_rows.append(row)
            labels.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "record_id": stable_id("candidate-label", target_id, family),
                    "dataset_record_type": "target_candidate_label",
                    "target_id": target_id,
                    "candidate_record_id": candidate_id,
                    "candidate_family": family,
                    "is_ground_truth_family": int(family == TARGETS[target_id]["vulnerability_family"]),
                    "label_source": "Vulhub lab ground truth",
                    "exploit_success_observed": None,
                }
            )
    return feature_rows, labels


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> int:
    materialized = list(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for item in materialized:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    return len(materialized)


def checksums(destination: Path) -> None:
    rows = []
    for path in sorted(p for p in destination.rglob("*") if p.is_file() and p.name != "checksums.sha256"):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {path.relative_to(destination).as_posix()}")
    (destination / "checksums.sha256").write_text("\n".join(rows) + "\n", encoding="ascii")


def validate_jsonl(destination: Path) -> dict[str, Any]:
    report: dict[str, Any] = {"files": {}, "valid": True}
    for path in sorted(destination.rglob("*.jsonl")):
        line_count = 0
        invalid_lines = []
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                line_count += 1
                try:
                    value = json.loads(line)
                    if not isinstance(value, dict):
                        invalid_lines.append(line_number)
                except json.JSONDecodeError:
                    invalid_lines.append(line_number)
        report["files"][path.relative_to(destination).as_posix()] = {
            "records": line_count,
            "invalid_lines": invalid_lines,
        }
        if invalid_lines:
            report["valid"] = False
    return report


def build(source: Path, destination: Path) -> dict[str, Any]:
    if not (source / "raw").is_dir():
        raise SystemExit(f"Source does not contain raw/: {source}")
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    observations = parse_httpx(source) + parse_naabu(source) + parse_nmap(source) + parse_scan_summaries(source)
    findings = parse_nuclei(source) + parse_wapiti(source) + parse_nikto(source)
    validations = parse_metasploit(source) + parse_sqlmap(source)
    targets = build_targets(observations)
    target_features = build_target_features(observations, findings, validations)
    candidate_features, labels = build_candidate_rows(target_features, findings)
    all_records = targets + observations + findings + validations

    counts = {
        "targets": write_jsonl(destination / "records" / "targets.jsonl", targets),
        "observations": write_jsonl(destination / "records" / "observations.jsonl", observations),
        "findings": write_jsonl(destination / "records" / "findings.jsonl", findings),
        "validations": write_jsonl(destination / "records" / "validations.jsonl", validations),
        "all_records": write_jsonl(destination / "records" / "all-records.jsonl", all_records),
        "target_features": write_jsonl(destination / "derived" / "target-features.jsonl", target_features),
        "candidate_features": write_jsonl(destination / "derived" / "target-candidate-features.jsonl", candidate_features),
        "candidate_labels": write_jsonl(destination / "labels" / "target-candidate-labels.jsonl", labels),
    }

    missing_tools = []
    for tool in ("openvas",):
        tool_root = source / "raw" / tool
        if not tool_root.exists() or not any(p.is_file() for p in tool_root.rglob("*")):
            missing_tools.append(tool)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "name": "chimera-scanner-dataset-dec-v2",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "source_policy": "read-only; raw files are referenced, not copied",
        "run_date": RUN_DATE,
        "counts": counts,
        "tools_with_structured_parsers": ["httpx-toolkit", "naabu", "nmap", "nuclei", "wapiti", "nikto", "metasploit", "sqlmap"],
        "tools_with_coverage_summaries_only": ["autorecon", "zaproxy"],
        "missing_tool_outputs": missing_tools,
        "label_policy": {
            "ground_truth_is_separate": True,
            "exploit_success_defaults_to_null": True,
            "no_rank_score_feature": True,
            "required_split_group": "target_id or product-family group",
        },
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    quality = validate_jsonl(destination)
    quality["warnings"] = [
        "OpenVAS output is absent in the source dataset.",
        "ZAP raw text contains no structured alerts; only scan coverage is recorded.",
        "AutoRecon is retained as a coverage summary because its output is a multi-file report tree.",
        "Only 10 vulnerable targets are present; this is a pipeline dataset, not a reliable model benchmark.",
        "Candidate labels represent Vulhub ground truth family, not observed exploit success.",
    ]
    (destination / "quality-report.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checksums(destination)
    return {"destination": str(destination), "counts": counts, "quality": quality}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Path to the original Dec dataset")
    parser.add_argument("destination", type=Path, help="New v2 output directory")
    args = parser.parse_args()
    result = build(args.source.resolve(), args.destination.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
