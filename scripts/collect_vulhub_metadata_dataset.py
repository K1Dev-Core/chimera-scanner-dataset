from __future__ import annotations

import hashlib
import csv
import json
import re
from datetime import date
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[1]
VULHUB_ROOT = WORKSPACE_ROOT / "vulhub"
OUT_ROOT = REPO_ROOT / "chimera-tools-name-date-2026-08-05-vulhub-expanded-metadata"


SELECTED = [
    ("1panel", "CVE-2024-39907"),
    ("activemq", "CVE-2015-5254"),
    ("activemq", "CVE-2016-3088"),
    ("activemq", "CVE-2023-46604"),
    ("adminer", "CVE-2021-21311"),
    ("airflow", "CVE-2020-11978"),
    ("apache-druid", "CVE-2021-25646"),
    ("apisix", "CVE-2020-13945"),
    ("cacti", "CVE-2022-46169"),
    ("cmsms", "CVE-2019-9053"),
    ("coldfusion", "CVE-2023-26360"),
    ("confluence", "CVE-2021-26084"),
    ("confluence", "CVE-2022-26134"),
    ("couchdb", "CVE-2017-12635"),
    ("craftcms", "CVE-2023-41892"),
    ("django", "CVE-2019-14234"),
    ("drupal", "CVE-2014-3704"),
    ("drupal", "CVE-2018-7600"),
    ("elasticsearch", "CVE-2015-1427"),
    ("flask", "ssti"),
    ("flink", "CVE-2020-17518"),
    ("geoserver", "CVE-2024-36401"),
    ("gitlab", "CVE-2021-22205"),
    ("grafana", "CVE-2021-43798"),
    ("grafana", "CVE-2024-9264"),
    ("h2database", "CVE-2021-42392"),
    ("httpd", "CVE-2021-41773"),
    ("jenkins", "CVE-2018-1000861"),
    ("jenkins", "CVE-2024-23897"),
    ("jira", "CVE-2019-11581"),
    ("joomla", "CVE-2023-23752"),
    ("jupyter", "notebook-rce"),
    ("kibana", "CVE-2019-7609"),
    ("laravel", "CVE-2021-3129"),
    ("log4j", "CVE-2021-44228"),
    ("magento", "2.2-sqli"),
    ("metabase", "CVE-2021-41277"),
    ("mongo-express", "CVE-2019-10758"),
    ("n8n", "CVE-2026-21858"),
    ("nacos", "CVE-2021-29441"),
    ("next.js", "CVE-2025-29927"),
    ("nexus", "CVE-2020-10199"),
    ("nginx", "CVE-2017-7529"),
    ("nginx-ui", "CVE-2026-27944"),
    ("ofbiz", "CVE-2023-51467"),
    ("openfire", "CVE-2023-32315"),
    ("php", "CVE-2012-1823"),
    ("php", "CVE-2019-11043"),
    ("phpmyadmin", "CVE-2018-12613"),
    ("phpunit", "CVE-2017-9841"),
    ("redis", "4-unacc"),
    ("rocketchat", "CVE-2021-22911"),
    ("rocketmq", "CVE-2023-33246"),
    ("shiro", "CVE-2016-4437"),
    ("showdoc", "3.2.5-sqli"),
    ("solr", "CVE-2019-17558"),
    ("spring", "CVE-2022-22965"),
    ("struts2", "s2-045"),
    ("teamcity", "CVE-2023-42793"),
    ("teamcity", "CVE-2024-27198"),
    ("thinkphp", "5.0.23-rce"),
    ("tomcat", "CVE-2017-12615"),
    ("weblogic", "CVE-2020-14882"),
    ("webmin", "CVE-2019-15107"),
    ("wordpress", "pwnscriptum"),
    ("zabbix", "CVE-2016-10134"),
]


FAMILY_BY_KEYWORD = [
    (("sqli", "sql-injection", "sqlinjection"), "sqli"),
    (("nosql", "mongodb-inj"), "nosql-injection"),
    (("xxe",), "xxe"),
    (("ssrf",), "ssrf"),
    (("file-read", "fileread", "file-inclusion", "lfi", "traversal", "path-traversal"), "file-inclusion"),
    (("upload",), "file-upload"),
    (("deserialization", "viewstate", "unserialize", "unpickle", "shiro"), "deserialization"),
    (("auth", "unauth", "unauthorized", "access-control", "bypass", "weak_password"), "auth-bypass"),
    (("xss",), "xss"),
    (("rce", "command", "code", "log4j", "struts2", "weblogic", "spring", "thinkphp"), "command-injection"),
]

PRODUCT_DEFAULT_FAMILY = {
    "activemq": "deserialization",
    "airflow": "command-injection",
    "apache-druid": "command-injection",
    "confluence": "command-injection",
    "drupal": "command-injection",
    "elasticsearch": "command-injection",
    "flask": "command-injection",
    "flink": "file-upload",
    "geoserver": "command-injection",
    "gitlab": "file-upload",
    "grafana": "file-inclusion",
    "h2database": "command-injection",
    "httpd": "file-inclusion",
    "jenkins": "file-inclusion",
    "jira": "ssti",
    "jupyter": "command-injection",
    "kibana": "command-injection",
    "laravel": "deserialization",
    "log4j": "command-injection",
    "nacos": "auth-bypass",
    "next.js": "auth-bypass",
    "ofbiz": "auth-bypass",
    "openfire": "auth-bypass",
    "php": "command-injection",
    "phpmyadmin": "file-inclusion",
    "phpunit": "command-injection",
    "redis": "auth-bypass",
    "rocketmq": "command-injection",
    "solr": "command-injection",
    "spring": "command-injection",
    "struts2": "command-injection",
    "teamcity": "auth-bypass",
    "tomcat": "file-upload",
    "weblogic": "auth-bypass",
    "webmin": "command-injection",
    "zabbix": "sqli",
}


RELATED_FAMILIES = {
    "command-injection": ["auth-bypass", "file-upload", "deserialization"],
    "sqli": ["auth-bypass", "sensitive-data-exposure", "xss"],
    "nosql-injection": ["auth-bypass", "sensitive-data-exposure", "sqli"],
    "xxe": ["file-inclusion", "ssrf", "sensitive-data-exposure"],
    "ssrf": ["file-inclusion", "auth-bypass", "sensitive-data-exposure"],
    "file-inclusion": ["sensitive-data-exposure", "auth-bypass", "command-injection"],
    "file-upload": ["command-injection", "xss", "auth-bypass"],
    "deserialization": ["command-injection", "auth-bypass", "file-inclusion"],
    "auth-bypass": ["broken-access-control", "sensitive-data-exposure", "command-injection"],
    "xss": ["csrf", "sensitive-data-exposure", "auth-bypass"],
    "ssti": ["command-injection", "file-inclusion", "sensitive-data-exposure"],
}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_ports(compose: str) -> list[dict]:
    ports: list[dict] = []
    for raw in re.findall(r'["\']?(\d{2,5})\s*:\s*(\d{1,5})(?:/(tcp|udp))?["\']?', compose):
        host, container, proto = raw
        ports.append({"host_port": int(host), "container_port": int(container), "protocol": proto or "tcp"})
    return ports


def extract_images(compose: str) -> list[str]:
    images = []
    for image in re.findall(r"(?m)^\s*image:\s*([^\s#]+)", compose):
        images.append(image.strip().strip('"').strip("'"))
    return sorted(set(images))


def infer_family(product: str, case: str, readme: str) -> str:
    haystack = f"{product} {case} {readme[:3000]}".lower()
    for keys, family in FAMILY_BY_KEYWORD:
        if any(key in haystack for key in keys):
            return family
    return PRODUCT_DEFAULT_FAMILY.get(product, "generic-web")


def candidate_rows(lab_id: str, product: str, cve: str | None, family: str) -> list[dict]:
    families = [family] + RELATED_FAMILIES.get(family, ["generic-web", "sensitive-data-exposure", "auth-bypass"])
    rows = []
    for idx, fam in enumerate(families[:4], start=1):
        score = max(0.18, 0.96 - ((idx - 1) * 0.18))
        rows.append(
            {
                "dataset_record_type": "exploit_rank_candidate",
                "lab_id": lab_id,
                "product": product,
                "cve": cve,
                "exploit_family": fam,
                "rank": idx,
                "rank_score": round(score, 3),
                "is_recommended": 1 if idx <= 2 else 0,
                "label_source": "vulhub_directory_metadata_heuristic",
                "label_warning": "Weak candidate label from Vulhub lab metadata; not exploit-success validation.",
            }
        )
    return rows


def main() -> None:
    records_dir = OUT_ROOT / "records"
    manifests_dir = OUT_ROOT / "manifests"
    derived_dir = OUT_ROOT / "derived"
    for path in (records_dir, manifests_dir, derived_dir):
        path.mkdir(parents=True, exist_ok=True)

    lab_records = []
    feature_rows = []
    label_rows = []
    candidates = []

    for product, case in SELECTED:
        lab_path = VULHUB_ROOT / product / case
        compose_path = lab_path / "docker-compose.yml"
        if not compose_path.exists():
            continue
        compose = read_text(compose_path)
        readme = read_text(lab_path / "README.md")
        cve_match = re.search(r"CVE-\d{4}-\d+", case, flags=re.I)
        cve = cve_match.group(0).upper() if cve_match else None
        family = infer_family(product, case, readme)
        lab_id = f"{slug(product)}-{slug(case)}"
        images = extract_images(compose)
        ports = extract_ports(compose)
        title = ""
        title_match = re.search(r"(?m)^#\s+(.+)$", readme)
        if title_match:
            title = title_match.group(1).strip()

        lab_record = {
            "dataset_record_type": "vulhub_lab_metadata",
            "lab_id": lab_id,
            "product": product,
            "case": case,
            "cve": cve,
            "known_exploit_family": family,
            "vulhub_path": f"{product}/{case}",
            "title": title,
            "images": images,
            "exposed_ports": ports,
            "compose_service_count": len(re.findall(r"(?m)^\s{2}[A-Za-z0-9_.-]+:\s*$", compose)),
            "has_readme": bool(readme),
            "has_compose": True,
            "runtime_scan_status": "not_run_docker_unavailable",
            "safety_scope": "metadata/fingerprint seed only; no exploit execution",
        }
        lab_records.append(lab_record)

        feature_rows.append(
            {
                "dataset_record_type": "exploit_dl_target_feature_seed",
                "lab_id": lab_id,
                "product": product,
                "cve": cve,
                "known_exploit_family": family,
                "exposed_port_count": len(ports),
                "has_http_port_hint": int(any(p["container_port"] in {80, 443, 8080, 8081, 8000, 9000, 3000, 5000, 5601, 8983} for p in ports)),
                "image_count": len(images),
                "compose_service_count": lab_record["compose_service_count"],
                "product_text": product,
                "image_text": " | ".join(images) or "none",
                "port_text": " | ".join(f'{p["host_port"]}:{p["container_port"]}/{p["protocol"]}' for p in ports) or "none",
                "label_source": "vulhub_directory_metadata",
            }
        )

        label_rows.append(
            {
                "dataset_record_type": "exploit_label_candidate",
                "lab_id": lab_id,
                "cve": cve,
                "product": product,
                "known_exploit_family": family,
                "exploit_success_observed": None,
                "label_source": "vulhub_directory_name_and_readme",
                "recommended_for_model": "Use as weak positive family label; replace/confirm with safe local validation later.",
            }
        )
        candidates.extend(candidate_rows(lab_id, product, cve, family))

    outputs = {
        "vulhub-lab-metadata.jsonl": lab_records,
        "exploit-dl-feature-seeds.jsonl": feature_rows,
        "exploit-label-candidates.jsonl": label_rows,
        "exploit-rank-candidates.jsonl": candidates,
        "all-records.jsonl": lab_records + feature_rows + label_rows + candidates,
    }
    for filename, rows in outputs.items():
        with (records_dir / filename).open("w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    label_by_lab = {row["lab_id"]: row for row in label_rows}
    training_rows = []
    for row in candidates:
        feature = next(item for item in feature_rows if item["lab_id"] == row["lab_id"])
        label = label_by_lab[row["lab_id"]]
        training_rows.append(
            {
                "lab_id": row["lab_id"],
                "product": row["product"],
                "cve": row["cve"] or "",
                "candidate_exploit_family": row["exploit_family"],
                "known_exploit_family": label["known_exploit_family"],
                "rank": row["rank"],
                "rank_score": row["rank_score"],
                "is_recommended": row["is_recommended"],
                "is_known_family": 1 if row["exploit_family"] == label["known_exploit_family"] else 0,
                "exposed_port_count": feature["exposed_port_count"],
                "has_http_port_hint": feature["has_http_port_hint"],
                "image_count": feature["image_count"],
                "compose_service_count": feature["compose_service_count"],
                "product_text": feature["product_text"],
                "image_text": feature["image_text"],
                "port_text": feature["port_text"],
                "label_source": row["label_source"],
            }
        )

    train_columns = list(training_rows[0].keys()) if training_rows else []
    with (derived_dir / "training_examples.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=train_columns)
        writer.writeheader()
        writer.writerows(training_rows)
    with (derived_dir / "training_examples.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for row in training_rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    categorical_cols = ["product", "candidate_exploit_family", "known_exploit_family"]
    categories = {col: sorted({str(row[col]) for row in training_rows}) for col in categorical_cols}
    vector_rows = []
    for row in training_rows:
        vector = {
            "lab_id": row["lab_id"],
            "candidate_exploit_family": row["candidate_exploit_family"],
            "rank_score": row["rank_score"],
            "exposed_port_count": row["exposed_port_count"],
            "has_http_port_hint": row["has_http_port_hint"],
            "image_count": row["image_count"],
            "compose_service_count": row["compose_service_count"],
            "label_is_recommended": row["is_recommended"],
            "label_is_known_family": row["is_known_family"],
        }
        for col in categorical_cols:
            for value in categories[col]:
                vector[f"{col}__{slug(value)}"] = 1 if str(row[col]) == value else 0
        vector_rows.append(vector)
    vector_columns = list(vector_rows[0].keys()) if vector_rows else []
    with (derived_dir / "feature_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=vector_columns)
        writer.writeheader()
        writer.writerows(vector_rows)

    family_counts = {}
    for row in label_rows:
        family_counts[row["known_exploit_family"]] = family_counts.get(row["known_exploit_family"], 0) + 1

    summary = {
        "name": "chimera-vulhub-expanded-metadata-tools-name-date",
        "date": date.today().isoformat(),
        "source_type": "local Vulhub source metadata",
        "schema_version": "0.1.0",
        "safety_scope": "no exploit execution; no active attack payloads; Docker runtime unavailable",
        "labs": len(lab_records),
        "feature_seed_rows": len(feature_rows),
        "label_candidate_rows": len(label_rows),
        "rank_candidate_rows": len(candidates),
        "derived_training_rows": len(training_rows),
        "derived_feature_columns": len(vector_columns),
        "all_records": sum(len(rows) for rows in outputs.values() if isinstance(rows, list) and rows is outputs["all-records.jsonl"]),
        "known_family_counts": family_counts,
        "note": "Use this batch to expand Step 2 features and candidate labels. Runtime scanner evidence should be appended when Docker is available.",
    }
    (manifests_dir / "index.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    checksum_lines = []
    for path in sorted(records_dir.glob("*.jsonl")) + sorted(manifests_dir.glob("*.json")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        checksum_lines.append(f"{digest}  {path.relative_to(OUT_ROOT).as_posix()}")
    (manifests_dir / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    readme = f"""# Chimera Vulhub Expanded Metadata Dataset (2026-08-05)

This batch adds many Vulhub-derived lab rows for Exploit-DL Step 2/3 preparation.

Important: Docker Desktop was unavailable during this run, so this is a metadata/fingerprint-seed dataset, not a live scan batch.

## Contents

- `records/vulhub-lab-metadata.jsonl`: product, CVE, compose images, exposed ports
- `records/exploit-dl-feature-seeds.jsonl`: numeric/text feature seeds for Step 2
- `records/exploit-label-candidates.jsonl`: weak family labels from Vulhub metadata
- `records/exploit-rank-candidates.jsonl`: candidate exploit-family ranking rows
- `records/all-records.jsonl`: combined records
- `manifests/index.json`: batch summary
- `manifests/checksums.sha256`: artifact checksums
- `derived/training_examples.csv`: candidate rows for baseline/ranking experiments
- `derived/feature_matrix.csv`: simple one-hot numeric matrix for Step 2

## Why this helps

The earlier live dataset is useful for the pipeline, but it is still small. This batch broadens product/CVE/family coverage so feature engineering can learn from many product and vulnerability families before live validation is added.

## Limits

- `exploit_success_observed` is still `null`.
- Labels are weak labels from lab metadata, not proof that an exploit succeeded.
- Runtime scanner features such as actual titles/headers/nmap service banners must be appended later.

## Next recommended work

1. When Docker works, run live fingerprinting on 10-20 of these labs.
2. Add negative samples from patched/non-vulnerable versions where possible.
3. Build Step 2 encoder over both runtime scan features and these metadata seeds.
4. Compare manual baseline vs model-assisted ranking using time-to-correct-family and top-k hit rate.
"""
    (OUT_ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
