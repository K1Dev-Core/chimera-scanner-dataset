from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


FAMILY_RISK = {
    "command-injection": 0.95,
    "sqli": 0.92,
    "nosql-injection": 0.88,
    "xxe": 0.82,
    "deserialization": 0.82,
    "file-upload": 0.78,
    "file-inclusion": 0.74,
    "auth-bypass": 0.70,
    "jwt": 0.68,
    "ssrf": 0.66,
    "broken-access-control": 0.62,
    "xss": 0.55,
    "csrf": 0.35,
    "sensitive-data-exposure": 0.34,
    "bruteforce": 0.30,
    "generic-web": 0.20,
}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def as_list(value):
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Exploit-DL feature/label tables from Chimera JSONL records.")
    parser.add_argument("--dataset-root", default=".", help="Path to chimera-tools-name-date-... dataset folder")
    args = parser.parse_args()

    root = Path(args.dataset_root).resolve()
    records_dir = root / "records"
    derived_dir = root / "derived"
    derived_dir.mkdir(parents=True, exist_ok=True)

    targets = read_jsonl(records_dir / "exploit-dl-target-features.jsonl")
    ranks = read_jsonl(records_dir / "exploit-rank-candidates.jsonl")
    all_records = read_jsonl(records_dir / "all-records.jsonl")

    target_by_lab = {row["lab_id"]: row for row in targets}
    finding_counts_by_lab: dict[str, dict[str, int]] = {}
    for row in all_records:
        lab_id = row.get("lab_id")
        tool = row.get("tool")
        if not lab_id or not tool:
            continue
        finding_counts_by_lab.setdefault(lab_id, {})
        finding_counts_by_lab[lab_id][tool] = finding_counts_by_lab[lab_id].get(tool, 0) + 1

    examples: list[dict] = []
    for rank in ranks:
        lab_id = rank["lab_id"]
        target = target_by_lab.get(lab_id, {})
        counts = target.get("scanner_finding_counts", {}) or {}
        observed_tech = as_list(target.get("observed_tech"))
        observed_titles = as_list(target.get("observed_titles"))
        service_products = as_list(target.get("service_products"))
        service_versions = as_list(target.get("service_versions"))
        evidence_sources = as_list(rank.get("evidence_sources"))
        candidate_family = rank.get("exploit_family", "unknown")
        rank_value = int(rank.get("rank", 999))
        rank_score = float(rank.get("rank_score", 0.0))

        examples.append(
            {
                "lab_id": lab_id,
                "product": rank.get("product") or target.get("product"),
                "target_url": rank.get("target_url") or target.get("target_url"),
                "port": int(target.get("port") or 0),
                "candidate_exploit_family": candidate_family,
                "rank": rank_value,
                "rank_score": rank_score,
                "is_top1": 1 if rank_value == 1 else 0,
                "is_recommended": 1 if rank_value <= 2 or rank_score >= 0.70 else 0,
                "family_risk_prior": FAMILY_RISK.get(candidate_family, 0.25),
                "evidence_source_count": len(set(evidence_sources)),
                "has_zap_evidence": 1 if "zap" in evidence_sources else 0,
                "has_nuclei_evidence": 1 if "nuclei" in evidence_sources else 0,
                "has_wapiti_evidence": 1 if "wapiti" in evidence_sources else 0,
                "has_nikto_evidence": 1 if "nikto" in evidence_sources else 0,
                "zap_finding_count": int(counts.get("zap", 0)),
                "nuclei_finding_count": int(counts.get("nuclei", 0)),
                "nikto_finding_count": int(counts.get("nikto", 0)),
                "wapiti_finding_count": int(counts.get("wapiti", 0)),
                "observed_title_count": len(observed_titles),
                "observed_tech_count": len(observed_tech),
                "service_product_count": len(service_products),
                "service_version_count": len(service_versions),
                "observed_titles_text": " | ".join(map(str, observed_titles)) or "none",
                "observed_tech_text": " | ".join(map(str, observed_tech)) or "none",
                "service_products_text": " | ".join(map(str, service_products)) or "none",
                "service_versions_text": " | ".join(map(str, service_versions)) or "none",
                "evidence_sources_text": " | ".join(map(str, evidence_sources)) or "none",
                "label_source": rank.get("label_source"),
                "label_warning": "demo label from ranking heuristic; replace with exploit_success_observed when validation exists",
            }
        )

    examples_df = pd.DataFrame(examples).sort_values(["lab_id", "rank"])
    examples_df.to_csv(derived_dir / "training_examples.csv", index=False, encoding="utf-8")
    examples_df.to_json(derived_dir / "training_examples.jsonl", orient="records", lines=True, force_ascii=False)

    numeric_cols = [
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
    categorical_cols = [
        "product",
        "candidate_exploit_family",
        "observed_tech_text",
        "service_products_text",
        "service_versions_text",
        "evidence_sources_text",
    ]

    vector_df = pd.get_dummies(examples_df[numeric_cols + categorical_cols], columns=categorical_cols, dtype=int)
    vector_df.insert(0, "lab_id", examples_df["lab_id"].values)
    vector_df.insert(1, "candidate_exploit_family", examples_df["candidate_exploit_family"].values)
    vector_df["label_is_recommended"] = examples_df["is_recommended"].values
    vector_df["label_is_top1"] = examples_df["is_top1"].values
    vector_df.to_csv(derived_dir / "feature_matrix.csv", index=False, encoding="utf-8")

    summary = {
        "rows": int(len(examples_df)),
        "targets": int(examples_df["lab_id"].nunique()),
        "candidate_families": sorted(examples_df["candidate_exploit_family"].unique().tolist()),
        "positive_recommended_rows": int(examples_df["is_recommended"].sum()),
        "feature_matrix_columns": int(vector_df.shape[1]),
        "main_label": "is_recommended",
        "ranking_label": "rank",
        "warning": "This is a demo/weak-label dataset. For research-grade training, replace heuristic labels with exploit validation results.",
    }
    (derived_dir / "feature_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
