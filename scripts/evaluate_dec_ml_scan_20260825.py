from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


FAMILY_HINTS = {
    "adminer": {"aliases": ["adminer"], "ports": [8080]},
    "aria2": {"aliases": ["aria2", "json-rpc"], "ports": [6800]},
    "appweb": {"aliases": ["appweb"], "ports": [8080]},
    "couchdb": {"aliases": ["couchdb", "erlang otp"], "ports": [5984]},
    "druid": {"aliases": ["druid", "apache druid"], "ports": [8888]},
    "drupal": {"aliases": ["drupal"], "ports": [8080]},
    "elasticsearch": {"aliases": ["elasticsearch", "elastic"], "ports": [9200, 18108]},
    "flask": {"aliases": ["flask", "werkzeug", "gunicorn"], "ports": [5000, 8000]},
    "goahead": {"aliases": ["goahead"], "ports": [8080]},
    "gogs": {"aliases": ["gogs"], "ports": [3000]},
    "grafana": {"aliases": ["grafana"], "ports": [3000]},
    "jenkins": {"aliases": ["jenkins"], "ports": [8080]},
    "jetty": {"aliases": ["jetty"], "ports": [8080]},
    "joomla": {"aliases": ["joomla"], "ports": [80, 8080]},
    "nextjs": {"aliases": ["nextjs", "next.js", "next"], "ports": [3000]},
    "nexus": {"aliases": ["nexus", "sonatype"], "ports": [8081]},
    "nginx": {"aliases": ["nginx"], "ports": [80, 8080]},
    "phpmyadmin": {"aliases": ["phpmyadmin", "phpmyadmin", "access denied"], "ports": [8080]},
    "rails": {"aliases": ["rails", "ruby on rails"], "ports": [3000]},
    "redis": {"aliases": ["redis"], "ports": [6379]},
    "shiro": {"aliases": ["shiro"], "ports": [8080]},
    "solr": {"aliases": ["solr"], "ports": [8983]},
    "spring": {"aliases": ["spring", "tomcat"], "ports": [8080]},
    "struts2": {"aliases": ["struts", "struts2"], "ports": [8080]},
    "thinkphp": {"aliases": ["thinkphp"], "ports": [8080]},
    "tomcat": {"aliases": ["tomcat", "catalina"], "ports": [8080]},
    "webmin": {"aliases": ["webmin", "miniserv"], "ports": [10000]},
}

PROFILES = {
    "current": {
        "features": [
            "title_alias_score",
            "server_alias_score",
            "nmap_alias_score",
            "body_alias_score",
            "port_score",
            "protocol_score",
            "http_tool_score",
        ],
        "description": "ใช้ scanner fingerprint หลักทั้งหมด: title/server/nmap/body/protocol/port/tool coverage",
    },
    "no_body_text": {
        "features": [
            "title_alias_score",
            "server_alias_score",
            "nmap_alias_score",
            "port_score",
            "protocol_score",
            "http_tool_score",
        ],
        "description": "ตัด body/probe text ออก เหลือเฉพาะ metadata ที่มักนิ่งกว่า",
    },
    "port_protocol_only": {
        "features": ["port_score", "protocol_score"],
        "description": "ใช้แค่ port/protocol เพื่อดู baseline ที่หยาบมากและเสี่ยงชนกัน",
    },
    "text_only": {
        "features": ["title_alias_score", "server_alias_score", "nmap_alias_score", "body_alias_score"],
        "description": "ใช้เฉพาะคำจาก scanner evidence ไม่ใช้ port",
    },
}

LEAKAGE_FIELDS = ["target_id", "candidate_family", "positive_family", "CVE in target_id"]
VALIDATED_POSITIVE = {"validated", "validated_positive"}
VALIDATED_NEGATIVE = {"validated_negative"}


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def load_weak_labels(experiment_dir: Path) -> list[dict]:
    labels = load_jsonl(experiment_dir / "labels-draft.jsonl")
    for row in labels:
        row["label_mode_source"] = "weak"
    return labels


def load_validated_label_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        if path.suffix.lower() == ".csv":
            return list(csv.DictReader(handle))
    return load_jsonl(path)


def load_effective_labels(experiment_dir: Path, validated_labels: Path, label_mode: str) -> tuple[list[dict], dict]:
    weak_labels = load_weak_labels(experiment_dir)
    weak_by_target = {row["target_id"]: row for row in weak_labels}
    validation_rows = load_validated_label_rows(validated_labels)
    validation_by_target = {row["target_id"]: row for row in validation_rows}

    if label_mode == "weak":
        return weak_labels, {
            "label_mode": label_mode,
            "weak_label_rows": len(weak_labels),
            "validated_label_rows": len(validation_rows),
            "effective_label_rows": len(weak_labels),
        }

    effective = []
    skipped = []
    for target_id, validation in validation_by_target.items():
        status = str(validation.get("validation_status", ""))
        strength = str(validation.get("label_strength", ""))
        is_validated_positive = status == "validated_positive" or strength in VALIDATED_POSITIVE
        is_validated_negative = status == "validated_negative" or strength in VALIDATED_NEGATIVE
        if is_validated_positive:
            effective.append(
                {
                    "target_id": target_id,
                    "positive_family": validation.get("weak_label", ""),
                    "label_source": "validated_positive",
                    "label_strength": strength or "validated",
                    "label_mode_source": "validated",
                }
            )
        elif is_validated_negative:
            skipped.append(target_id)

    if label_mode == "validated":
        return effective, {
            "label_mode": label_mode,
            "weak_label_rows": len(weak_labels),
            "validated_label_rows": len(validation_rows),
            "effective_label_rows": len(effective),
            "skipped_validated_negative_or_without_positive": skipped,
        }

    if label_mode != "merged":
        raise ValueError(f"unsupported label_mode={label_mode!r}")

    effective_by_target = {row["target_id"]: row for row in effective}
    for target_id, weak in weak_by_target.items():
        if target_id in effective_by_target or target_id in skipped:
            continue
        merged = dict(weak)
        merged["label_mode_source"] = "weak_fallback"
        effective_by_target[target_id] = merged
    labels = [effective_by_target[target_id] for target_id in sorted(effective_by_target)]
    return labels, {
        "label_mode": label_mode,
        "weak_label_rows": len(weak_labels),
        "validated_label_rows": len(validation_rows),
        "effective_label_rows": len(labels),
        "validated_positive_rows": len(effective),
        "skipped_validated_negative_or_without_positive": skipped,
    }


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def text_value(row: dict, *keys: str) -> str:
    return " ".join(str(row.get(key, "") or "") for key in keys).lower()


def alias_score(text: str, aliases: list[str]) -> float:
    if not text:
        return 0.0
    hits = sum(1 for alias in aliases if alias and alias.lower() in text)
    return min(1.0, hits / max(len(aliases), 1))


def as_int(value: object) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(float(str(value)))
    except ValueError:
        return None


def candidate_features(target: dict, family: str) -> dict:
    hints = FAMILY_HINTS.get(family, {"aliases": [family], "ports": []})
    aliases = hints["aliases"]
    port = as_int(target.get("port"))
    protocol = str(target.get("protocol_kind", "") or "").lower()
    title = text_value(target, "title")
    server = text_value(target, "server", "x_powered_by")
    nmap = text_value(target, "nmap_service_line")
    body = text_value(target, "http_status")

    title_alias = alias_score(title, aliases)
    server_alias = alias_score(server, aliases)
    nmap_alias = alias_score(nmap, aliases)
    body_alias = alias_score(body, aliases)
    port_score = 1.0 if port is not None and port in set(hints.get("ports", [])) else 0.0
    protocol_score = 0.0
    if protocol == "nonhttp" and family in {"redis", "aria2"}:
        protocol_score = 1.0
    elif protocol == "http" and family not in {"redis", "aria2"}:
        protocol_score = 0.25

    http_tool_score = 0.0
    if family not in {"redis", "aria2"}:
        http_tool_score = 0.15 * truthy(target.get("has_probe"))
        http_tool_score += 0.10 * truthy(target.get("has_nikto"))
        http_tool_score += 0.10 * truthy(target.get("has_wapiti"))

    score = (
        2.5 * title_alias
        + 2.0 * server_alias
        + 2.0 * nmap_alias
        + 1.2 * body_alias
        + 0.7 * port_score
        + 0.6 * protocol_score
        + http_tool_score
    )
    return {
        "title_alias_score": title_alias,
        "server_alias_score": server_alias,
        "nmap_alias_score": nmap_alias,
        "body_alias_score": body_alias,
        "port_score": port_score,
        "protocol_score": protocol_score,
        "http_tool_score": http_tool_score,
        "heuristic_score": score,
    }


def build_candidate_rows(features: list[dict], labels: list[dict]) -> list[dict]:
    label_by_target = {row["target_id"]: row["positive_family"] for row in labels}
    families = sorted({row["positive_family"] for row in labels})
    rows = []
    for target in features:
        target_id = target["target_id"]
        if target_id not in label_by_target:
            continue
        positive = label_by_target[target_id]
        for family in families:
            row = {
                "target_id": target_id,
                "candidate_family": family,
                "positive_family": positive,
                "is_positive": family == positive,
            }
            row.update(candidate_features(target, family))
            rows.append(row)
    return rows


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40, 40)))


def build_matrix(rows: list[dict], feature_names: list[str], mean: np.ndarray | None = None, std: np.ndarray | None = None):
    values = np.array([[float(row.get(name, 0.0) or 0.0) for name in feature_names] for row in rows], dtype=float)
    if mean is None:
        mean = values.mean(axis=0)
    if std is None:
        std = values.std(axis=0)
    std = np.where(std == 0, 1.0, std)
    values = (values - mean) / std
    return np.hstack([np.ones((len(rows), 1), dtype=float), values]), mean, std


def train_logistic(X: np.ndarray, y: np.ndarray, epochs: int = 700, lr: float = 0.08, l2: float = 0.02) -> np.ndarray:
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


def group_by_target(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["target_id"]].append(row)
    return groups


def evaluate_ml(rows: list[dict], feature_names: list[str], score_key: str) -> list[dict]:
    output = [dict(row) for row in rows]
    targets = sorted(group_by_target(rows))
    by_key = {(row["target_id"], row["candidate_family"]): row for row in output}
    for target_id in targets:
        train_rows = [row for row in rows if row["target_id"] != target_id]
        test_rows = [row for row in rows if row["target_id"] == target_id]
        X_train, mean, std = build_matrix(train_rows, feature_names)
        y_train = np.array([1.0 if row["is_positive"] else 0.0 for row in train_rows], dtype=float)
        weights = train_logistic(X_train, y_train)
        X_test, _, _ = build_matrix(test_rows, feature_names, mean, std)
        probabilities = sigmoid(X_test @ weights)
        for row, probability in zip(test_rows, probabilities):
            by_key[(row["target_id"], row["candidate_family"])][score_key] = float(probability)
    return output


def hit_at_k(rows: list[dict], score_key: str, k: int) -> float:
    hits = []
    for group in group_by_target(rows).values():
        ranked = sorted(group, key=lambda row: row[score_key], reverse=True)[:k]
        hits.append(1.0 if any(row["is_positive"] for row in ranked) else 0.0)
    return sum(hits) / len(hits) if hits else 0.0


def mrr(rows: list[dict], score_key: str) -> float:
    values = []
    for group in group_by_target(rows).values():
        ranked = sorted(group, key=lambda row: row[score_key], reverse=True)
        for index, row in enumerate(ranked, start=1):
            if row["is_positive"]:
                values.append(1.0 / index)
                break
    return sum(values) / len(values) if values else 0.0


def attempts(rows: list[dict], score_key: str) -> dict:
    values = []
    for group in group_by_target(rows).values():
        ranked = sorted(group, key=lambda row: row[score_key], reverse=True)
        for index, row in enumerate(ranked, start=1):
            if row["is_positive"]:
                values.append(float(index))
                break
    ordered = sorted(values)
    mid = len(ordered) // 2
    median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2.0
    return {"mean": sum(values) / len(values), "median": median, "max": max(values), "evaluated_targets": len(values)}


def expected_random_hit(rows: list[dict], k: int) -> float:
    probabilities = []
    for group in group_by_target(rows).values():
        total = len(group)
        positives = sum(1 for row in group if row["is_positive"])
        miss = math.comb(total - positives, k) / math.comb(total, k) if k < total else 0.0
        probabilities.append(1.0 - miss)
    return sum(probabilities) / len(probabilities) if probabilities else 0.0


def expected_random_attempts(rows: list[dict]) -> dict:
    values = []
    for group in group_by_target(rows).values():
        total = len(group)
        positives = sum(1 for row in group if row["is_positive"])
        values.append((total + 1.0) / (positives + 1.0))
    ordered = sorted(values)
    mid = len(ordered) // 2
    median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2.0
    return {"mean": sum(values) / len(values), "median": median, "max": max(values), "evaluated_targets": len(values)}


def summarize(rows: list[dict], score_key: str) -> dict:
    return {
        "top1_hit_rate": hit_at_k(rows, score_key, 1),
        "top3_hit_rate": hit_at_k(rows, score_key, 3),
        "top5_hit_rate": hit_at_k(rows, score_key, 5),
        "mrr": mrr(rows, score_key),
        "attempts_to_first_positive": attempts(rows, score_key),
    }


def rank_rows(rows: list[dict], score_key: str) -> None:
    for group in group_by_target(rows).values():
        ranked = sorted(group, key=lambda row: row[score_key], reverse=True)
        for rank, row in enumerate(ranked, start=1):
            row[f"{score_key}_rank"] = rank


def format_float(value: float) -> str:
    return f"{value:.3f}"


def write_report(output_dir: Path, metrics: dict, failures: list[dict], report_prefix: str) -> None:
    lines = [
        "# รายงานทดสอบ ML จากผลสแกน Kali 29 Targets",
        "",
        "รายงานนี้ใช้ชุด `experiments/dec-ml-scan-2026-08-25/` เพื่อทดสอบว่า feature ที่ได้จาก scanner/fingerprint ช่วยเรียงลำดับ candidate family ได้ถูกต้องแค่ไหน",
        "",
        "สิ่งสำคัญ: นี่ไม่ใช่การยืนยันว่า exploit สำเร็จ แต่เป็นการวัดว่า evidence จาก scanner พาเราไปหา family ที่ตรงกับ weak label ได้เร็วขึ้นหรือไม่",
        "",
        "## Dataset",
        "",
        f"- target records: {metrics['targets']}",
        f"- candidate rows: {metrics['candidate_rows']}",
        f"- candidate families: {metrics['candidate_families']}",
        f"- label counts: `{json.dumps(metrics['label_counts'], ensure_ascii=False)}`",
        f"- label mode: `{metrics['label_metadata']['label_mode']}`",
        f"- effective label rows: {metrics['label_metadata']['effective_label_rows']}",
        "",
        "## Input ที่ใช้ทดสอบ",
        "",
        "ใช้ข้อมูลจาก scanner/fingerprint เท่านั้น เช่น `title`, `server`, `x_powered_by`, `nmap_service_line`, `port`, `protocol_kind`, และ flag ว่ามี output จาก tool ไหนบ้าง",
        "",
        "ไม่ใช้ field ที่เฉลยคำตอบโดยตรง:",
        "",
    ]
    lines.extend([f"- `{field}`" for field in metrics["excluded_leakage_fields"]])
    lines.extend([
        "",
        "## ผลเทียบ Baseline",
        "",
        "| วิธี | Top-1 | Top-3 | Top-5 | MRR | mean attempts |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        f"| ML logistic ranker | {format_float(metrics['ml']['top1_hit_rate'])} | {format_float(metrics['ml']['top3_hit_rate'])} | {format_float(metrics['ml']['top5_hit_rate'])} | {format_float(metrics['ml']['mrr'])} | {format_float(metrics['ml']['attempts_to_first_positive']['mean'])} |",
        f"| Scanner heuristic | {format_float(metrics['heuristic']['top1_hit_rate'])} | {format_float(metrics['heuristic']['top3_hit_rate'])} | {format_float(metrics['heuristic']['top5_hit_rate'])} | {format_float(metrics['heuristic']['mrr'])} | {format_float(metrics['heuristic']['attempts_to_first_positive']['mean'])} |",
        f"| Random expected | {format_float(metrics['random_expected']['top1_hit_rate'])} | {format_float(metrics['random_expected']['top3_hit_rate'])} | {format_float(metrics['random_expected']['top5_hit_rate'])} | n/a | {format_float(metrics['random_expected']['attempts_to_first_positive']['mean'])} |",
        "",
        "คำอ่าน: ถ้า Top-1 สูง แปลว่าโมเดล/heuristic เลือก family แรกถูกบ่อย ถ้า mean attempts ต่ำ แปลว่าต้องลอง candidate น้อยก่อนเจอตัวที่ถูก",
        "",
        "## Feature Ablation",
        "",
        "| Profile | Top-1 | Top-3 | mean attempts | ความหมาย |",
        "| --- | ---: | ---: | ---: | --- |",
    ])
    for name, result in metrics["feature_ablation"].items():
        lines.append(
            f"| `{name}` | {format_float(result['top1_hit_rate'])} | {format_float(result['top3_hit_rate'])} | {format_float(result['attempts_to_first_positive']['mean'])} | {result['description']} |"
        )
    lines.extend([
        "",
        "## จุดที่พลาดหรือเสี่ยง",
        "",
    ])
    if failures:
        for item in failures:
            top3 = ", ".join(f"{row['candidate_family']}#{row['rank']}" for row in item["ml_top3"])
            lines.append(
                f"- `{item['target_id']}` label=`{item['positive_family']}` แต่ ML วาง positive ไว้อันดับ {item['positive_rank']}; top3={top3}"
            )
    else:
        lines.append("- ไม่พบ target ที่ positive หลุดเกิน Top-3 ในรอบนี้")
    lines.extend([
        "",
        "## สรุปสำหรับโปรเจกต์",
        "",
        "- การเพิ่มผล scan มีผลจริง เพราะทำให้เราเห็นว่า fingerprint แบบไหนช่วย/ไม่ช่วยแยก family",
        "- ค่าคะแนนที่ดีมากยังต้องระวัง เพราะ label ยังมาจากชื่อ lab/folder ของ Vulhub ไม่ใช่ exploit success",
        "- สิ่งที่ควรทำต่อคือเพิ่ม negative controls และทำ exploit validation เฉพาะ target ที่มี PoC ชัด เช่น Joomla, Grafana, Redis, Aria2, ThinkPHP",
    ])
    (output_dir / f"{report_prefix}-report-th.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_candidate_feature_tables(derived_dir: Path, rows: list[dict], label_mode: str) -> None:
    derived_dir.mkdir(parents=True, exist_ok=True)
    feature_names = [
        "title_alias_score",
        "server_alias_score",
        "nmap_alias_score",
        "body_alias_score",
        "port_score",
        "protocol_score",
        "http_tool_score",
        "heuristic_score",
    ]
    fieldnames = ["target_id", "candidate_family", "positive_family", "label", *feature_names]
    export_rows = []
    for row in rows:
        export_row = {
            "target_id": row["target_id"],
            "candidate_family": row["candidate_family"],
            "positive_family": row["positive_family"],
            "label": "positive_family_match" if row["is_positive"] else "negative_family",
        }
        export_row.update({name: float(row.get(name, 0.0) or 0.0) for name in feature_names})
        export_rows.append(export_row)

    suffix = "" if label_mode == "weak" else f"-{label_mode}"
    with (derived_dir / f"candidate-family-features{suffix}.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(export_rows)
    with (derived_dir / f"candidate-family-features{suffix}.jsonl").open("w", encoding="utf-8") as handle:
        for row in export_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate target-level Dec ML scan fingerprints.")
    parser.add_argument("--experiment-dir", default="experiments/dec-ml-scan-2026-08-25")
    parser.add_argument("--output-dir", default="experiments/dec-ml-scan-2026-08-25/reports")
    parser.add_argument("--label-mode", choices=["weak", "validated", "merged"], default="weak")
    parser.add_argument(
        "--validated-labels",
        default="experiments/dec-ml-scan-2026-08-25/derived/validated-labels.csv",
        help="CSV/JSONL produced by scripts/import_dec_validation_results.py",
    )
    parser.add_argument(
        "--derived-output-dir",
        default=None,
        help="Where candidate-family feature tables are written; defaults to <experiment-dir>/derived",
    )
    args = parser.parse_args()

    experiment_dir = Path(args.experiment_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with (experiment_dir / "features.csv").open(encoding="utf-8", newline="") as handle:
        target_features = list(csv.DictReader(handle))
    labels, label_metadata = load_effective_labels(experiment_dir, Path(args.validated_labels), args.label_mode)
    if not labels:
        raise ValueError(f"no effective labels available for label_mode={args.label_mode!r}")
    rows = build_candidate_rows(target_features, labels)
    if not rows:
        raise ValueError(f"no candidate rows available for label_mode={args.label_mode!r}")
    if len({row["target_id"] for row in rows}) < 2:
        raise ValueError(
            f"label_mode={args.label_mode!r} needs at least 2 evaluated targets for leave-one-target-out validation"
        )
    derived_output_dir = Path(args.derived_output_dir) if args.derived_output_dir else experiment_dir / "derived"
    write_candidate_feature_tables(derived_output_dir, rows, args.label_mode)

    predictions = evaluate_ml(rows, PROFILES["current"]["features"], "ml_probability")
    for row in predictions:
        row["heuristic_score"] = float(row["heuristic_score"])
    rank_rows(predictions, "ml_probability")
    rank_rows(predictions, "heuristic_score")

    profile_results = {}
    for name, profile in PROFILES.items():
        profile_rows = evaluate_ml(rows, profile["features"], f"{name}_probability")
        profile_results[name] = {
            "description": profile["description"],
            "features": profile["features"],
            **summarize(profile_rows, f"{name}_probability"),
        }

    failures = []
    per_target = []
    for target_id, group in group_by_target(predictions).items():
        ranked = sorted(group, key=lambda row: row["ml_probability"], reverse=True)
        positive = next(row for row in ranked if row["is_positive"])
        item = {
            "target_id": target_id,
            "positive_family": positive["positive_family"],
            "positive_rank": positive["ml_probability_rank"],
            "ml_top3": [
                {
                    "rank": row["ml_probability_rank"],
                    "candidate_family": row["candidate_family"],
                    "probability": row["ml_probability"],
                    "is_positive": row["is_positive"],
                }
                for row in ranked[:3]
            ],
        }
        per_target.append(item)
        if positive["ml_probability_rank"] > 3:
            failures.append(item)

    metrics = {
        "task": "ทดสอบว่า scanner-derived target fingerprints ช่วยเรียง candidate family ได้ถูกต้องหรือไม่",
        "experiment_dir": str(experiment_dir),
        "validation": "Leave-One-Target-Out logistic ranker over generated candidate-family rows",
        "label_metadata": label_metadata,
        "targets": len(target_features),
        "evaluated_targets": len({row["target_id"] for row in rows}),
        "candidate_rows": len(rows),
        "candidate_families": len({row["candidate_family"] for row in rows}),
        "label_counts": dict(Counter("positive_family_match" if row["is_positive"] else "negative_family" for row in rows)),
        "input_features": PROFILES["current"]["features"],
        "excluded_leakage_fields": LEAKAGE_FIELDS,
        "ml": summarize(predictions, "ml_probability"),
        "heuristic": summarize(predictions, "heuristic_score"),
        "random_expected": {
            "top1_hit_rate": expected_random_hit(predictions, 1),
            "top3_hit_rate": expected_random_hit(predictions, 3),
            "top5_hit_rate": expected_random_hit(predictions, 5),
            "attempts_to_first_positive": expected_random_attempts(predictions),
        },
        "feature_ablation": profile_results,
        "failure_case_count_top3": len(failures),
        "warnings": [
            "labels-draft.jsonl เป็น weak label จากชื่อ lab/folder ยังไม่ใช่ exploit-success ground truth",
            "candidate rows ถูกสร้างจาก family list เพื่อวัด ranking เท่านั้น ไม่ใช่ข้อมูล scanner ดิบโดยตรง",
            "ห้ามนำ target_id, candidate_family เดิมใน features.csv, positive_family หรือ CVE จากชื่อ target ไปเป็น input model จริง",
        ],
    }

    suffix = "" if args.label_mode == "weak" else f"-{args.label_mode}"
    report_prefix = f"dec-ml-scan-ranking{suffix}"
    (output_dir / f"{report_prefix}-metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / f"{report_prefix}-predictions.json").write_text(json.dumps(predictions, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / f"{report_prefix}-per-target.json").write_text(json.dumps(per_target, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / f"{report_prefix}-failures.json").write_text(json.dumps(failures, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(output_dir, metrics, failures, report_prefix)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
