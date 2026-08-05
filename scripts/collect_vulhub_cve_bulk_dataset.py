from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[1]
VULHUB_ROOT = WORKSPACE_ROOT / "vulhub"
OUT_ROOT = REPO_ROOT / "chimera-tools-name-date-2026-08-05-vulhub-cve-bulk"
TODAY = "2026-08-05"
MAX_LABS = 160


FAMILY_BY_KEYWORD = [
    (("sql-injection", "sqli", "sql injection"), "sqli"),
    (("nosql", "mongodb-injection"), "nosql-injection"),
    (("xss", "cross-site scripting"), "xss"),
    (("xxe", "xml external"), "xxe"),
    (("ssrf",), "ssrf"),
    (("path traversal", "directory traversal", "file read", "arbitrary file", "lfi", "local file"), "file-inclusion"),
    (("upload", "file upload"), "file-upload"),
    (("deserial", "unserialize", "pickle", "shiro"), "deserialization"),
    (("auth bypass", "authentication bypass", "unauthorized", "unauth", "access control", "privilege"), "auth-bypass"),
    (("rce", "remote code", "command injection", "code execution", "ognl", "jndi", "log4shell"), "command-injection"),
]


PRODUCT_DEFAULT_FAMILY = {
    "activemq": "deserialization",
    "airflow": "command-injection",
    "apache-druid": "command-injection",
    "apisix": "auth-bypass",
    "cacti": "command-injection",
    "coldfusion": "command-injection",
    "confluence": "command-injection",
    "couchdb": "auth-bypass",
    "craftcms": "command-injection",
    "django": "sqli",
    "drupal": "command-injection",
    "elasticsearch": "command-injection",
    "flink": "file-upload",
    "geoserver": "command-injection",
    "gitlab": "file-upload",
    "grafana": "file-inclusion",
    "h2database": "command-injection",
    "httpd": "file-inclusion",
    "jenkins": "file-inclusion",
    "jira": "ssti",
    "joomla": "auth-bypass",
    "kibana": "command-injection",
    "laravel": "deserialization",
    "log4j": "command-injection",
    "nacos": "auth-bypass",
    "next.js": "auth-bypass",
    "nginx": "file-inclusion",
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
    "thinkphp": "command-injection",
    "tomcat": "file-upload",
    "weblogic": "auth-bypass",
    "webmin": "command-injection",
    "wordpress": "auth-bypass",
    "zabbix": "sqli",
}


RELATED_FAMILIES = {
    "command-injection": ["auth-bypass", "file-upload", "deserialization"],
    "sqli": ["auth-bypass", "sensitive-data-exposure", "xss"],
    "nosql-injection": ["auth-bypass", "sensitive-data-exposure", "sqli"],
    "xss": ["csrf", "sensitive-data-exposure", "auth-bypass"],
    "xxe": ["file-inclusion", "ssrf", "sensitive-data-exposure"],
    "ssrf": ["file-inclusion", "auth-bypass", "sensitive-data-exposure"],
    "file-inclusion": ["sensitive-data-exposure", "auth-bypass", "command-injection"],
    "file-upload": ["command-injection", "xss", "auth-bypass"],
    "deserialization": ["command-injection", "auth-bypass", "file-inclusion"],
    "auth-bypass": ["broken-access-control", "sensitive-data-exposure", "command-injection"],
    "ssti": ["command-injection", "file-inclusion", "sensitive-data-exposure"],
    "generic-web": ["auth-bypass", "sensitive-data-exposure", "xss"],
}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def read_text(path: Path, limit: int | None = None) -> str:
    if not path.exists():
        return ""
    data = path.read_text(encoding="utf-8", errors="ignore")
    return data[:limit] if limit else data


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def extract_images(compose: str) -> list[str]:
    return sorted(set(x.strip().strip('"').strip("'") for x in re.findall(r"(?m)^\s*image:\s*([^\s#]+)", compose)))


def extract_ports(compose: str) -> list[dict]:
    ports: list[dict] = []
    patterns = [
        r'["\']?(\d{2,5})\s*:\s*(\d{1,5})(?:/(tcp|udp))?["\']?',
        r'["\']?(\d{1,5})(?:/(tcp|udp))?["\']?',
    ]
    for host, container, proto in re.findall(patterns[0], compose):
        ports.append({"host_port": int(host), "container_port": int(container), "protocol": proto or "tcp"})
    if not ports:
        for container, proto in re.findall(patterns[1], compose):
            port = int(container)
            if port in {80, 443, 8080, 8000, 3000, 5000, 7001, 8081, 9000, 9200, 10086}:
                ports.append({"host_port": None, "container_port": port, "protocol": proto or "tcp"})
    unique = []
    seen = set()
    for port in ports:
        key = (port["host_port"], port["container_port"], port["protocol"])
        if key not in seen:
            unique.append(port)
            seen.add(key)
    return unique


def extract_cves(text: str) -> list[str]:
    return sorted(set(re.findall(r"CVE-\d{4}-\d{4,7}", text, flags=re.I)), key=str.lower)


def infer_family(product: str, case: str, readme: str) -> str:
    haystack = f"{product} {case} {readme[:6000]}".lower()
    for keys, family in FAMILY_BY_KEYWORD:
        if any(key in haystack for key in keys):
            return family
    return PRODUCT_DEFAULT_FAMILY.get(product, "generic-web")


def candidate_rows(lab_id: str, product: str, cve: str, family: str) -> list[dict]:
    families = [family] + RELATED_FAMILIES.get(family, RELATED_FAMILIES["generic-web"])
    rows = []
    for idx, candidate in enumerate(families[:4], start=1):
        score = max(0.18, 0.96 - (idx - 1) * 0.18)
        rows.append(
            {
                "dataset_record_type": "exploit_rank_candidate",
                "tool": "vulhub-rank-seed",
                "lab_id": lab_id,
                "product": product,
                "cve": cve,
                "candidate_exploit_family": candidate,
                "known_exploit_family": family,
                "rank": idx,
                "rank_score": round(score, 3),
                "is_recommended": 1 if idx <= 2 else 0,
                "is_known_family": 1 if candidate == family else 0,
                "label_source": "vulhub_metadata_weak_label",
                "label_warning": "Weak label from Vulhub metadata and README keywords; not exploit-success validation.",
            }
        )
    return rows


def discover_labs() -> list[dict]:
    compose_files = sorted(VULHUB_ROOT.glob("*/*/docker-compose.yml"))
    labs = []
    for compose_path in compose_files:
        product = compose_path.parents[1].name
        case = compose_path.parent.name
        if product.startswith(".") or product in {"base"}:
            continue
        readme = read_text(compose_path.parent / "README.md")
        readme_zh = read_text(compose_path.parent / "README.zh-cn.md")
        compose = read_text(compose_path)
        cves = extract_cves(f"{case}\n{readme}\n{readme_zh}")
        cve = cves[0] if cves else case
        lab_id = slug(f"{product}-{case}")
        family = infer_family(product, case, f"{readme}\n{readme_zh}")
        labs.append(
            {
                "lab_id": lab_id,
                "product": product,
                "case": case,
                "cve": cve,
                "all_cves": cves,
                "known_exploit_family": family,
                "compose_path": compose_path,
                "readme_path": compose_path.parent / "README.md",
                "readme_zh_path": compose_path.parent / "README.zh-cn.md",
                "images": extract_images(compose),
                "ports": extract_ports(compose),
                "relative_path": str(compose_path.parent.relative_to(VULHUB_ROOT)).replace("\\", "/"),
            }
        )
    # Prefer named CVE labs first, then keep broad product coverage.
    labs.sort(key=lambda row: (0 if str(row["case"]).upper().startswith("CVE-") else 1, row["product"], row["case"]))
    return labs[:MAX_LABS]


def one_hot(rows: list[dict], field: str, prefix: str) -> list[str]:
    values = sorted({str(row.get(field, "none")) for row in rows})
    return [f"{prefix}_{slug(value)}" for value in values]


def main() -> None:
    if not VULHUB_ROOT.exists():
        raise SystemExit(f"Missing Vulhub clone: {VULHUB_ROOT}")
    if OUT_ROOT.exists():
        shutil.rmtree(OUT_ROOT)

    records_dir = OUT_ROOT / "records"
    derived_dir = OUT_ROOT / "derived"
    manifests_dir = OUT_ROOT / "manifests"
    for path in (records_dir, derived_dir, manifests_dir):
        path.mkdir(parents=True, exist_ok=True)

    labs = discover_labs()
    lab_records: list[dict] = []
    all_records: list[dict] = []
    feature_seed_rows: list[dict] = []
    label_rows: list[dict] = []
    rank_rows: list[dict] = []

    for lab in labs:
        lab_dir = OUT_ROOT / "datasets" / "labs" / lab["lab_id"]
        lab_dir.mkdir(parents=True, exist_ok=True)
        lab_json = {
            "lab_id": lab["lab_id"],
            "product": lab["product"],
            "case": lab["case"],
            "cve": lab["cve"],
            "all_cves": lab["all_cves"],
            "known_exploit_family": lab["known_exploit_family"],
            "relative_vulhub_path": lab["relative_path"],
            "images": lab["images"],
            "ports": lab["ports"],
        }
        (lab_dir / "lab.json").write_text(json.dumps(lab_json, indent=2, ensure_ascii=False), encoding="utf-8")
        lab_records.append({"dataset_record_type": "lab_metadata", **lab_json})

        compose = read_text(lab["compose_path"])
        readme = read_text(lab["readme_path"], limit=24000)
        readme_zh = read_text(lab["readme_zh_path"], limit=16000)

        compose_base = OUT_ROOT / "datasets" / "tools-name-date" / f"vulhub-compose-{TODAY}" / lab["lab_id"]
        compose_raw = compose_base / "raw"
        compose_norm = compose_base / "normalized"
        compose_raw.mkdir(parents=True, exist_ok=True)
        compose_norm.mkdir(parents=True, exist_ok=True)
        (compose_raw / "docker-compose.yml").write_text(compose, encoding="utf-8")
        compose_record = {
            "dataset_record_type": "compose_fingerprint",
            "tool": "vulhub-compose",
            "lab_id": lab["lab_id"],
            "product": lab["product"],
            "cve": lab["cve"],
            "images": lab["images"],
            "ports": lab["ports"],
            "compose_service_count": len(re.findall(r"(?m)^\s{2}[a-zA-Z0-9_.-]+:\s*$", compose)),
            "source": lab["relative_path"] + "/docker-compose.yml",
        }
        write_jsonl(compose_norm / "compose-normalized.jsonl", [compose_record])
        all_records.append(compose_record)

        readme_base = OUT_ROOT / "datasets" / "tools-name-date" / f"vulhub-readme-{TODAY}" / lab["lab_id"]
        readme_raw = readme_base / "raw"
        readme_norm = readme_base / "normalized"
        readme_raw.mkdir(parents=True, exist_ok=True)
        readme_norm.mkdir(parents=True, exist_ok=True)
        (readme_raw / "README.md").write_text(readme or readme_zh or "", encoding="utf-8")
        readme_text = f"{readme}\n{readme_zh}"
        readme_record = {
            "dataset_record_type": "readme_fingerprint",
            "tool": "vulhub-readme",
            "lab_id": lab["lab_id"],
            "product": lab["product"],
            "cve": lab["cve"],
            "title_hint": (readme_text.strip().splitlines() or [""])[0][:180],
            "cves_in_readme": extract_cves(readme_text),
            "keyword_family": lab["known_exploit_family"],
            "readme_length": len(readme_text),
            "source": lab["relative_path"] + "/README.md",
        }
        write_jsonl(readme_norm / "readme-normalized.jsonl", [readme_record])
        all_records.append(readme_record)

        cve_base = OUT_ROOT / "datasets" / "tools-name-date" / f"vulhub-cve-map-{TODAY}" / lab["lab_id"]
        cve_raw = cve_base / "raw"
        cve_norm = cve_base / "normalized"
        cve_raw.mkdir(parents=True, exist_ok=True)
        cve_norm.mkdir(parents=True, exist_ok=True)
        cve_map = {
            "lab_id": lab["lab_id"],
            "product": lab["product"],
            "case": lab["case"],
            "cve": lab["cve"],
            "all_cves": lab["all_cves"],
            "known_exploit_family": lab["known_exploit_family"],
        }
        (cve_raw / "cve-map.json").write_text(json.dumps(cve_map, indent=2, ensure_ascii=False), encoding="utf-8")
        cve_record = {"dataset_record_type": "cve_family_mapping", "tool": "vulhub-cve-map", **cve_map}
        write_jsonl(cve_norm / "cve-map-normalized.jsonl", [cve_record])
        all_records.append(cve_record)

        feature_seed = {
            "dataset_record_type": "feature_seed",
            "lab_id": lab["lab_id"],
            "product": lab["product"],
            "cve": lab["cve"],
            "known_exploit_family": lab["known_exploit_family"],
            "exposed_port_count": len(lab["ports"]),
            "has_http_port_hint": 1 if any(p["container_port"] in {80, 443, 8080, 8000, 3000, 5000, 7001, 8081, 9000, 10086} for p in lab["ports"]) else 0,
            "image_count": len(lab["images"]),
            "compose_service_count": compose_record["compose_service_count"],
            "has_cve": 1 if str(lab["cve"]).upper().startswith("CVE-") else 0,
            "cve_year": int(lab["cve"].split("-")[1]) if str(lab["cve"]).upper().startswith("CVE-") else 0,
            "product_text": lab["product"],
            "image_text": " | ".join(lab["images"]) or "none",
            "port_text": " | ".join(f"{p['host_port']}:{p['container_port']}/{p['protocol']}" for p in lab["ports"]) or "none",
        }
        feature_seed_rows.append(feature_seed)
        label_rows.append(
            {
                "dataset_record_type": "label_candidate",
                "lab_id": lab["lab_id"],
                "product": lab["product"],
                "cve": lab["cve"],
                "known_exploit_family": lab["known_exploit_family"],
                "label_source": "vulhub_readme_compose_metadata",
                "label_warning": "Weak label only. Confirm with scanner evidence and exploit-success feedback later.",
            }
        )
        ranks = candidate_rows(lab["lab_id"], lab["product"], lab["cve"], lab["known_exploit_family"])
        rank_rows.extend(ranks)
        rank_base = OUT_ROOT / "datasets" / "tools-name-date" / f"vulhub-rank-seed-{TODAY}" / lab["lab_id"]
        write_jsonl(rank_base / "normalized" / "rank-candidates.jsonl", ranks)
        (rank_base / "raw").mkdir(parents=True, exist_ok=True)
        (rank_base / "raw" / "rank-seed.json").write_text(json.dumps(ranks, indent=2, ensure_ascii=False), encoding="utf-8")
        all_records.extend(ranks)

    write_jsonl(records_dir / "lab-index.jsonl", lab_records)
    write_jsonl(records_dir / "feature-seeds.jsonl", feature_seed_rows)
    write_jsonl(records_dir / "label-candidates.jsonl", label_rows)
    write_jsonl(records_dir / "rank-candidates.jsonl", rank_rows)
    write_jsonl(records_dir / "all-records.jsonl", all_records)

    training_rows = []
    seed_by_lab = {row["lab_id"]: row for row in feature_seed_rows}
    for rank in rank_rows:
        seed = seed_by_lab[rank["lab_id"]]
        training_rows.append(
            {
                "lab_id": rank["lab_id"],
                "product": rank["product"],
                "cve": rank["cve"],
                "candidate_exploit_family": rank["candidate_exploit_family"],
                "known_exploit_family": rank["known_exploit_family"],
                "rank": rank["rank"],
                "rank_score": rank["rank_score"],
                "is_recommended": rank["is_recommended"],
                "is_known_family": rank["is_known_family"],
                "exposed_port_count": seed["exposed_port_count"],
                "has_http_port_hint": seed["has_http_port_hint"],
                "image_count": seed["image_count"],
                "compose_service_count": seed["compose_service_count"],
                "has_cve": seed["has_cve"],
                "cve_year": seed["cve_year"],
                "product_text": seed["product_text"],
                "image_text": seed["image_text"],
                "port_text": seed["port_text"],
                "label_source": rank["label_source"],
            }
        )

    with (derived_dir / "training_examples.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(training_rows[0].keys()))
        writer.writeheader()
        writer.writerows(training_rows)
    write_jsonl(derived_dir / "training_examples.jsonl", training_rows)

    products = sorted({row["product"] for row in training_rows})
    candidates = sorted({row["candidate_exploit_family"] for row in training_rows})
    knowns = sorted({row["known_exploit_family"] for row in training_rows})
    feature_rows_matrix = []
    for row in training_rows:
        out = {
            "lab_id": row["lab_id"],
            "candidate_exploit_family": row["candidate_exploit_family"],
            "rank_score": row["rank_score"],
            "exposed_port_count": row["exposed_port_count"],
            "has_http_port_hint": row["has_http_port_hint"],
            "image_count": row["image_count"],
            "compose_service_count": row["compose_service_count"],
            "has_cve": row["has_cve"],
            "cve_year": row["cve_year"],
            "label_is_recommended": row["is_recommended"],
            "label_is_known_family": row["is_known_family"],
        }
        for product in products:
            out[f"product__{slug(product)}"] = 1 if row["product"] == product else 0
        for candidate in candidates:
            out[f"candidate_exploit_family__{slug(candidate)}"] = 1 if row["candidate_exploit_family"] == candidate else 0
        for known in knowns:
            out[f"known_exploit_family__{slug(known)}"] = 1 if row["known_exploit_family"] == known else 0
        feature_rows_matrix.append(out)
    with (derived_dir / "feature_matrix.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(feature_rows_matrix[0].keys()))
        writer.writeheader()
        writer.writerows(feature_rows_matrix)

    family_counts: dict[str, int] = {}
    for row in label_rows:
        family_counts[row["known_exploit_family"]] = family_counts.get(row["known_exploit_family"], 0) + 1
    manifest = {
        "name": "chimera-tools-name-date-2026-08-05-vulhub-cve-bulk",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(VULHUB_ROOT),
        "scope": "Vulhub static lab metadata collection; raw/normalized dataset seed; no exploit execution.",
        "tools_name_date_views": [
            f"vulhub-compose-{TODAY}",
            f"vulhub-readme-{TODAY}",
            f"vulhub-cve-map-{TODAY}",
            f"vulhub-rank-seed-{TODAY}",
        ],
        "planned_active_scanner_tools": ["nmap", "httpx", "nuclei", "nikto", "wapiti", "zap"],
        "counts": {
            "labs": len(lab_records),
            "feature_seed_rows": len(feature_seed_rows),
            "label_candidate_rows": len(label_rows),
            "rank_candidate_rows": len(rank_rows),
            "all_records": len(all_records),
            "training_rows": len(training_rows),
            "feature_matrix_rows": len(feature_rows_matrix),
            "feature_matrix_columns": len(feature_rows_matrix[0]),
            "family_counts": dict(sorted(family_counts.items())),
        },
        "label_warning": "Labels are weak metadata labels. Add exploit_success_observed for research-grade Exploit-DL training.",
    }
    (manifests_dir / "index.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (manifests_dir / "source-run-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    readme = f"""# Chimera Vulhub CVE Bulk Dataset ({TODAY})

ชุดนี้รวบรวม CVE/lab จาก Vulhub จำนวนมาก เพื่อเพิ่มฐานข้อมูลสำหรับโปรเจกต์ Exploit-DL ก่อนนำไปต่อยอดด้วย scanner evidence และ exploit-success labels

## สถานะ

- Labs: {manifest['counts']['labs']}
- Training rows: {manifest['counts']['training_rows']}
- Feature matrix rows: {manifest['counts']['feature_matrix_rows']}
- Feature matrix columns: {manifest['counts']['feature_matrix_columns']}
- Records ทั้งหมด: {manifest['counts']['all_records']}

## โครงสร้าง tools-name-date

```text
datasets/tools-name-date/vulhub-compose-{TODAY}/<lab-id>/raw/
datasets/tools-name-date/vulhub-compose-{TODAY}/<lab-id>/normalized/
datasets/tools-name-date/vulhub-readme-{TODAY}/<lab-id>/raw/
datasets/tools-name-date/vulhub-readme-{TODAY}/<lab-id>/normalized/
datasets/tools-name-date/vulhub-cve-map-{TODAY}/<lab-id>/raw/
datasets/tools-name-date/vulhub-cve-map-{TODAY}/<lab-id>/normalized/
datasets/tools-name-date/vulhub-rank-seed-{TODAY}/<lab-id>/raw/
datasets/tools-name-date/vulhub-rank-seed-{TODAY}/<lab-id>/normalized/
```

## ไฟล์สำคัญ

- `records/lab-index.jsonl` — รายชื่อ lab/CVE/product
- `records/feature-seeds.jsonl` — seed feature เช่น ports, images, cve year
- `records/label-candidates.jsonl` — weak label ของ vulnerability family
- `records/rank-candidates.jsonl` — candidate family ranking
- `derived/training_examples.csv` — ตาราง train/ranking แบบคนอ่าน
- `derived/feature_matrix.csv` — feature matrix แบบตัวเลข
- `manifests/index.json` — summary ของ dataset

## หมายเหตุ

ชุดนี้เป็น static metadata collection จาก Vulhub ยังไม่ใช่ active scan ด้วย `nmap/httpx/nuclei/nikto/wapiti/zap` และยังไม่ใช่ exploit validation จริง ขั้นต่อไปคือรัน scanner suite กับ lab ที่เลือก แล้วเพิ่ม `exploit_success_observed = 1/0`
"""
    (OUT_ROOT / "README.md").write_text(readme, encoding="utf-8")

    checksum_lines = []
    for path in sorted(OUT_ROOT.rglob("*")):
        if path.is_file() and path.name != "checksums.sha256":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            rel = path.relative_to(OUT_ROOT).as_posix()
            checksum_lines.append(f"{digest}  {rel}")
    (manifests_dir / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

