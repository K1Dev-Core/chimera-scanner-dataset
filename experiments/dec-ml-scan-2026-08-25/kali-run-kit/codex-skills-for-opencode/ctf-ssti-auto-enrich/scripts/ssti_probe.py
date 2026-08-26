#!/usr/bin/env python3
"""Stdlib-only SSTI recon helper for scoped CTF targets."""

from __future__ import annotations

import argparse
import html
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_PAYLOADS = [
    "ssti_probe_marker",
    "{{7*7}}",
    "{{7*'7'}}",
    "${7*7}",
    "<%= 7*7 %>",
    "#{7*7}",
    "*{7*7}",
]


def fetch(url: str, insecure: bool) -> tuple[int, str]:
    context = ssl._create_unverified_context() if insecure else None
    req = urllib.request.Request(url, headers={"User-Agent": "Codex-CTF-SSTI-Probe/1.1"})
    try:
        with urllib.request.urlopen(req, context=context, timeout=20) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


def discover_form(url: str, insecure: bool) -> tuple[str, str, str]:
    status, text = fetch(url, insecure)
    if status >= 400:
        return url, "POST", "input"

    form = re.search(r"<form\b(?P.attrs>.*?)>(?P<body>.*?)</form>", text, re.I | re.S)
    if not form:
        field = guess_field(text) or "input"
        return url, "GET", field

    attrs = form.group("attrs")
    body = form.group("body")
    method = attr_value(attrs, "method") or "GET"
    action = attr_value(attrs, "action") or url
    field = guess_field(body) or "input"
    return urllib.parse.urljoin(url, html.unescape(action)), method.upper(), field


def attr_value(attrs: str, name: str) -> str | None:
    match = re.search(rf"""{name}\s*=\s*["']([^"']+)["']""", attrs, re.I)
    return html.unescape(match.group(1)) if match else None


def guess_field(text: str) -> str | None:
    preferred = re.search(r"<textarea\b[^>]*\bname\s*=\s*['\"]([^'\"]+)['\"]", text, re.I)
    if preferred:
        return html.unescape(preferred.group(1))
    for tag in re.finditer(r"<input\b[^>]*>", text, re.I):
        raw = tag.group(0)
        kind = (attr_value(raw, "type") or "text").lower()
        name = attr_value(raw, "name")
        if name and kind not in {"hidden", "submit", "button", "csrf"}:
            return name
    return None


def load_payloads(args: argparse.Namespace) -> list[str]:
    payloads: list[str] = []
    if args.payload:
        payloads.append(args.payload)
    if args.payload_file:
        with open(args.payload_file, "r", encoding="utf-8") as handle:
            payloads.extend(line.rstrip("\n") for line in handle if line.strip())
    return payloads or DEFAULT_PAYLOADS


def request_once(url: str, method: str, field: str, payload: str, insecure: bool) -> tuple[int, str]:
    context = ssl._create_unverified_context() if insecure else None
    headers = {"User-Agent": "Codex-CTF-SSTI-Probe/1.1"}
    if method == "GET":
        sep = "&" if "?" in url else "?"
        req = urllib.request.Request(url + sep + urllib.parse.urlencode({field: payload}), headers=headers)
    else:
        body = urllib.parse.urlencode({field: payload}).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        req = urllib.request.Request(url, data=body, headers=headers)

    try:
        with urllib.request.urlopen(req, context=context, timeout=20) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


def extract_near_label(text: str, label: str | None) -> str:
    clean = html.unescape(text)
    clean = re.sub(r"<script\b.*?</script>", " ", clean, flags=re.I | re.S)
    clean = re.sub(r"\s+", " ", clean)
    if not label:
        return clean[:600]
    index = clean.lower().find(label.lower())
    return clean[index : index + 800] if index != -1 else clean[:600]


def signal(payload: str, status: int, text: str) -> str:
    clean = html.unescape(text)
    if status >= 500:
        return "server-error"
    if "49" in clean and payload in {"{{7*7}}", "${7*7}", "<%= 7*7 %>", "#{7*7}", "*{7*7}"}:
        return "math-rendered"
    if "7777777" in clean and payload == "{{7*'7'}}":
        return "jinja-pythonic-render"
    if payload in clean:
        return "literal-reflection"
    if any(word in clean.lower() for word in ["blocked", "rejected", "forbidden", "firewall"]):
        return "blocked-or-filtered"
    return "changed-output"


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe a one-field web form for SSTI behavior.")
    parser.add_argument("url")
    parser.add_argument("--auto", action="store_true", help="Discover first form action/method/field from the page")
    parser.add_argument("--method", choices=["GET", "POST"], default="POST")
    parser.add_argument("--field", default="input")
    parser.add_argument("--payload")
    parser.add_argument("--payload-file")
    parser.add_argument("--extract", help="Label or nearby text to print around in the response")
    parser.add_argument("--summary", action="store_true", help="Print compact status/signal lines only")
    parser.add_argument("--verify-tls", action="store_true", help="Verify TLS certificates")
    args = parser.parse_args()

    url, method, field = args.url, args.method, args.field
    if args.auto:
        url, method, field = discover_form(args.url, not args.verify_tls)
        print(f"[*] auto target: {method} {url} field={field}")

    for payload in load_payloads(args):
        status, text = request_once(url, method, field, payload, not args.verify_tls)
        mark = signal(payload, status, text)
        print(f"\n=== {status} {mark} {payload!r}")
        if not args.summary:
            print(extract_near_label(text, args.extract))
    return 0


if __name__ == "__main__":
    sys.exit(main())
