from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_queue(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["target_id"]: row for row in csv.DictReader(handle)}


def grouped(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        out[row["target_id"]].append(row)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Dec ML attack order from ranking predictions.")
    parser.add_argument("--experiment-dir", default="experiments/dec-ml-scan-2026-08-25")
    parser.add_argument("--prediction-file", default=None)
    parser.add_argument("--queue-file", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--suffix", default="")
    args = parser.parse_args()

    experiment_dir = Path(args.experiment_dir)
    prediction_file = Path(args.prediction_file) if args.prediction_file else experiment_dir / "reports" / "dec-ml-scan-ranking-predictions.json"
    queue_file = Path(args.queue_file) if args.queue_file else experiment_dir / "validation-target-queue.csv"
    output_dir = Path(args.output_dir) if args.output_dir else experiment_dir / "derived"
    output_dir.mkdir(parents=True, exist_ok=True)

    predictions = load_json(prediction_file)
    queue_by_target = load_queue(queue_file)
    rows = []
    for target_id, group in grouped(predictions).items():
        queue = queue_by_target.get(target_id, {})
        ranked = sorted(group, key=lambda row: int(row.get("ml_probability_rank", 999999)))
        for row in ranked[: args.top_k]:
            rows.append(
                {
                    "target_id": target_id,
                    "queue_priority": queue.get("priority", ""),
                    "queue_type": queue.get("queue_type", ""),
                    "queue_reason": queue.get("reason", ""),
                    "candidate_family": row["candidate_family"],
                    "positive_family": row["positive_family"],
                    "is_positive": bool(row["is_positive"]),
                    "ml_rank": int(row["ml_probability_rank"]),
                    "ml_probability": float(row["ml_probability"]),
                    "heuristic_rank": int(row["heuristic_score_rank"]),
                    "heuristic_score": float(row["heuristic_score"]),
                    "recommended_action": "validate_expected_family" if row["is_positive"] else "compare_as_negative_or_confuser",
                }
            )

    suffix = f"-{args.suffix}" if args.suffix else ""
    csv_path = output_dir / f"attack-order-top{args.top_k}{suffix}.csv"
    jsonl_path = output_dir / f"attack-order-top{args.top_k}{suffix}.jsonl"
    fieldnames = [
        "target_id",
        "queue_priority",
        "queue_type",
        "queue_reason",
        "candidate_family",
        "positive_family",
        "is_positive",
        "ml_rank",
        "ml_probability",
        "heuristic_rank",
        "heuristic_score",
        "recommended_action",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(json.dumps({"rows": len(rows), "csv": str(csv_path), "jsonl": str(jsonl_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
