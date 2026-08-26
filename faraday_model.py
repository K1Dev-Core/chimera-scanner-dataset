from __future__ import annotations

# Faraday-like workspace normalization + machine-consumable report for MCP/AI.
# Builds: hosts -> services -> vulnerabilities, plus an attack_order that ranks
# CONFIRMED findings (evidence-driven) above speculative model candidates.

_SEV_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
_SEV_W = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.35, "info": 0.1}

# A believable test action per ranked family, so an AI agent can act on the report.
_FAMILY_PROBE = {
    "redis": "redis-cli -h {host} -p {port} info server",
    "couchdb": "curl -s {url}/_all_dbs",
    "elasticsearch": "curl -s {url}/_cat/indices",
    "adminer": "curl -s -o /dev/null -w '%{{http_code}}' {url}/",
    "jenkins": "curl -s -o /dev/null -w '%{{http_code}}' {url}/login",
    "grafana": "curl -s -o /dev/null -w '%{{http_code}}' {url}/login",
    "tomcat": "curl -s -o /dev/null -w '%{{http_code}}' {url}/manager/html",
    "spring": "curl -s {url}/env",
}


def _sev(text: str) -> str:
    t = (text or "").lower()
    for s in ("critical", "high", "medium", "low"):
        if s in t:
            return s
    return "info"


def _cve(text: str) -> str:
    import re

    m = re.search(r"CVE-\d{4}-\d{4,7}", text or "")
    return m.group(0) if m else ""


def _template_id(finding: str) -> str:
    return finding.split("]")[0].strip("[") if finding and "]" in finding else finding


def _compose_action(vuln: dict, target: dict) -> dict:
    url = target.get("url", "")
    host = target.get("target_id", "")
    port = target.get("port", "")
    cve = vuln.get("cve")
    status = vuln.get("status", "")
    payload = ""
    method = "verify"
    if status == "Confirmed" and vuln.get("tool") == "nuclei" and cve:
        method = "nuclei_rerun"
        payload = f"nuclei -u {url} -t {cve}"
    elif status == "Confirmed" and vuln.get("tool") == "nikto":
        method = "review"
        payload = f"nikto -h {url} -nointeractive"
    elif status == "Ranked":
        method = "probe"
        fam = vuln.get("name", "")
        tpl = _FAMILY_PROBE.get(fam, "curl -s -o /dev/null -w '%{{http_code}}' {url}/")
        payload = tpl.format(url=url, host=host or "127.0.0.1", port=port or 80)
    return {"method": method, "command": payload, "status": status, "cve": cve}

def _nuclei_desc(finding: str, sev: str, cve: str) -> str:
    body = "Nuclei matched a template on the target."
    if cve:
        body += f" Associated CVE: {cve}."
    body += f" Classified severity: {sev}."
    return body


def normalize_target(target: dict) -> dict:
    host_id = target.get("target_id") or "unknown"
    port = target.get("port")
    url = target.get("url", "")
    host = {
        "id": host_id, "name": host_id, "ip": host_id, "url": url,
        "title": target.get("title", ""), "http_status": target.get("http_status", ""),
        "server": target.get("server", ""), "x_powered_by": target.get("x_powered_by", ""),
        "os": "", "services": [], "resources": [],
    }
    services = []
    if port:
        services.append({
            "name": host_id, "port": port,
            "protocol": str(target.get("protocol_kind", "http") or "http").upper(),
            "status": "open", "banner": target.get("nmap_service_line", ""), "source": "nmap",
        })
    host["services"] = services

    vulnerabilities = []
    rank_source = {}

    for finding in target.get("nuclei_findings", []):
        sev = _sev(finding); cve = _cve(finding); tid = _template_id(finding)
        vulnerabilities.append({
            "id": f"{host_id}:{tid}", "name": tid or "nuclei match", "severity": sev,
            "status": "Confirmed", "tool": "nuclei", "cve": cve, "port": port,
            "desc": _nuclei_desc(finding, sev, cve),
            "references": [cve] if cve else [], "evidence": finding,
            "solution": "Review the detection and apply the vendor patch / disable the vulnerable component.",
        })
        # Evidence signal: any confirmed nuclei/Nikto finding boosts confidence of ranked families
        # whose name/aliases appear in the finding text.
        cfg = (finding or "").lower()
        for fam in target.get("ranking", []):
            if fam["family"] in cfg:
                rank_source[fam["family"]] = max(rank_source.get(fam["family"], 0), _SEV_W[sev])

    for line in target.get("tool_summary", {}).get("nikto", []):
        sev = "medium" if _sev(line) == "info" else _sev(line); cve = _cve(line)
        vulnerabilities.append({
            "id": f"{host_id}:nikto:{str(line)[:40]}", "name": str(line).strip()[:120] or "nikto finding",
            "severity": sev, "status": "Reported", "tool": "nikto", "cve": cve, "port": port,
            "desc": "Nikto reported a potential issue against the HTTP server.",
            "references": [cve] if cve else [],
            "solution": "Confirm against the documented Nikto/OSVDB advisory and remediate.",
            "evidence": line,
        })

    if target.get("title") or target.get("server"):
        vulnerabilities.append({
            "id": f"{host_id}:http-info",
            "name": (target.get("title") or target.get("server") or "HTTP service")[:90],
            "severity": "info", "status": "Open", "tool": "probe", "cve": "", "port": port,
            "desc": "HTTP service fingerprint from a passive probe.", "references": [],
            "solution": "", "evidence": f"Server: {target.get('server','')} | Title: {target.get('title','')}",
        })

    # Build attack_order candidates from the family ranker, fusing evidence signal.
    ranked_rows = []
    for row in target.get("ranking", []):
        prob = float(row.get("probability", row.get("confidence", 0)) or 0)
        conf = rank_source.get(row["family"], 0.0)
        fused = min(1.0, prob * 0.6 + conf * 0.8)
        if fused < 0.05:
            continue
        fam = row["family"]
        v = {
            "id": f"{host_id}:rank:{fam}", "name": fam, "severity": "info" if conf == 0 else "medium",
            "status": "Ranked", "tool": "model", "cve": "", "port": port,
            "desc": f"Model-probability candidate '{fam}' (p={prob:.2f}, evidence={conf:.2f}).",
            "references": [], "solution": "Investigate the inferred component for known CVEs.",
            "evidence": f"p={prob:.3f}; evidence_signal={conf:.2f}", "fused_confidence": round(fused, 4),
        }
        rank_source.setdefault(fam, 0.0)
        vulnerabilities.append(v)
        ranked_rows.append((fam, fused))

    # Confirmed findings carry a confidence based on severity; rankers derived from model get fused confidence.
    def confidence(v):
        if v["status"] in ("Confirmed", "Reported"):
            return _SEV_W.get(v["severity"], 0.2)
        return v.get("fused_confidence", 0.1)

    # attack_order := all vulnerabilities, evidence-driven worst-first, with an executable action.
    attack_order = []
    for v in vulnerabilities:
        a = _compose_action(v, target)
        attack_order.append({
            "rank": 0,
            "family": v["name"] if v["tool"] == "model" else (v["cve"] or v["tool"]),
            "severity": v["severity"],
            "status": v["status"],
            "confidence": round(confidence(v), 4),
            "source_tool": v["tool"],
            "cve": v.get("cve", ""),
            "evidence": v.get("evidence", ""),
            "method": a["method"], "command": a["command"],
            "why": v["desc"],
        })
    # sort: confirmed/reported first, then by severity desc, then confidence desc, then name.
    def rank_key(x):
        prio = {"Confirmed": 0, "Reported": 1, "Open": 2, "Ranked": 3}[x["status"]]
        return (prio, -_SEV_ORDER.get(x["severity"], 0), -x["confidence"])
    attack_order.sort(key=rank_key)
    for i, a in enumerate(attack_order, 1):
        a["rank"] = i

    vulnerabilities.sort(key=lambda v: (-_SEV_ORDER.get(v["severity"], 0), v["status"] != "Confirmed"))

    summary = {
        "hosts": 1, "services": len(services), "vulnerabilities": len(vulnerabilities),
        "by_severity": {s: sum(1 for v in vulnerabilities if v["severity"] == s) for s in _SEV_ORDER},
        "open": sum(1 for v in vulnerabilities if v["status"] in ("Open", "Reported", "Confirmed")),
        "confirmed": sum(1 for v in vulnerabilities if v["status"] == "Confirmed"),
    }

    return {
        "schema_version": "1.0",
        "target": host,
        "services": services,
        "vulnerabilities": vulnerabilities,
        "attack_order": attack_order,
        "workflow": [
            {"step": "Discover", "detail": f"{len(services)} service(s)"},
            {"step": "Probe", "detail": f"HTTP {host['http_status']} | {host['server']}"},
            {"step": "Scan", "detail": f"{len(vulnerabilities)} issue(s) reported"},
            {"step": "Rank", "detail": f"{len(attack_order)} step(s) queued"},
        ],
        "summary": summary,
    }
