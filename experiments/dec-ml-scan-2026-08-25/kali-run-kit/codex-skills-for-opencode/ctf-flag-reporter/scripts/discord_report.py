#!/usr/bin/env python3
import argparse
import json
import os
import socket
import sys
import urllib.request
from pathlib import Path

config_path = Path.home() / ".config" / "opencode" / "ctf-flag-reporter.json"
try:
    config = json.loads(config_path.read_text(encoding="utf-8"))
except (FileNotFoundError, json.JSONDecodeError):
    config = {}

service_env = {}
service_env_paths = [
    Path.home() / "ctf_flag_service" / ".env",
    Path.cwd() / "ctf_flag_service" / ".env",
]
for service_env_path in service_env_paths:
    try:
        for raw in service_env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            service_env[k.strip()] = v.strip().strip('"').strip("'")
        break
    except FileNotFoundError:
        continue

hostname = socket.gethostname()

parser = argparse.ArgumentParser(description="Send solved CTF report to local ctf-flag-service")
parser.add_argument("--challenge", required=True)
parser.add_argument("--category", required=True)
parser.add_argument("--flag", required=True)
parser.add_argument("--summary", required=True)
parser.add_argument("--reporter-name", default=os.getenv("CTF_REPORTER_NAME", "") or hostname)
parser.add_argument("--api-url", default=os.getenv("CTF_FLAG_SERVICE_URL", config.get("ctf_flag_service_url", service_env.get("CTF_FLAG_SERVICE_URL", "http://127.0.0.1:8765/api/report"))))
parser.add_argument("--api-token", default=os.getenv("CTF_FLAG_SERVICE_TOKEN", config.get("ctf_flag_service_token", service_env.get("API_TOKEN", ""))))
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()

payload = {
    "challenge": args.challenge,
    "category": args.category,
    "flag": args.flag,
    "summary": args.summary,
    "reporter_name": str(args.reporter_name or hostname).strip() or hostname,
    "reporter_host": hostname,
    "source": "ctf-flag-reporter-skill",
}

if args.dry_run:
    print(json.dumps({"url": args.api_url, "payload": payload}, ensure_ascii=False, indent=2))
    raise SystemExit(0)

headers = {"Content-Type": "application/json", "User-Agent": "OpenCode-CTF-Service-Bridge"}
if args.api_token:
    headers["Authorization"] = f"Bearer {args.api_token}"
request = urllib.request.Request(
    args.api_url,
    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    headers=headers,
    method="POST",
)
try:
    with urllib.request.urlopen(request, timeout=20) as response:
        result = json.loads(response.read().decode("utf-8"))
except Exception as e:
    print(f"CTF flag service report failed: {e}", file=sys.stderr)
    raise SystemExit(2)

print(json.dumps(result, ensure_ascii=False, indent=2))
if not result.get("ok"):
    raise SystemExit(1)
print("CTF flag service report sent")
