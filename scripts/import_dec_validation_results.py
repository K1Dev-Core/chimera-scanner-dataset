from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


VALID_STATUSES = {"validated_positive", "validated_negative", "inconclusive", "not_run"}
VALID_CONFIDENCE = {"high", "medium", "low", "none"}
REQUIRED_FIELDS = [
    "target_id",
    "weak_label",
    "validation_status",
    "confidence",
    "evidence_summary",
    "evidence_files",
    "tools_used",
    "safe_poc_used",
    "destructive_action",
    "notes",
]


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        validate_row(row, path, line_number)
        rows.append(row)
    return rows


def validate_row(row: dict, path: Path, line_number: int) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in row]
    if missing:
        raise ValueError(f"{path}:{line_number}: missing fields: {missing}")
    if row["validation_status"] not in VALID_STATUSES:
        raise ValueError(f"{path}:{line_number}: invalid validation_status={row['validation_status']!r}")
    if row["confidence"] not in VALID_CONFIDENCE:
        raise ValueError(f"{path}:{line_number}: invalid confidence={row['confidence']!r}")
    if not isinstance(row["evidence_files"], list):
        raise ValueError(f"{path}:{line_number}: evidence_files must be a list")
    if not isinstance(row["tools_used"], list):
        raise ValueError(f"{path}:{line_number}: tools_used must be a list")
    if not isinstance(row["safe_poc_used"], bool):
        raise ValueError(f"{path}:{line_number}: safe_poc_used must be boolean")
    if not isinstance(row["destructive_action"], bool):
        raise ValueError(f"{path}:{line_number}: destructive_action must be boolean")
    if row["destructive_action"]:
        raise ValueError(f"{path}:{line_number}: destructive_action=true is not allowed for this dataset")


def label_strength(row: dict) -> str:
    if row["validation_status"] == "validated_positive" and row["confidence"] in {"high", "medium"}:
        return "validated"
    if row["validation_status"] == "validated_negative":
        return "validated_negative"
    if row["validation_status"] == "inconclusive":
        return "weak_pending_validation"
    return "not_run"


def write_outputs(rows: list[dict], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "target_id",
        "weak_label",
        "validation_status",
        "confidence",
        "label_strength",
        "safe_poc_used",
        "evidence_file_count",
        "tools_used",
        "evidence_summary",
        "notes",
    ]
    out_rows = []
    for row in rows:
        out_rows.append(
            {
                "target_id": row["target_id"],
                "weak_label": row["weak_label"],
                "validation_status": row["validation_status"],
                "confidence": row["confidence"],
                "label_strength": label_strength(row),
                "safe_poc_used": row["safe_poc_used"],
                "evidence_file_count": len(row["evidence_files"]),
                "tools_used": ";".join(row["tools_used"]),
                "evidence_summary": row["evidence_summary"],
                "notes": row["notes"],
            }
        )

    with (output_dir / "validated-labels.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)
    with (output_dir / "validated-labels.jsonl").open("w", encoding="utf-8") as handle:
        for row in out_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and import Dec Kali validation results.")
    parser.add_argument("--input", default="experiments/dec-ml-scan-2026-08-25/validation-results.example.jsonl")
    parser.add_argument("--output-dir", default="experiments/dec-ml-scan-2026-08-25/derived")
    args = parser.parse_args()

    rows = load_jsonl(Path(args.input))
    write_outputs(rows, Path(args.output_dir))
    print(json.dumps({"input_rows": len(rows), "output_dir": args.output_dir}, ensure_ascii=False))


if __name__ == "__main__":
    main()
