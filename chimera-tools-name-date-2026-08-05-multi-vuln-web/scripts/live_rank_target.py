from __future__ import annotations

import argparse
import json
import re
import socket
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import joblib
import pandas as pd


FAMILY_RISK = {
    "command-injection": 0.95,
    "sqli": 0.92,
    "nosql-injection": 0.88,
    "xxe": 0.82,
    "deserialization": 0.82,
    "file-upload": 0.78,
    "file-inclusion": 0.74,
    "auth-bypass": 0.70,
    "jwt": 0.68,
    "ssrf": 0.66,
    "broken-access-control": 0.62,
    "xss": 0.55,
    "csrf": 0.35,
    "sensitive-data-exposure": 0.34,
    "bruteforce": 0.30,
    "generic-web": 0.20,
}


PROFILES = {
    "juice-shop": {
        "product": "OWASP Juice Shop",
        "families": ["nosql-injection", "sqli", "xss", "broken-access-control", "auth-bypass", "sensitive-data-exposure", "ssrf"],
    },
    "webgoat": {
        "product": "OWASP WebGoat",
        "families": ["sqli", "xxe", "jwt", "broken-access-control", "deserialization", "xss", "auth-bypass"],
    },
    "dvwa": {
        "product": "Damn Vulnerable Web Application",
        "families": ["command-injection", "sqli", "file-upload", "file-inclusion", "xss", "csrf", "bruteforce"],
    },
    "bwapp": {
        "product": "bWAPP",
        "families": ["sqli", "command-injection", "xss", "xxe", "ssrf", "file-inclusion", "csrf"],
    },
    "mutillidae": {
        "product": "OWASP Mutillidae / NOWASP",
        "families": ["sqli", "xss", "command-injection", "file-inclusion", "auth-bypass", "csrf", "sensitive-data-exposure"],
    },
    "acme-support": {
        "product": "Acme Support Portal",
        "families": ["sqli", "command-injection", "file-inclusion", "broken-access-control", "xss", "sensitive-data-exposure"],
    },
    "nova-devops": {
        "product": "Nova DevOps Console",
        "families": ["command-injection", "sqli", "file-inclusion", "ssrf", "broken-access-control", "xss", "sensitive-data-exposure"],
    },
    "grafana-hard": {
        "product": "Grafana",
        "families": ["sqli", "file-inclusion", "command-injection", "broken-access-control", "sensitive-data-exposure", "ssrf", "xss"],
    },
}


def detect_title(html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    if not match:
        return "none"
    return re.sub(r"\s+", " ", match.group(1)).strip() or "none"


def detect_tech(headers: dict, html: str) -> list[str]:
    text = html.lower()
    tech = []
    server = headers.get("server")
    powered_by = headers.get("x-powered-by")
    if server:
        tech.append(server)
    if powered_by:
        tech.append(powered_by)
    checks = {
        "PHP": ["php", ".php"],
        "Angular": ["ng-version", "angular"],
        "React/Next.js": ["__next", "next.js"],
        "Jenkins": ["jenkins"],
        "Drupal": ["drupal"],
        "Java/Tomcat": ["tomcat", "jsessionid"],
        "Bootstrap": ["bootstrap"],
    }
    for name, needles in checks.items():
        if any(needle in text for needle in needles):
            tech.append(name)
    return sorted(set(tech)) or ["unknown"]


def http_fingerprint(url: str, timeout: int = 10) -> dict:
    req = Request(url, headers={"User-Agent": "Chimera-Exploit-DL-Demo/0.1"})
    parsed = urlparse(url)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    result = {
        "url": url,
        "port": port,
        "http_status_code": 0,
        "http_title": "none",
        "http_server": "none",
        "observed_tech": ["unknown"],
        "content_length": 0,
        "service_reachable": 0,
        "error": None,
    }
    try:
        with urlopen(req, timeout=timeout) as res:
            body = res.read(200_000)
            html = body.decode("utf-8", errors="ignore")
            headers = {k.lower(): v for k, v in res.headers.items()}
            result.update(
                {
                    "http_status_code": int(res.status),
                    "http_title": detect_title(html),
                    "http_server": headers.get("server", "none"),
                    "observed_tech": detect_tech(headers, html),
                    "content_length": len(body),
                    "service_reachable": 1,
                }
            )
    except Exception as exc:
        result["error"] = str(exc)
        try:
            host = parsed.hostname or "127.0.0.1"
            with socket.create_connection((host, port), timeout=timeout):
                result["service_reachable"] = 1
        except Exception:
            pass
    return result


def build_rows(profile: str, url: str, fingerprint: dict) -> pd.DataFrame:
    profile_data = PROFILES[profile]
    rows = []
    for index, family in enumerate(profile_data["families"]):
        prior_rank_score = max(0.18, 0.52 - index * 0.035) + (FAMILY_RISK.get(family, 0.25) - 0.50)
        if fingerprint["service_reachable"]:
            prior_rank_score += 0.08
        if fingerprint["http_status_code"] in {200, 301, 302, 401, 403}:
            prior_rank_score += 0.05
        prior_rank_score = max(0.05, min(0.98, prior_rank_score))
        rows.append(
            {
                "lab_id": f"live-{profile}",
                "product": profile_data["product"],
                "target_url": url,
                "port": int(fingerprint["port"]),
                "candidate_exploit_family": family,
                "rank_score": round(prior_rank_score, 3),
                "family_risk_prior": FAMILY_RISK.get(family, 0.25),
                "evidence_source_count": 1 if fingerprint["service_reachable"] else 0,
                "has_zap_evidence": 0,
                "has_nuclei_evidence": 0,
                "has_wapiti_evidence": 0,
                "has_nikto_evidence": 0,
                "zap_finding_count": 0,
                "nuclei_finding_count": 0,
                "nikto_finding_count": 0,
                "wapiti_finding_count": 0,
                "observed_title_count": 1 if fingerprint["http_title"] != "none" else 0,
                "observed_tech_count": len(fingerprint["observed_tech"]),
                "service_product_count": 1 if fingerprint["http_server"] != "none" else 0,
                "service_version_count": 0,
                "observed_titles_text": fingerprint["http_title"],
                "observed_tech_text": " | ".join(fingerprint["observed_tech"]),
                "service_products_text": fingerprint["http_server"],
                "service_versions_text": "none",
                "evidence_sources_text": "live-http-fingerprint" if fingerprint["service_reachable"] else "none",
            }
        )
    return pd.DataFrame(rows)


def write_report(out_dir: Path, profile: str, fingerprint: dict, predictions: pd.DataFrame) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "fingerprint.json").write_text(json.dumps(fingerprint, indent=2, ensure_ascii=False), encoding="utf-8")
    predictions.to_csv(out_dir / "ranked_exploits.csv", index=False, encoding="utf-8")
    predictions.to_json(out_dir / "ranked_exploits.jsonl", orient="records", lines=True, force_ascii=False)

    top = predictions.head(5)
    md = [
        "# Chimera Live Exploit-DL Report",
        "",
        f"- generated_at: `{datetime.now(timezone.utc).isoformat()}`",
        f"- profile: `{profile}`",
        f"- target_url: `{fingerprint['url']}`",
        f"- reachable: `{fingerprint['service_reachable']}`",
        f"- status_code: `{fingerprint['http_status_code']}`",
        f"- title: `{fingerprint['http_title']}`",
        f"- server: `{fingerprint['http_server']}`",
        f"- tech: `{', '.join(fingerprint['observed_tech'])}`",
        "",
        "## Top exploit families",
        "",
        "| rank | exploit_family | predicted_success_probability | model_note |",
        "|---:|---|---:|---|",
    ]
    for i, row in enumerate(top.to_dict("records"), start=1):
        md.append(
            f"| {i} | `{row['candidate_exploit_family']}` | {row['predicted_success_probability']:.3f} | weak-label demo model |"
        )
    md.extend(
        [
            "",
            "## Important note",
            "",
            "This is a ranking demo from fingerprint + weak-label baseline model. It is not proof that the exploit will succeed. For research-grade labels, run a local exploit validation loop and record `exploit_success_observed`.",
        ]
    )
    (out_dir / "report.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank exploit families for a live local lab target.")
    parser.add_argument("--dataset-root", default=".", help="Path to dataset folder")
    parser.add_argument("--profile", required=True, choices=sorted(PROFILES), help="Known lab profile")
    parser.add_argument("--url", required=True, help="Target URL, e.g. http://127.0.0.1:26001")
    parser.add_argument("--out", default=None, help="Output report folder")
    args = parser.parse_args()

    root = Path(args.dataset_root).resolve()
    model_path = root / "models" / "random_forest_exploit_ranker.joblib"
    if not model_path.exists():
        raise SystemExit(f"Missing model: {model_path}. Run scripts/train_baseline.py first.")

    fingerprint = http_fingerprint(args.url)
    rows = build_rows(args.profile, args.url, fingerprint)
    model = joblib.load(model_path)
    rows["predicted_success_probability"] = model.predict_proba(rows)[:, 1]
    rows = rows.sort_values("predicted_success_probability", ascending=False)
    rows.insert(0, "predicted_rank", range(1, len(rows) + 1))

    out_dir = Path(args.out) if args.out else root / "live-reports" / f"{args.profile}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    write_report(out_dir, args.profile, fingerprint, rows)

    print(f"Report written to: {out_dir}")
    print(rows[["predicted_rank", "candidate_exploit_family", "predicted_success_probability"]].head(8).to_string(index=False))


if __name__ == "__main__":
    main()
