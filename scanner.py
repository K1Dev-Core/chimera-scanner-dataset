from __future__ import annotations

import re
import shutil
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

# Tools run in PARALLEL. Each tool fn writes its own target fields; a lock guards the shared dict.
# emit(event, tool, message, level) streams a log line + lifecycle events to the UI.

_LOCK = threading.Lock()


def _have(tool: str) -> bool:
    return shutil.which(tool) is not None


def _run(cmd: list[str], timeout: int = 90) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        return -1, ""
    except FileNotFoundError:
        return -1, ""


def _set(target, key, value):
    with _LOCK:
        target[key] = value


def _probe(target, url, emit):
    emit("tool_start", "probe", "", "")
    _set(target, "has_probe", "0")
    emit("log", "probe", f"HTTP GET {url} (title/server/status)", "cmd")
    try:
        req = Request(url, headers={"User-Agent": "ChimeraScanner/1.0"})
        with urlopen(req, timeout=10) as resp:  # noqa: S310
            status = str(resp.status)
            headers = dict(resp.getheaders())
            body = ""
            try:
                body = resp.read(65536).decode("utf-8", "ignore")
            except Exception:  # noqa: BLE001
                body = ""
        _set(target, "http_status", status)
        _set(target, "server", headers.get("Server", "") or "")
        _set(target, "x_powered_by", headers.get("X-Powered-By", "") or "")
        m = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
        if m:
            _set(target, "title", m.group(1).strip().replace("\n", " "))
        _set(target, "has_probe", "1")
        emit("log", "probe", f"[status] {status} | [server] {target['server'] or '(none)'} | [title] {target['title'] or '(none)'}", "info")
    except URLError as exc:
        emit("log", "probe", f"probe error: {exc.reason}", "warn")
    except Exception as exc:  # noqa: BLE001
        emit("log", "probe", f"probe error: {exc}", "warn")
    emit("tool_done", "probe", "", "")


def _nmap(target, url, host, port, emit):
    emit("tool_start", "nmap", "", "")
    if not _have("nmap"):
        emit("log", "nmap", "nmap not installed, skipping port scan", "warn")
        emit("tool_done", "nmap", "", "")
        return
    _set(target, "port", port)
    emit("log", "nmap", f"nmap -sV -Pn -p {port} {host}", "cmd")
    _, out = _run(["nmap", "-sV", "-Pn", "-p", str(port), host], 90)
    for line in out.splitlines():
        if line.strip():
            emit("log", "nmap", line, "raw")
    m = re.search(r"(\d+)/tcp\s+open\s+(\S+)\s+(.*)", out)
    if m:
        service_line = f"{m.group(2)} {m.group(3)}".strip()
        _set(target, "nmap_service_line", service_line)
        low = m.group(2).lower()
        if low not in ("http", "https", "ssl/http", "ssl/https"):
            _set(target, "protocol_kind", "nonhttp")
        emit("log", "nmap", f"[detect] service={service_line}", "info")
    elif out.strip():
        m2 = re.search(r"(\d+)/tcp\s+(open|closed|filtered)\s+(.*)", out)
        if m2:
            _set(target, "nmap_service_line", m2.group(3).strip())
            emit("log", "nmap", f"[detect] port {m2.group(1)} {m2.group(2)}", "info")
    emit("tool_done", "nmap", "", "")


def _nikto(target, url, emit):
    emit("tool_start", "nikto", "", "")
    if not _have("nikto"):
        emit("log", "nikto", "nikto not installed, skipping", "warn")
        emit("tool_done", "nikto", "", "")
        return
    _set(target, "has_nikto", "0")
    emit("log", "nikto", f"nikto -h {url} -nointeractive", "cmd")
    _, out = _run(["nikto", "-h", url, "-nointeractive"], 120)
    hits = 0
    for line in out.splitlines():
        if not line.strip():
            continue
        emit("log", "nikto", line, "raw")
        if "+" in line and ("OSVDB" in line or "CVE-" in line or ":" in line):
            hits += 1
    if hits:
        _set(target, "has_nikto", "1")
        emit("log", "nikto", f"[summary] {hits} lines of interest", "info")
    emit("tool_done", "nikto", "", "")


def _nuclei(target, url, emit):
    emit("tool_start", "nuclei", "", "")
    if not _have("nuclei"):
        emit("log", "nuclei", "nuclei not installed, skipping", "warn")
        emit("tool_done", "nuclei", "", "")
        return
    _set(target, "has_nuclei", "0")
    # ponytail: full template run but tuned for SPEED — no-interactsh (-ni),
    # high concurrency (-c 100), limit rate (-rl 200), short timeout, retries 0.
    emit("log", "nuclei", f"nuclei -u {url} -silent -ni -c 100 -rl 200 -timeout 5 -retries 0", "cmd")
    _, out = _run(
        ["nuclei", "-u", url, "-nc", "-no-color", "-silent", "-ni",
         "-c", "100", "-rl", "200", "-timeout", "5", "-retries", "0"], 200)
    for line in out.splitlines():
        if line.strip():
            emit("log", "nuclei", line, "raw")
    findings = [l for l in out.splitlines()
                if "[" in l and l.count("[") >= 2
                and not l.lstrip().startswith(("[INF]", "[WRN]", "[DBG]", "[FTL]", "[TRC]"))]
    if findings:
        _set(target, "has_nuclei", "1")
        _set(target, "nuclei_findings", findings[:20])
        emit("log", "nuclei", f"[summary] {len(findings)} template matches", "info")
    else:
        emit("log", "nuclei", "[summary] 0 template matches", "info")
    emit("tool_done", "nuclei", "", "")


# Tools we know about but are not installed on this host (Kali/system-specific). Skipped gracefully.
KNOWN_BUT_UNAVAILABLE = [
    "dnsrecon", "enum4linux", "enum4linux-ng", "feroxbuster", "impacket-scripts",
    "nbtscan", "onesixtyone", "oscanner", "smbmap", "sslscan", "svwar",
    "tnscmd10g", "whatweb", "wapiti",
]


def _summary(target, tool, lines):
    with _LOCK:
        target.setdefault("tool_summary", {})[tool] = lines


def _curl(target, url, emit):
    emit("tool_start", "curl", "", "")
    out = ""
    if _have("curl"):
        emit("log", "curl", f"curl -sk -I {url} (headers + banner)", "cmd")
        rc, out = _run(["curl", "-sk", "-I", "--max-time", "15", url], 20)
        interesting = [l for l in out.splitlines() if l.strip()][:14]
        for line in interesting:
            emit("log", "curl", line, "raw")
        _summary(target, "curl", interesting)
    else:
        emit("log", "curl", "curl not installed, skipping", "warn")
    emit("tool_done", "curl", "", "")


def _gobuster(target, url, emit):
    emit("tool_start", "gobuster", "", "")
    if _have("gobuster"):
        emit("log", "gobuster", f"gobuster dir -u {url} -w /usr/share/wordlists/dirb/common.txt", "cmd")
        rc, out = _run(["gobuster", "dir", "-q", "-u", url, "-w", "/usr/share/wordlists/dirb/common.txt", "-t", "20", "--timeout", "8s"], 60)
        for line in out.splitlines():
            if line.strip() and "Status:" in line:
                emit("log", "gobuster", line, "raw")
                _summary(target, "gobuster", [line])
    else:
        emit("log", "gobuster", "gobuster not installed (or no wordlist), skipping dir brute", "warn")
    emit("tool_done", "gobuster", "", "")


def _redis_cli(target, url, host, port, emit):
    emit("tool_start", "redis-tools", "", "")
    if _have("redis-cli") and port == 6379:
        emit("log", "redis-tools", f"redis-cli -h {host} -p {port} info", "cmd")
        rc, out = _run(["redis-cli", "-h", host, "-p", str(port), "info", "server"], 12)
        lines = [l for l in out.splitlines() if l.strip()][:14]
        for line in lines:
            emit("log", "redis-tools", line, "raw")
        _summary(target, "redis-tools", lines)
    else:
        emit("log", "redis-tools", "redis-cli: skip (target is not on port 6379)", "warn")
    emit("tool_done", "redis-tools", "", "")


def _smbclient(target, url, host, emit):
    emit("tool_start", "smbclient", "", "")
    if _have("smbclient"):
        emit("log", "smbclient", f"smbclient -L {host} -N (list shares)", "cmd")
        rc, out = _run(["smbclient", "-L", host, "-N", "-g"], 20)
        shares = [l for l in out.splitlines() if "Disk" in l or "|" in l][:14]
        for line in shares:
            emit("log", "smbclient", line, "raw")
        _summary(target, "smbclient", shares)
    else:
        emit("log", "smbclient", "smbclient not installed, skipping", "warn")
    emit("tool_done", "smbclient", "", "")


def _snmpwalk(target, url, host, emit):
    emit("tool_start", "snmpwalk", "", "")
    if _have("snmpwalk"):
        emits = ["snmpwalk -v2c -c public {host} system"]
        emit("log", "snmpwalk", f"snmpwalk -v2c -c public {host} system", "cmd")
        rc, out = _run(["snmpwalk", "-v2c", "-c", "public", "-t", "3", host, "system"], 20)
        lines = [l for l in out.splitlines() if ".0 =" in l][:14]
        for line in lines:
            emit("log", "snmpwalk", line, "raw")
        _summary(target, "snmpwalk", lines)
    else:
        emit("log", "snmpwalk", "snmpwalk not installed, skipping", "warn")
    emit("tool_done", "snmpwalk", "", "")


def run_scan(url: str, emit) -> dict:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    target = {
        "target_id": host or url,
        "url": url,
        "port": port,
        "protocol_kind": "http" if parsed.scheme in ("http", "https") else "nonhttp",
        "title": "",
        "server": "",
        "http_status": "",
        "nmap_service_line": "",
        "has_probe": "0",
        "has_nikto": "0",
        "has_wapiti": "0",
        "has_nuclei": "0",
        "nuclei_findings": [],
        "tool_summary": {},
        "skipped_tools": [],
    }

    jobs = [
        lambda: _nmap(target, url, host, port, emit),
        lambda: _probe(target, url, emit),
        lambda: _nikto(target, url, emit),
        lambda: _nuclei(target, url, emit),
        lambda: _curl(target, url, emit),
        lambda: _gobuster(target, url, emit),
        lambda: _redis_cli(target, url, host, port, emit),
        lambda: _smbclient(target, url, host, emit),
        lambda: _snmpwalk(target, url, host, emit),
    ]
    unavailable = [t for t in KNOWN_BUT_UNAVAILABLE]
    if unavailable:
        with _LOCK:
            target["skipped_tools"] = unavailable
        emit("log", "app", f"not installed on this host (skipped): {', '.join(unavailable)}", "warn")
    emit("log", "app", f"scanning {url} — running {len(jobs)} tools in parallel", "info")
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futures = {pool.submit(job): job for job in jobs}
        for fut in as_completed(futures):
            try:
                fut.result()
            except Exception as exc:  # noqa: BLE001
                emit("log", "app", f"tool error: {exc}", "warn")

    emit("done", "app", "Scan complete", "done")
    return target
