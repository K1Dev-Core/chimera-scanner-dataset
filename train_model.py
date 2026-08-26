from __future__ import annotations

# Train a logistic regression ranker on the repo's candidate-family features and
# export a portable model.json so the live prototype can rank with a learned model
# (instead of only the raw heuristic). NO leakage: target_id/candidate_family/positive_family
# are dropped; only the 7 scanner-derived alias features are used.
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score

REPO_FEATURES = (
    experiments := Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "/var/folders/sb/_m362yg13tj3bbdy8mnrk4kw0000gn/T/opencode/chimera/experiments/dec-ml-scan-2026-08-25/derived"
    )
) / "candidate-family-features.csv"

FEATURES = [
    "title_alias_score",
    "server_alias_score",
    "nmap_alias_score",
    "body_alias_score",
    "port_score",
    "protocol_score",
    "http_tool_score",
]
OUT = Path(__file__).parent / "models" / "model.json"


def main() -> None:
    if not REPO_FEATURES.exists():
        print(f"training features not found: {REPO_FEATURES}")
        sys.exit(1)
    df = pd.read_csv(REPO_FEATURES)
    y = (df["label"] == "positive_family_match").astype(int).to_numpy()
    X = df[FEATURES].to_numpy(dtype=float)

    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std = np.where(std == 0, 1.0, std)  # avoid div-by-zero
    Xs = (X - mean) / std

    clf = LogisticRegression(max_iter=2000, class_weight="balanced")
    clf.fit(Xs, y)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_acc = cross_val_score(LogisticRegression(max_iter=2000, class_weight="balanced"), Xs, y, cv=cv, scoring="accuracy")

    model = {
        "feature_names": FEATURES,
        "mean": mean.tolist(),
        "std": std.tolist(),
        "coef": clf.coef_[0].tolist(),
        "intercept": float(clf.intercept_[0]),
        "metrics": {
            "train_rows": int(len(df)),
            "positive_rows": int(y.sum()),
            "negative_rows": int(len(y) - y.sum()),
            "cv_accuracy_mean": round(float(cv_acc.mean()), 4),
            "cv_accuracy_std": round(float(cv_acc.std()), 4),
            "n_features": len(FEATURES),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(model, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"trained from: {REPO_FEATURES}")
    print(f"rows={len(df)} positive={int(y.sum())} negative={int(len(y)-y.sum())}")
    print(f"cv_accuracy = {cv_acc.mean():.4f} ± {cv_acc.std():.4f}")
    print("coefficients (learned weights):")
    for name, w in zip(FEATURES, clf.coef_[0]):
        print(f"  {name:20s} {w:+.3f}")
    print(f"saved -> {OUT}")


if __name__ == "__main__":
    main()
