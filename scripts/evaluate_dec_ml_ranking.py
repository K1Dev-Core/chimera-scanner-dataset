from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


SAFE_NUMERIC_FEATURES = [
    "candidate_product_match_score",
    "candidate_service_match_score",
    "candidate_port_match_score",
    "candidate_technology_match_score",
    "candidate_scanner_signal_score",
]

LEAKAGE_FEATURES = [
    "is_ground_truth_family",
    "candidate_cve_match_score",
    "candidate_validation_available",
]

AGENTIC_FIXED_PLAYBOOK_ORDER = [
    "web_server",
    "web_framework",
    "java_web_framework",
    "java_app_server",
    "cms",
    "php_web",
    "python_web",
    "database_admin",
    "search_engine",
    "message_broker",
    "file_management",
    "admin_panel",
    "cgi",
    "unknown",
]


def load_json_array(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40, 40)))


def build_matrix(rows: list[dict], families: list[str], mean: np.ndarray | None = None, std: np.ndarray | None = None):
    numeric = np.array([[float(row.get(col, 0.0) or 0.0) for col in SAFE_NUMERIC_FEATURES] for row in rows], dtype=float)
    if mean is None:
        mean = numeric.mean(axis=0)
    if std is None:
        std = numeric.std(axis=0)
    std = np.where(std == 0, 1.0, std)
    numeric = (numeric - mean) / std

    family_index = {family: idx for idx, family in enumerate(families)}
    one_hot = np.zeros((len(rows), len(families)), dtype=float)
    for i, row in enumerate(rows):
        family = row.get("candidate_family")
        if family in family_index:
            one_hot[i, family_index[family]] = 1.0

    intercept = np.ones((len(rows), 1), dtype=float)
    return np.hstack([intercept, numeric, one_hot]), mean, std


def train_logistic(X: np.ndarray, y: np.ndarray, epochs: int = 900, lr: float = 0.08, l2: float = 0.01) -> np.ndarray:
    weights = np.zeros(X.shape[1], dtype=float)
    positives = max(float(y.sum()), 1.0)
    negatives = max(float(len(y) - y.sum()), 1.0)
    sample_weight = np.where(y == 1, len(y) / (2.0 * positives), len(y) / (2.0 * negatives))

    for _ in range(epochs):
        pred = sigmoid(X @ weights)
        error = (pred - y) * sample_weight
        grad = (X.T @ error) / len(y)
        grad[1:] += l2 * weights[1:]
        weights -= lr * grad
    return weights


def hit_at_k(rows: list[dict], score_key: str, k: int) -> float:
    hits = []
    for _, group in group_by_target(rows).items():
        positives = [row for row in group if row["is_positive"]]
        if not positives:
            continue
        top = sorted(group, key=lambda row: row[score_key], reverse=True)[:k]
        hits.append(1.0 if any(row["is_positive"] for row in top) else 0.0)
    return float(sum(hits) / len(hits)) if hits else 0.0


def mean_reciprocal_rank(rows: list[dict], score_key: str) -> float:
    rr = []
    for _, group in group_by_target(rows).items():
        if not any(row["is_positive"] for row in group):
            continue
        ranked = sorted(group, key=lambda row: row[score_key], reverse=True)
        for idx, row in enumerate(ranked, start=1):
            if row["is_positive"]:
                rr.append(1.0 / idx)
                break
    return float(sum(rr) / len(rr)) if rr else 0.0


def expected_random_hit_at_k(rows: list[dict], k: int) -> float:
    probs = []
    for _, group in group_by_target(rows).items():
        positives = sum(1 for row in group if row["is_positive"])
        if positives == 0:
            continue
        total = len(group)
        if k >= total:
            probs.append(1.0)
        else:
            miss = math.comb(total - positives, k) / math.comb(total, k)
            probs.append(1.0 - miss)
    return float(sum(probs) / len(probs)) if probs else 0.0


def group_by_target(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["target_id"]].append(row)
    return groups


def heuristic_score(row: dict) -> float:
    return (
        1.20 * float(row.get("candidate_scanner_signal_score", 0.0) or 0.0)
        + 1.00 * float(row.get("candidate_product_match_score", 0.0) or 0.0)
        + 0.80 * float(row.get("candidate_service_match_score", 0.0) or 0.0)
        + 0.65 * float(row.get("candidate_technology_match_score", 0.0) or 0.0)
        + 0.35 * float(row.get("candidate_port_match_score", 0.0) or 0.0)
    )


def fixed_playbook_score(row: dict) -> float:
    family = row.get("candidate_family")
    try:
        return float(-AGENTIC_FIXED_PLAYBOOK_ORDER.index(family))
    except ValueError:
        return float(-len(AGENTIC_FIXED_PLAYBOOK_ORDER))


def attempts_to_first_positive(rows: list[dict], score_key: str) -> dict:
    attempts = []
    missed_targets = []
    for target_id, group in group_by_target(rows).items():
        if not any(row["is_positive"] for row in group):
            continue
        ranked = sorted(group, key=lambda row: row[score_key], reverse=True)
        for idx, row in enumerate(ranked, start=1):
            if row["is_positive"]:
                attempts.append(float(idx))
                break
        else:
            missed_targets.append(target_id)
    if not attempts:
        return {"mean": None, "median": None, "max": None, "evaluated_targets": 0, "missed_targets": missed_targets}
    ordered = sorted(attempts)
    mid = len(ordered) // 2
    median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2.0
    return {
        "mean": float(sum(attempts) / len(attempts)),
        "median": float(median),
        "max": float(max(attempts)),
        "evaluated_targets": len(attempts),
        "missed_targets": missed_targets,
    }


def expected_random_attempts(rows: list[dict]) -> dict:
    values = []
    for _, group in group_by_target(rows).items():
        positives = sum(1 for row in group if row["is_positive"])
        if positives == 0:
            continue
        total = len(group)
        values.append((total + 1.0) / (positives + 1.0))
    if not values:
        return {"mean": None, "median": None, "max": None, "evaluated_targets": 0}
    ordered = sorted(values)
    mid = len(ordered) // 2
    median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2.0
    return {
        "mean": float(sum(values) / len(values)),
        "median": float(median),
        "max": float(max(values)),
        "evaluated_targets": len(values),
    }


def precision_recall_at_threshold(rows: list[dict], score_key: str, threshold: float = 0.5) -> dict:
    tp = fp = tn = fn = 0
    for row in rows:
        pred = row[score_key] >= threshold
        actual = bool(row["is_positive"])
        if pred and actual:
            tp += 1
        elif pred and not actual:
            fp += 1
        elif not pred and actual:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Dec target-candidate exploit ranking.")
    parser.add_argument("--dataset-root", default="generated/dec-vulhub-2026-08-24-fixed-core")
    parser.add_argument("--output-dir", default="generated/dec-vulhub-2026-08-24-fixed-core/reports")
    args = parser.parse_args()

    root = Path(args.dataset_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    feature_rows = load_json_array(root / "derived" / "target-candidate-features.json")
    label_rows = load_jsonl(root / "labels" / "target-candidate-labels.jsonl")
    label_by_key = {(row["target_id"], row["candidate_family"]): row for row in label_rows}

    rows = []
    for row in feature_rows:
        label = label_by_key.get((row["target_id"], row["candidate_family"]), {}).get("label", "missing")
        merged = dict(row)
        merged["label"] = label
        merged["is_positive"] = label == "positive_family_match"
        merged["heuristic_score"] = heuristic_score(row)
        merged["agentic_fixed_playbook_score"] = fixed_playbook_score(row)
        rows.append(merged)

    families = sorted({row["candidate_family"] for row in rows})
    targets = sorted({row["target_id"] for row in rows})
    predictions: list[dict] = []

    for held_out_target in targets:
        train_rows = [row for row in rows if row["target_id"] != held_out_target]
        test_rows = [row for row in rows if row["target_id"] == held_out_target]
        X_train, mean, std = build_matrix(train_rows, families)
        y_train = np.array([1.0 if row["is_positive"] else 0.0 for row in train_rows], dtype=float)
        X_test, _, _ = build_matrix(test_rows, families, mean=mean, std=std)
        weights = train_logistic(X_train, y_train)
        probs = sigmoid(X_test @ weights)
        for row, prob in zip(test_rows, probs):
            out = {
                "target_id": row["target_id"],
                "candidate_family": row["candidate_family"],
                "label": row["label"],
                "is_positive": row["is_positive"],
                "ml_probability": float(prob),
                "heuristic_score": float(row["heuristic_score"]),
                "agentic_fixed_playbook_score": float(row["agentic_fixed_playbook_score"]),
                "leakage_fields_present": {field: row.get(field) for field in LEAKAGE_FEATURES},
            }
            predictions.append(out)

    for target_id, group in group_by_target(predictions).items():
        for score_key in ["ml_probability", "heuristic_score", "agentic_fixed_playbook_score"]:
            ranked = sorted(group, key=lambda row: row[score_key], reverse=True)
            for rank, row in enumerate(ranked, start=1):
                row[f"{score_key}_rank"] = rank

    failures = []
    per_target = []
    for target_id, group in group_by_target(predictions).items():
        positives = [row for row in group if row["is_positive"]]
        ml_top = sorted(group, key=lambda row: row["ml_probability"], reverse=True)[:5]
        heuristic_top = sorted(group, key=lambda row: row["heuristic_score"], reverse=True)[:5]
        best_positive_rank = None
        if positives:
            best_positive_rank = min(row["ml_probability_rank"] for row in positives)
        item = {
            "target_id": target_id,
            "positive_families": [row["candidate_family"] for row in positives],
            "best_positive_ml_rank": best_positive_rank,
            "ml_top5": [
                {
                    "candidate_family": row["candidate_family"],
                    "probability": row["ml_probability"],
                    "label": row["label"],
                }
                for row in ml_top
            ],
            "heuristic_top5": [
                {
                    "candidate_family": row["candidate_family"],
                    "score": row["heuristic_score"],
                    "label": row["label"],
                }
                for row in heuristic_top
            ],
        }
        per_target.append(item)
        if positives and best_positive_rank and best_positive_rank > 3:
            failures.append(item)

    metrics = {
        "task": "ทดสอบว่า ML เรียง candidate exploit family ต่อ target ได้ดีกว่าสุ่มหรือไม่",
        "dataset_root": str(root),
        "rows": len(rows),
        "targets": len(targets),
        "candidate_families": len(families),
        "label_counts": dict(Counter(row["label"] for row in rows)),
        "validation": "Leave-One-Target-Out; ทดสอบ target ที่ model ไม่เห็นตอน train",
        "safe_features_used": SAFE_NUMERIC_FEATURES + ["candidate_family(one-hot)"],
        "excluded_leakage_features": LEAKAGE_FEATURES,
        "ml": {
            "top1_hit_rate": hit_at_k(predictions, "ml_probability", 1),
            "top3_hit_rate": hit_at_k(predictions, "ml_probability", 3),
            "top5_hit_rate": hit_at_k(predictions, "ml_probability", 5),
            "mrr": mean_reciprocal_rank(predictions, "ml_probability"),
            "classification_at_0_5": precision_recall_at_threshold(predictions, "ml_probability", 0.5),
        },
        "heuristic": {
            "top1_hit_rate": hit_at_k(predictions, "heuristic_score", 1),
            "top3_hit_rate": hit_at_k(predictions, "heuristic_score", 3),
            "top5_hit_rate": hit_at_k(predictions, "heuristic_score", 5),
            "mrr": mean_reciprocal_rank(predictions, "heuristic_score"),
        },
        "random_expected": {
            "top1_hit_rate": expected_random_hit_at_k(predictions, 1),
            "top3_hit_rate": expected_random_hit_at_k(predictions, 3),
            "top5_hit_rate": expected_random_hit_at_k(predictions, 5),
        },
        "ml_vs_agentic_efficiency": {
            "metric": "attempts_to_first_positive_candidate; lower is better",
            "ml_ranker": attempts_to_first_positive(predictions, "ml_probability"),
            "agentic_scanner_heuristic": attempts_to_first_positive(predictions, "heuristic_score"),
            "agentic_fixed_playbook": attempts_to_first_positive(predictions, "agentic_fixed_playbook_score"),
            "agentic_random_expected": expected_random_attempts(predictions),
            "interpretation": "agentic_scanner_heuristic คือ agent ที่อ่าน scanner evidence แล้วจัดลำดับด้วย rule; fixed_playbook คือ agent ที่ไล่ family ตาม playbook เดิมโดยไม่เรียนจากข้อมูล",
        },
        "failure_case_count_top3": len(failures),
        "warnings": [
            "label เป็น positive_family_match จาก family/lab identity จึงยังเป็น weak label ไม่ใช่ exploit success ทุกแถว",
            "ผลนี้ใช้ทดสอบ ranking เบื้องต้น ไม่ใช่ final model validation",
            "ห้ามใช้ is_ground_truth_family, candidate_cve_match_score, candidate_validation_available เป็น input หลัก เพราะเสี่ยง label leakage",
        ],
    }

    (output_dir / "dec-ml-ranking-metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "dec-ml-ranking-predictions.json").write_text(json.dumps(predictions, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "dec-ml-ranking-failures.json").write_text(json.dumps(failures, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "dec-ml-vs-agentic-comparison.json").write_text(
        json.dumps(metrics["ml_vs_agentic_efficiency"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = [
        "# รายงานทดสอบ ML Ranking ของ Dec",
        "",
        "เป้าหมายคือทดสอบว่า model ช่วยเรียง candidate exploit family ได้ดีกว่าการสุ่มหรือไล่ทีละตัวหรือไม่",
        "",
        "## Dataset",
        "",
        f"- rows: {metrics['rows']}",
        f"- targets: {metrics['targets']}",
        f"- candidate families: {metrics['candidate_families']}",
        f"- label counts: `{json.dumps(metrics['label_counts'], ensure_ascii=False)}`",
        "",
        "## Feature ที่ใช้",
        "",
        "ใช้เฉพาะ feature ที่ไม่เฉลยคำตอบตรง ๆ:",
        "",
    ]
    lines.extend([f"- `{name}`" for name in metrics["safe_features_used"]])
    lines.extend([
        "",
        "feature ที่ตั้งใจไม่ใช้:",
        "",
    ])
    lines.extend([f"- `{name}`" for name in LEAKAGE_FEATURES])
    lines.extend([
        "",
        "## ผลเทียบกับ baseline",
        "",
        "| Method | Top-1 hit | Top-3 hit | Top-5 hit | MRR |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| ML logistic ranker | {metrics['ml']['top1_hit_rate']:.3f} | {metrics['ml']['top3_hit_rate']:.3f} | {metrics['ml']['top5_hit_rate']:.3f} | {metrics['ml']['mrr']:.3f} |",
        f"| Heuristic weighted score | {metrics['heuristic']['top1_hit_rate']:.3f} | {metrics['heuristic']['top3_hit_rate']:.3f} | {metrics['heuristic']['top5_hit_rate']:.3f} | {metrics['heuristic']['mrr']:.3f} |",
        f"| Random expected | {metrics['random_expected']['top1_hit_rate']:.3f} | {metrics['random_expected']['top3_hit_rate']:.3f} | {metrics['random_expected']['top5_hit_rate']:.3f} | n/a |",
        "",
        "## ML vs Agentic",
        "",
        "ตารางนี้วัดจำนวน attempt เฉลี่ยจนเจอ candidate family ที่เป็น positive ยิ่งน้อยยิ่งดี",
        "",
        "| วิธี | mean attempts | median | max | ความหมาย |",
        "| --- | ---: | ---: | ---: | --- |",
        f"| ML logistic ranker | {metrics['ml_vs_agentic_efficiency']['ml_ranker']['mean']:.3f} | {metrics['ml_vs_agentic_efficiency']['ml_ranker']['median']:.3f} | {metrics['ml_vs_agentic_efficiency']['ml_ranker']['max']:.3f} | model เรียงจากข้อมูล train แบบ leave-one-target-out |",
        f"| Agentic scanner heuristic | {metrics['ml_vs_agentic_efficiency']['agentic_scanner_heuristic']['mean']:.3f} | {metrics['ml_vs_agentic_efficiency']['agentic_scanner_heuristic']['median']:.3f} | {metrics['ml_vs_agentic_efficiency']['agentic_scanner_heuristic']['max']:.3f} | agent ใช้ scanner evidence/rule จัดลำดับเอง |",
        f"| Agentic fixed playbook | {metrics['ml_vs_agentic_efficiency']['agentic_fixed_playbook']['mean']:.3f} | {metrics['ml_vs_agentic_efficiency']['agentic_fixed_playbook']['median']:.3f} | {metrics['ml_vs_agentic_efficiency']['agentic_fixed_playbook']['max']:.3f} | agent ไล่ family ตาม playbook คงที่ |",
        f"| Agentic random expected | {metrics['ml_vs_agentic_efficiency']['agentic_random_expected']['mean']:.3f} | {metrics['ml_vs_agentic_efficiency']['agentic_random_expected']['median']:.3f} | {metrics['ml_vs_agentic_efficiency']['agentic_random_expected']['max']:.3f} | agent ลองสุ่มจนเจอ |",
        "",
        "คำอ่านผล: บน feature ชุดนี้ ML และ agentic scanner heuristic มีประสิทธิภาพเท่ากัน เพราะ scanner-derived match score ชี้ family ถูกชัดมาก ส่วน agentic fixed playbook/random แพ้ด้านจำนวน attempt",
        "",
        "## คำวินิจฉัยเบื้องต้น",
        "",
        "ผลรอบนี้ดีมากจนควรมองเป็น red flag มากกว่าชัยชนะสุดท้าย เพราะ ML และ heuristic ได้ Top-1 เท่ากันที่ 1.000 แปลว่า feature กลุ่ม `candidate_*_match_score` น่าจะมี signal ที่ใกล้กับ family label มากอยู่แล้ว",
        "",
        "สรุปคือ model เรียงถูกบน dataset นี้ แต่ยังตอบไม่ได้เต็มที่ว่า generalize ไป target ใหม่จริงหรือไม่ ต้องทดสอบรอบถัดไปด้วย feature ที่อ่อนลง, negative controls, และ exploit validation จริง",
        "",
        "## จุดที่ model ยังพลาด",
        "",
    ])
    if failures:
        for failure in failures[:20]:
            top = ", ".join(f"{row['candidate_family']}({row['label']})" for row in failure["ml_top5"][:3])
            positives = ", ".join(failure["positive_families"])
            lines.append(f"- `{failure['target_id']}` positive=`{positives}` แต่ positive อันดับแรกอยู่ rank {failure['best_positive_ml_rank']}; top3={top}")
    else:
        lines.append("- ไม่พบ target ที่ positive หลุดเกิน Top-3 ในรอบนี้")
    lines.extend([
        "",
        "## ข้อควรระวัง",
        "",
        "- label ยังเป็น weak label จาก family/lab identity ไม่ใช่ exploit success ทุกแถว",
        "- metric สูงไม่ได้แปลว่า exploit ได้จริง ต้อง validate ด้วย manual PoC/Metasploit/sqlmap เพิ่ม",
        "- ขั้นถัดไปควรเพิ่ม positive/negative controls และวัดกับ target ใหม่จาก Kali",
    ])
    (output_dir / "dec-ml-ranking-report-th.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
