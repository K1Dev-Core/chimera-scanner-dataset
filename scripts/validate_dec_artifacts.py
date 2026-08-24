from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXED_CORE = ROOT / "generated" / "dec-vulhub-2026-08-24-fixed-core"
ML_SCAN = ROOT / "experiments" / "dec-ml-scan-2026-08-25"


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{path}:{line_number}: invalid JSONL: {exc}") from exc
    return rows


def count_csv(path: Path) -> tuple[int, list[str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return len(rows), reader.fieldnames or []


def require(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"missing required artifact: {path.relative_to(ROOT)}")


def validate_fixed_core() -> dict:
    require(FIXED_CORE / "manifest.json")
    require(FIXED_CORE / "quality-report.json")
    manifest = load_json(FIXED_CORE / "manifest.json")
    quality = load_json(FIXED_CORE / "quality-report.json")

    targets = load_jsonl(FIXED_CORE / "records" / "targets.jsonl")
    observations = load_jsonl(FIXED_CORE / "records" / "observations.jsonl")
    findings = load_jsonl(FIXED_CORE / "records" / "findings.jsonl")
    validations = load_jsonl(FIXED_CORE / "records" / "validations.jsonl")
    labels = load_jsonl(FIXED_CORE / "labels" / "target-candidate-labels.jsonl")
    candidate_features = load_json(FIXED_CORE / "derived" / "target-candidate-features.json")

    if not quality.get("valid"):
        raise AssertionError("fixed core quality-report.json has valid=false")
    if len(targets) != 43:
        raise AssertionError(f"fixed core targets expected 43, got {len(targets)}")
    if len(candidate_features) != len(labels):
        raise AssertionError("fixed core candidate feature/label row counts differ")

    return {
        "targets": len(targets),
        "observations": len(observations),
        "findings": len(findings),
        "validations": len(validations),
        "candidate_rows": len(candidate_features),
        "manifest_keys": sorted(manifest.keys()),
    }


def validate_ml_scan() -> dict:
    require(ML_SCAN / "features.csv")
    require(ML_SCAN / "observations.jsonl")
    require(ML_SCAN / "labels-draft.jsonl")
    require(ML_SCAN / "derived" / "candidate-family-features.csv")
    require(ML_SCAN / "reports" / "dec-ml-scan-ranking-metrics.json")
    require(ML_SCAN / "validation-results.schema.json")
    require(ML_SCAN / "validation-results.example.jsonl")
    require(ML_SCAN / "validation-results.fixture.jsonl")

    feature_count, feature_cols = count_csv(ML_SCAN / "features.csv")
    candidate_count, candidate_cols = count_csv(ML_SCAN / "derived" / "candidate-family-features.csv")
    merged_count, _ = count_csv(ML_SCAN / "derived" / "candidate-family-features-merged.csv")
    observations = load_jsonl(ML_SCAN / "observations.jsonl")
    labels = load_jsonl(ML_SCAN / "labels-draft.jsonl")
    metrics = load_json(ML_SCAN / "reports" / "dec-ml-scan-ranking-metrics.json")
    merged_metrics = load_json(ML_SCAN / "reports" / "dec-ml-scan-ranking-merged-metrics.json")
    example = load_jsonl(ML_SCAN / "validation-results.example.jsonl")
    fixture = load_jsonl(ML_SCAN / "validation-results.fixture.jsonl")
    fixture_labels_count, _ = count_csv(ML_SCAN / "derived" / "fixture" / "validated-labels.csv")
    fixture_validated_metrics = load_json(ML_SCAN / "reports" / "fixture" / "dec-ml-scan-ranking-validated-metrics.json")
    fixture_merged_metrics = load_json(ML_SCAN / "reports" / "fixture" / "dec-ml-scan-ranking-merged-metrics.json")

    expected_feature_cols = {"target_id", "protocol_kind", "port", "candidate_family", "scan_success"}
    missing_feature_cols = expected_feature_cols - set(feature_cols)
    if missing_feature_cols:
        raise AssertionError(f"features.csv missing columns: {sorted(missing_feature_cols)}")
    expected_candidate_cols = {"target_id", "candidate_family", "positive_family", "label", "heuristic_score"}
    missing_candidate_cols = expected_candidate_cols - set(candidate_cols)
    if missing_candidate_cols:
        raise AssertionError(f"candidate-family-features.csv missing columns: {sorted(missing_candidate_cols)}")
    if feature_count != 29 or len(observations) != 29 or len(labels) != 29:
        raise AssertionError("ML scan expected 29 features/observations/labels")
    if candidate_count != 783 or merged_count != 783:
        raise AssertionError("ML scan expected 783 candidate rows")
    if metrics["label_metadata"]["label_mode"] != "weak":
        raise AssertionError("default ranking metrics must use weak label mode")
    if merged_metrics["label_metadata"]["label_mode"] != "merged":
        raise AssertionError("merged ranking metrics must use merged label mode")
    if not example:
        raise AssertionError("validation-results.example.jsonl must contain at least one row")
    if len(fixture) != 5 or fixture_labels_count != 5:
        raise AssertionError("validation fixture expected 5 rows")
    if fixture_validated_metrics["evaluated_targets"] != 2:
        raise AssertionError("fixture validated mode expected 2 evaluated targets")
    if fixture_merged_metrics["evaluated_targets"] != 28:
        raise AssertionError("fixture merged mode expected 28 evaluated targets")

    return {
        "target_features": feature_count,
        "observations": len(observations),
        "weak_labels": len(labels),
        "candidate_rows": candidate_count,
        "merged_candidate_rows": merged_count,
        "weak_top1": round(metrics["ml"]["top1_hit_rate"], 3),
        "merged_top1": round(merged_metrics["ml"]["top1_hit_rate"], 3),
        "fixture_rows": len(fixture),
        "fixture_validated_targets": fixture_validated_metrics["evaluated_targets"],
        "fixture_merged_targets": fixture_merged_metrics["evaluated_targets"],
    }


def main() -> None:
    summary = {
        "fixed_core": validate_fixed_core(),
        "ml_scan_2026_08_25": validate_ml_scan(),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
