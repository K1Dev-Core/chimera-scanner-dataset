from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Show ranked exploit-family predictions for one lab.")
    parser.add_argument("--dataset-root", default=".")
    parser.add_argument("--lab-id", default="dvwa")
    args = parser.parse_args()

    root = Path(args.dataset_root).resolve()
    model = joblib.load(root / "models" / "random_forest_exploit_ranker.joblib")
    df = pd.read_csv(root / "derived" / "training_examples.csv")
    sample = df[df["lab_id"] == args.lab_id].copy()
    if sample.empty:
        raise SystemExit(f"Unknown lab_id: {args.lab_id}")

    feature_cols = [
        "port", "rank_score", "family_risk_prior", "evidence_source_count",
        "has_zap_evidence", "has_nuclei_evidence", "has_wapiti_evidence", "has_nikto_evidence",
        "zap_finding_count", "nuclei_finding_count", "nikto_finding_count", "wapiti_finding_count",
        "observed_title_count", "observed_tech_count", "service_product_count", "service_version_count",
        "product", "candidate_exploit_family", "observed_tech_text", "service_products_text",
        "service_versions_text", "evidence_sources_text",
    ]
    sample["predicted_success_probability"] = model.predict_proba(sample[feature_cols])[:, 1]
    ranked = sample.sort_values("predicted_success_probability", ascending=False)
    print(ranked[["lab_id", "candidate_exploit_family", "predicted_success_probability", "rank", "rank_score"]].to_string(index=False))


if __name__ == "__main__":
    main()
