from __future__ import annotations

# Reused from chimera-scanner-dataset scripts/evaluate_dec_ml_scan_20260825.py (Dec branch).
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
    "phpmyadmin": {"aliases": ["phpmyadmin", "access denied"], "ports": [8080]},
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

# Same as the repo's alias_score().
def alias_score(text: str, aliases: list[str]) -> float:
    if not text:
        return 0.0
    hits = sum(1 for alias in aliases if alias and alias.lower() in text)
    return min(1.0, hits / max(len(aliases), 1))


def as_int(value) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(float(str(value)))
    except (ValueError, TypeError):
        return None


def text_value(row: dict, *keys: str) -> str:
    return " ".join(str(row.get(key, "") or "") for key in keys).lower()


def truthy(value) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


# Same as the repo's candidate_features(); returns per-feature + heuristic score.
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


def _softmax(scores: list[float]) -> list[float]:
    # ponytail: raw softmax over heuristic scores (fallback when no trained model).
    import numpy as np

    arr = np.array(scores, dtype=float)
    arr = arr - arr.max()
    e = np.exp(arr)
    return (e / e.sum()).tolist()


def _load_model():
    """Load the trained logistic ranker if present; otherwise fall back to heuristic."""
    import json
    from pathlib import Path

    path = Path(__file__).parent / "models" / "model.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


_MODEL = _load_model()


def _model_probabilities(rows: list[dict]) -> dict:
    """Standardize each family's features and score with the trained logistic model."""
    import numpy as np

    m = _MODEL
    names = m["feature_names"]
    mean = np.array(m["mean"], dtype=float)
    std = np.array(m["std"], dtype=float)
    coef = np.array(m["coef"], dtype=float)
    intercept = float(m["intercept"])
    probs = {}
    for row in rows:
        X = np.array([row.get(n, 0.0) or 0.0 for n in names], dtype=float)
        X = (X - mean) / std
        logit = intercept + float(coef @ X)
        probs[row["family"]] = 1.0 / (1.0 + float(np.exp(-max(-40.0, min(40.0, logit)))))
    return probs


def rank_target(target: dict) -> list[dict]:
    rows = []
    for family in sorted(FAMILY_HINTS):
        feats = candidate_features(target, family)
        rows.append({"family": family, **feats})

    if _MODEL:
        probs = _model_probabilities(rows)
        for row in rows:
            row["probability"] = probs[row["family"]]
            row["confidence"] = round(row["probability"], 4)
        rows.sort(key=lambda r: r["probability"], reverse=True)
    else:
        rows.sort(key=lambda r: r["heuristic_score"], reverse=True)
        for row, prob in zip(rows, _softmax([r["heuristic_score"] for r in rows])):
            row["confidence"] = round(prob, 4)

    for row in rows:
        row["rank"] = len([1 for other in rows if row["probability"] < other["probability"]]) + 1
    return rows
