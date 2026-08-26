from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

from import_dec_validation_results import load_jsonl, validate_row, write_outputs


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value)


def safe_file_name(path: Path) -> str:
    stem = safe_name(path.stem)
    suffix = path.suffix.lower()
    if suffix:
        return f"{stem}{suffix}"
    return safe_name(path.name)


def copy_raw_curated(run_dir: Path, raw_root: Path) -> dict[str, int]:
    source_root = run_dir / "raw-curated"
    if not source_root.exists():
        return {"targets": 0, "files": 0}

    run_name = safe_name(run_dir.name)
    target_count = 0
    file_count = 0
    for target_dir in sorted(path for path in source_root.iterdir() if path.is_dir()):
        target_count += 1
        source_raw = target_dir / "raw"
        if not source_raw.exists():
            continue
        dest_raw = raw_root / target_dir.name / "raw"
        dest_raw.mkdir(parents=True, exist_ok=True)
        for source_file in sorted(path for path in source_raw.rglob("*") if path.is_file()):
            rel = source_file.relative_to(source_raw)
            dest_name = f"validation_{run_name}_{safe_file_name(rel)}"
            shutil.copy2(source_file, dest_raw / dest_name)
            file_count += 1
    return {"targets": target_count, "files": file_count}


def load_existing_validation_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                {
                    "target_id": row.get("target_id", ""),
                    "weak_label": row.get("weak_label", ""),
                    "validation_status": row.get("validation_status", ""),
                    "confidence": row.get("confidence", ""),
                    "evidence_summary": row.get("evidence_summary", ""),
                    "evidence_files": [],
                    "tools_used": [tool for tool in str(row.get("tools_used", "")).split(";") if tool],
                    "safe_poc_used": str(row.get("safe_poc_used", "")).lower() == "true",
                    "destructive_action": False,
                    "notes": row.get("notes", ""),
                }
            )
    return rows


def merge_validation_rows(existing: list[dict], incoming: list[dict]) -> list[dict]:
    by_target: dict[str, dict] = {}
    for row in existing + incoming:
        if row.get("target_id"):
            by_target[str(row["target_id"])] = row
    return [by_target[target_id] for target_id in sorted(by_target)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest one Dec Kali validation run into the ML experiment.")
    parser.add_argument("--run-dir", required=True, help="Shared Kali output folder containing validation-results.jsonl")
    parser.add_argument("--experiment-dir", default="experiments/dec-ml-scan-2026-08-25")
    parser.add_argument("--raw-root", default="dataset/raw-curated/dec-ml-scan-2026-08-25")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    validation_path = run_dir / "validation-results.jsonl"
    if not validation_path.exists():
        raise FileNotFoundError(f"missing {validation_path}")

    rows = load_jsonl(validation_path)
    experiment_dir = Path(args.experiment_dir)
    output_dir = experiment_dir / "derived"
    existing_rows = load_existing_validation_rows(output_dir / "validated-labels.csv")
    merged_rows = merge_validation_rows(existing_rows, rows)
    for line_number, row in enumerate(merged_rows, start=1):
        validate_row(row, output_dir / "validated-labels.csv", line_number)
    write_outputs(merged_rows, output_dir)
    copied = copy_raw_curated(run_dir, Path(args.raw_root))
    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "validation_rows": len(rows),
                "merged_validation_rows": len(merged_rows),
                "validated_labels": str(experiment_dir / "derived" / "validated-labels.csv"),
                "raw_copied": copied,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
