from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen


FAMILY_PRIORS = [
    ("auth-bypass", 0.78, "login/register flow is the primary exposed surface"),
    ("sqli", 0.68, "username/password POST form may depend on backend query handling"),
    ("broken-access-control", 0.62, "social-app style account/session flows often expose authorization checks"),
    ("xss", 0.48, "social posting/profile surfaces are plausible but not yet observed from login page"),
    ("sensitive-data-exposure", 0.35, "framework/version header is visible; more evidence needed"),
    ("csrf", 0.28, "state-changing forms exist; token evidence not yet collected"),
]


def fetch(url: str) -> dict:
    req = Request(url, headers={"User-Agent": "Chimera-AB-Test-Fingerprint/0.1"})
    with urlopen(req, timeout=20) as res:
        body = res.read(250_000)
        text = body.decode("utf-8", errors="ignore")
        headers = {k.lower(): v for k, v in res.headers.items()}
        title_match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.I | re.S)
        links = sorted(set(re.findall(r"""href=["']([^"']+)["']""", text, flags=re.I)))
        forms = re.findall(r"<form\b[\s\S]*?</form>", text, flags=re.I)
        inputs = sorted(set(re.findall(r"""name=["']([^"']+)["']""", text, flags=re.I)))
        return {
            "url": url,
            "status_code": res.status,
            "content_type": headers.get("content-type", ""),
            "server": headers.get("server", ""),
            "content_length": len(body),
            "title": re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else "",
            "links": [urljoin(url, link) for link in links],
            "form_count": len(forms),
            "input_names": inputs,
        }


def build_report(fp: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    ranking = []
    for i, (family, score, reason) in enumerate(FAMILY_PRIORS, start=1):
        ranking.append(
            {
                "rank": i,
                "exploit_family": family,
                "predicted_priority_score": score,
                "reason": reason,
                "label_type": "safe weak-prior ranking from passive fingerprint",
            }
        )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": fp["url"],
        "fingerprint": fp,
        "ranking": ranking,
        "warning": "Passive fingerprint/ranking only. Not proof of exploitability and not a payload guide.",
    }
    (out_dir / "chimera_model_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "ranked_families.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in ranking) + "\n", encoding="utf-8")

    lines = [
        "# Chimera A/B Test Model Report",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- target: `{fp['url']}`",
        f"- status_code: `{fp['status_code']}`",
        f"- title: `{fp['title']}`",
        f"- server: `{fp['server']}`",
        f"- content_type: `{fp['content_type']}`",
        f"- form_count: `{fp['form_count']}`",
        f"- input_names: `{', '.join(fp['input_names'])}`",
        f"- discovered_links: `{', '.join(fp['links'])}`",
        "",
        "## Ranked vulnerability families",
        "",
        "| rank | family | score | reason |",
        "|---:|---|---:|---|",
    ]
    for row in ranking:
        lines.append(f"| {row['rank']} | `{row['exploit_family']}` | {row['predicted_priority_score']:.2f} | {row['reason']} |")
    lines.extend(
        [
            "",
            "## Limitation",
            "",
            "This report is a safe prioritization aid from passive fingerprint only. It should be used to decide what to inspect first, not as proof that an exploit will work.",
        ]
    )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    fp = fetch(args.url)
    out_dir = Path(args.out)
    build_report(fp, out_dir)
    print(f"Report written to: {out_dir}")
    print(json.dumps({"title": fp["title"], "server": fp["server"], "forms": fp["form_count"], "inputs": fp["input_names"]}, indent=2))


if __name__ == "__main__":
    main()
