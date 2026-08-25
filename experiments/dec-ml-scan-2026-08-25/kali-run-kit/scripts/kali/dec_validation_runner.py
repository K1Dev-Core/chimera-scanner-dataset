#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shutil
import socket
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


HTTP_ALIASES = {
    "grafana": ["grafana"],
    "goahead": ["goahead", "goahead-webs"],
    "joomla": ["joomla", "com_config", "api/index.php"],
    "nginx": ["nginx"],
    "shiro": ["shiro", "rememberme", "jsecurity"],
    "spring": ["spring", "actuator", "tomcat"],
    "tomcat": ["tomcat", "apache-coyote", "catalina"],
}
NONHTTP_ALIASES = {
    "aria2": ["aria2"],
    "redis": ["redis", "redis_version"],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="replace")


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run_command(args: list[str], output: Path, timeout: int = 60) -> tuple[bool, str]:
    if not command_exists(args[0]):
        write_text(output, f"SKIPPED: command not found: {args[0]}\n")
        return False, "missing"
    try:
        proc = subprocess.run(args, text=True, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        write_text(output, (exc.stdout or "") + (exc.stderr or "") + "\nTIMEOUT\n")
        return False, "timeout"
    write_text(output, proc.stdout + proc.stderr)
    return proc.returncode == 0, f"exit={proc.returncode}"


def http_get(url: str, output: Path, timeout: int = 10) -> tuple[bool, str]:
    req = Request(url, headers={"User-Agent": "chimera-dec-validation/1.0"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            headers = "".join(f"{k}: {v}\n" for k, v in resp.headers.items())
            body = resp.read(200000).decode("utf-8", errors="replace")
            write_text(output, f"STATUS: {resp.status}\n{headers}\n{body}")
            return True, f"http={resp.status}"
    except Exception as exc:  # noqa: BLE001 - runner must keep collecting evidence
        write_text(output, f"ERROR: {type(exc).__name__}: {exc}\n")
        return False, "error"


def tcp_probe(host: str, port: int, payload: bytes, output: Path, timeout: int = 5) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.sendall(payload)
            data = sock.recv(4096)
    except Exception as exc:  # noqa: BLE001
        write_text(output, f"ERROR: {type(exc).__name__}: {exc}\n")
        return False, "error"
    write_text(output, data.decode("utf-8", errors="replace"))
    return True, "tcp_response"


def find_feature(features: list[dict[str, str]], target_id: str) -> dict[str, str] | None:
    for row in features:
        if row.get("target_id") == target_id:
            return row
    return None


def evidence_text(files: list[Path]) -> str:
    chunks = []
    for path in files:
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8", errors="replace").lower())
    return "\n".join(chunks)


def classify(weak_label: str, text: str, safe_poc_used: bool, evidence_count: int) -> tuple[str, str, str]:
    aliases = HTTP_ALIASES.get(weak_label, []) + NONHTTP_ALIASES.get(weak_label, [])
    if any(alias.lower() in text for alias in aliases):
        confidence = "high" if safe_poc_used else "medium"
        return "validated_positive", confidence, f"พบ fingerprint/probe ที่ตรงกับ family `{weak_label}`"
    if evidence_count:
        return "inconclusive", "low", f"มีหลักฐานจาก scanner แล้ว แต่ยังไม่พอ confirm family `{weak_label}`"
    return "not_run", "none", "ยังไม่มี service หรือ evidence ที่อ่านได้"


def scan_target(row: dict[str, str], feature: dict[str, str] | None, out_dir: Path) -> dict:
    target_id = row["target_id"]
    weak_label = row.get("weak_label", "")
    target_dir = out_dir / "raw-curated" / target_id
    raw_dir = target_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    url = (feature or {}).get("url", "")
    port_text = (feature or {}).get("port", "")
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    port = int(port_text or parsed.port or (443 if parsed.scheme == "https" else 80))
    evidence_files: list[Path] = []
    tools_used: list[str] = []
    safe_poc_used = False

    nmap_out = raw_dir / "nmap.stdout"
    ok, _ = run_command(["nmap", "-sV", "-Pn", "-p", str(port), host], nmap_out, timeout=90)
    if ok or nmap_out.exists():
        evidence_files.append(nmap_out)
        tools_used.append("nmap")

    if parsed.scheme in {"http", "https"}:
        curl_out = raw_dir / "curl_home.txt"
        if command_exists("curl"):
            ok, _ = run_command(["curl", "-k", "-i", "-L", "--max-time", "10", url], curl_out, timeout=20)
        else:
            ok, _ = http_get(url, curl_out)
        if ok or curl_out.exists():
            evidence_files.append(curl_out)
            tools_used.append("curl")

        probe_urls = []
        if weak_label == "joomla":
            probe_urls.append(url.rstrip("/") + "/api/index.php/v1/config/application?public=true")
        elif weak_label == "grafana":
            probe_urls.append(url.rstrip("/") + "/login")
        elif weak_label == "spring":
            probe_urls.append(url.rstrip("/") + "/actuator")
        elif weak_label == "tomcat":
            probe_urls.append(url.rstrip("/") + "/docs/")
        elif weak_label == "nginx":
            probe_urls.append(url.rstrip("/") + "/")
        elif weak_label in {"goahead", "shiro"}:
            probe_urls.append(url.rstrip("/") + "/")
        for index, probe_url in enumerate(probe_urls, start=1):
            probe_out = raw_dir / f"safe_probe_{index}.txt"
            ok, _ = http_get(probe_url, probe_out)
            if ok or probe_out.exists():
                evidence_files.append(probe_out)
                tools_used.append("safe-http-probe")
                safe_poc_used = True

        if command_exists("nikto"):
            nikto_out = raw_dir / "nikto.stdout"
            run_command(["nikto", "-nointeractive", "-ask", "no", "-Tuning", "b", "-host", url], nikto_out, timeout=120)
            if nikto_out.exists():
                evidence_files.append(nikto_out)
                tools_used.append("nikto")
    elif weak_label == "redis":
        redis_out = raw_dir / "redis_info.txt"
        tcp_probe(host, port, b"INFO\r\n", redis_out)
        evidence_files.append(redis_out)
        tools_used.append("tcp-info")
        safe_poc_used = True
    elif weak_label == "aria2":
        aria_out = raw_dir / "aria2_get_version.txt"
        payload = b'{"jsonrpc":"2.0","id":"dec","method":"aria2.getVersion"}\n'
        tcp_probe(host, port, payload, aria_out)
        evidence_files.append(aria_out)
        tools_used.append("tcp-jsonrpc-version")
        safe_poc_used = True

    text = evidence_text(evidence_files)
    status, confidence, summary = classify(weak_label, text, safe_poc_used, len(evidence_files))
    rel_files = [str(path.relative_to(out_dir)).replace("\\", "/") for path in evidence_files if path.exists()]
    return {
        "target_id": target_id,
        "weak_label": weak_label,
        "validation_status": status,
        "confidence": confidence,
        "evidence_summary": summary,
        "evidence_files": rel_files,
        "tools_used": sorted(set(tools_used)),
        "safe_poc_used": safe_poc_used,
        "destructive_action": False,
        "notes": "local Vulhub/Docker lab validation only; no destructive action",
    }


def write_summary(out_dir: Path, results: list[dict]) -> None:
    counts: dict[str, int] = {}
    for row in results:
        counts[row["validation_status"]] = counts.get(row["validation_status"], 0) + 1
    lines = [
        "# Dec Kali Validation Scan Summary",
        "",
        f"- generated_at: {datetime.now().isoformat(timespec='seconds')}",
        f"- output: `{out_dir}`",
        f"- total_targets: {len(results)}",
    ]
    for key in ["validated_positive", "validated_negative", "inconclusive", "not_run"]:
        lines.append(f"- {key}: {counts.get(key, 0)}")
    lines.extend(["", "## Target Results", ""])
    for row in results:
        lines.append(f"- `{row['target_id']}`: {row['validation_status']} ({row['confidence']}) - {row['evidence_summary']}")
    lines.extend(["", "หมายเหตุ: ใช้เฉพาะ local lab/Vulhub ที่ควบคุมเองเท่านั้น"])
    write_text(out_dir / "SCAN-SUMMARY-TH.md", "\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run safe Dec validation probes on Kali local labs.")
    parser.add_argument("--queue", default="validation-target-queue.csv")
    parser.add_argument("--features", default="features.csv")
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    queue_path = Path(args.queue)
    features_path = Path(args.features)
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    out_dir = Path(args.output_dir or f"/home/kali/reports/dec-validation-{stamp}")
    out_dir.mkdir(parents=True, exist_ok=True)

    queue = read_csv(queue_path)
    features = read_csv(features_path)
    results = []
    for row in queue:
        feature = find_feature(features, row["target_id"])
        results.append(scan_target(row, feature, out_dir))

    validation_path = out_dir / "validation-results.jsonl"
    with validation_path.open("w", encoding="utf-8") as handle:
        for row in results:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    write_summary(out_dir, results)
    print(json.dumps({"targets": len(results), "output_dir": str(out_dir), "validation_results": str(validation_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
