from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


NUMERIC_COLS = [
    "port",
    "rank_score",
    "family_risk_prior",
    "evidence_source_count",
    "has_zap_evidence",
    "has_nuclei_evidence",
    "has_wapiti_evidence",
    "has_nikto_evidence",
    "zap_finding_count",
    "nuclei_finding_count",
    "nikto_finding_count",
    "wapiti_finding_count",
    "observed_title_count",
    "observed_tech_count",
    "service_product_count",
    "service_version_count",
]

CAT_COLS = [
    "product",
    "candidate_exploit_family",
    "observed_tech_text",
    "service_products_text",
    "service_versions_text",
    "evidence_sources_text",
]


def topk_hit_rate(predictions: pd.DataFrame, k: int) -> float:
    hits = []
    for _, group in predictions.groupby("lab_id"):
        top = group.sort_values("predicted_success_probability", ascending=False).head(k)
        hits.append(int(top["is_recommended"].max() == 1))
    return sum(hits) / len(hits) if hits else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a fast Exploit-DL baseline ranker/classifier.")
    parser.add_argument("--dataset-root", default=".", help="Path to chimera-tools-name-date-... dataset folder")
    args = parser.parse_args()

    root = Path(args.dataset_root).resolve()
    derived_dir = root / "derived"
    model_dir = root / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    data_path = derived_dir / "training_examples.csv"
    if not data_path.exists():
        raise SystemExit(f"Missing {data_path}. Run scripts/build_features.py first.")

    df = pd.read_csv(data_path)
    X = df[NUMERIC_COLS + CAT_COLS]
    y = df["is_recommended"].astype(int)
    groups = df["lab_id"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_COLS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
        ]
    )
    model = RandomForestClassifier(
        n_estimators=250,
        random_state=42,
        class_weight="balanced",
        min_samples_leaf=1,
    )
    pipe = Pipeline([("features", preprocessor), ("model", model)])

    logo = LeaveOneGroupOut()
    proba = cross_val_predict(pipe, X, y, groups=groups, cv=logo, method="predict_proba")[:, 1]
    pred = (proba >= 0.5).astype(int)

    predictions = df[
        [
            "lab_id",
            "product",
            "candidate_exploit_family",
            "rank",
            "rank_score",
            "is_recommended",
        ]
    ].copy()
    predictions["predicted_success_probability"] = proba
    predictions["predicted_label"] = pred
    predictions = predictions.sort_values(["lab_id", "predicted_success_probability"], ascending=[True, False])
    predictions.to_csv(derived_dir / "baseline_predictions.csv", index=False, encoding="utf-8")

    metrics = {
        "task": "predict whether an exploit family should be recommended for a target",
        "rows": int(len(df)),
        "targets": int(groups.nunique()),
        "positive_rows": int(y.sum()),
        "validation": "LeaveOneTargetOut; each fold tests on a lab not seen during training",
        "accuracy": float(accuracy_score(y, pred)),
        "roc_auc": float(roc_auc_score(y, proba)) if y.nunique() == 2 else None,
        "top1_hit_rate_by_target": float(topk_hit_rate(predictions, 1)),
        "top3_hit_rate_by_target": float(topk_hit_rate(predictions, 3)),
        "classification_report": classification_report(y, pred, output_dict=True, zero_division=0),
        "label_warning": "Labels are heuristic recommendations, not confirmed exploit success.",
    }
    (derived_dir / "baseline_metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    pipe.fit(X, y)
    joblib.dump(pipe, model_dir / "random_forest_exploit_ranker.joblib")

    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print("\nTop prediction per lab:")
    print(predictions.groupby("lab_id").head(1)[["lab_id", "candidate_exploit_family", "predicted_success_probability", "is_recommended"]].to_string(index=False))


if __name__ == "__main__":
    main()
