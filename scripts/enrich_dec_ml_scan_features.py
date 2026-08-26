from __future__ import annotations

import argparse
import csv
import json
import re
from html import unescape
from pathlib import Path


TEXT_EXTENSIONS = {".html", ".json", ".jsonl", ".stdout", ".txt", ".xml"}
TEXT_NAME_SUFFIXES = ("_html", "_json", "_jsonl", "_stdout", "_txt", "_xml")
MAX_TEXT_PER_FILE = 12000
MAX_EVIDENCE_TEXT = 24000


def read_text_sample(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:MAX_TEXT_PER_FILE]
    except OSError:
        return ""


def strip_html(text: str) -> str:
    text = re.sub(r"(?is)<script.*?</script>", " ", text)
    text = re.sub(r"(?is)<style.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return unescape(text)


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def is_text_evidence(path: Path) -> bool:
    name = path.name.lower()
    return path.suffix.lower() in TEXT_EXTENSIONS or name.endswith(TEXT_NAME_SUFFIXES)


def evidence_sort_key(path: Path) -> tuple[int, str]:
    return (0 if path.name.lower().startswith("validation_") else 1, path.name.lower())


def evidence_label(path: Path) -> str:
    label = path.name
    label = re.sub(r"(?i)^validation_[^_]+_", "validation_file_", label)
    return label


def redact_leakage(text: str, target_id: str) -> str:
    redacted = text
    variants = {
        target_id,
        target_id.lower(),
        target_id.upper(),
        target_id.replace("_", "-"),
        target_id.replace("-", "_"),
    }
    for variant in sorted(variants, key=len, reverse=True):
        if variant:
            redacted = redacted.replace(variant, " TARGET_ID_REDACTED ")
    redacted = re.sub(r"(?i)cve-\d{4}-\d{4,7}", " CVE_REDACTED ", redacted)
    redacted = re.sub(r"[/\\][^\s\"']*dec-ml-scan-2026-08-25[/\\][^\s\"']+", " PATH_REDACTED ", redacted)
    return redacted


def count_nikto_findings(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.lstrip().startswith("+") and "Target " not in line)


def count_nuclei_findings(text: str) -> int:
    count = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            json.loads(line)
            count += 1
        except json.JSONDecodeError:
            if "[" in line and "]" in line:
                count += 1
    return count


def count_wapiti_findings(text: str) -> int:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return 0
    total = 0
    for section_name in ("vulnerabilities", "anomalies", "additionals"):
        section = payload.get(section_name, {})
        if isinstance(section, dict):
            for items in section.values():
                if isinstance(items, list):
                    total += len(items)
    return total


def extract_title(text: str) -> str:
    match = re.search(r"(?is)<title[^>]*>(.*?)</title>", text)
    return compact(strip_html(match.group(1))) if match else ""


def collect_target_evidence(target_dir: Path, target_id: str) -> dict[str, object]:
    raw_dir = target_dir / "raw"
    if not raw_dir.exists():
        return {}

    evidence_parts: list[str] = []
    file_count = 0
    nikto_count = 0
    nuclei_count = 0
    wapiti_count = 0
    best_title = ""

    for path in sorted(raw_dir.rglob("*"), key=evidence_sort_key):
        if not path.is_file() or not is_text_evidence(path):
            continue
        text = read_text_sample(path)
        if not text:
            continue
        file_count += 1
        lower_name = path.name.lower()
        cleaned = strip_html(text) if path.suffix.lower() == ".html" else text
        cleaned = redact_leakage(cleaned, target_id)
        evidence_parts.append(f"{evidence_label(path)}: {compact(cleaned)}")

        if path.suffix.lower() == ".html" and not best_title:
            best_title = extract_title(text)
        if lower_name.startswith("nikto"):
            nikto_count += count_nikto_findings(text)
        elif lower_name.startswith("nuclei"):
            nuclei_count += count_nuclei_findings(text)
        elif lower_name.startswith("wapiti"):
            wapiti_count += count_wapiti_findings(read_text_sample(path) if path.suffix.lower() != ".json" else path.read_text(encoding="utf-8", errors="ignore"))

    body_fingerprint = compact(" ".join(evidence_parts))[:MAX_EVIDENCE_TEXT]
    return {
        "body_fingerprint": body_fingerprint,
        "raw_title": best_title,
        "evidence_text": body_fingerprint,
        "evidence_file_count": file_count,
        "nikto_finding_count": nikto_count,
        "nuclei_finding_count": nuclei_count,
        "wapiti_finding_count": wapiti_count,
    }


def merge_row(row: dict[str, str], target_root: Path) -> dict[str, str]:
    evidence = collect_target_evidence(target_root / row["target_id"], row["target_id"])
    out = dict(row)
    if not out.get("title") and evidence.get("raw_title"):
        out["title"] = str(evidence["raw_title"])
    for key, value in evidence.items():
        out[key] = str(value)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich Dec ML scan features from raw-curated evidence files.")
    parser.add_argument("--experiment-dir", default="experiments/dec-ml-scan-2026-08-25")
    parser.add_argument("--raw-root", default="dataset/raw-curated/dec-ml-scan-2026-08-25")
    parser.add_argument("--input", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    experiment_dir = Path(args.experiment_dir)
    input_path = Path(args.input) if args.input else experiment_dir / "features.csv"
    output_path = Path(args.output) if args.output else experiment_dir / "features-enriched.csv"
    raw_root = Path(args.raw_root)

    with input_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        base_fieldnames = list(reader.fieldnames or [])

    enriched = [merge_row(row, raw_root) for row in rows]
    extra_fields = [
        "body_fingerprint",
        "raw_title",
        "evidence_text",
        "evidence_file_count",
        "nikto_finding_count",
        "nuclei_finding_count",
        "wapiti_finding_count",
    ]
    fieldnames = base_fieldnames + [field for field in extra_fields if field not in base_fieldnames]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched)

    print(
        json.dumps(
            {
                "input": str(input_path),
                "output": str(output_path),
                "rows": len(enriched),
                "with_evidence_text": sum(1 for row in enriched if row.get("evidence_text")),
                "with_nikto": sum(1 for row in enriched if int(row.get("nikto_finding_count") or 0) > 0),
                "with_wapiti": sum(1 for row in enriched if int(row.get("wapiti_finding_count") or 0) > 0),
                "with_nuclei": sum(1 for row in enriched if int(row.get("nuclei_finding_count") or 0) > 0),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
