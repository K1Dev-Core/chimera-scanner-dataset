from __future__ import annotations

import json
import queue
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

import faraday_model
import rank
import scanner

app = Flask(__name__)

JOBS: dict[str, dict] = {}
LOCK = threading.Lock()

# Persistent scan history (survives app restart).
DATA_DIR = Path(__file__).parent / "data" / "scans"
DATA_DIR.mkdir(parents=True, exist_ok=True)
INDEX_PATH = DATA_DIR.parent / "index.json"
_cfg_load = Path(__file__).parent / "data" / "config.json"


def _load_index() -> list:
    if INDEX_PATH.exists():
        try:
            return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return []
    return []


SCANS = _load_index()


def _save_scan(job: dict):
    """Persist a finished scan: index entry + full workspace json."""
    global SCANS
    rec = {
        "id": job["id"], "url": job["url"], "name": job["name"],
        "created_at": job["created_at"], "summary": job.get("workspace", {}).get("summary", {}),
    }
    with LOCK:
        SCANS = [r for r in SCANS if r["id"] != rec["id"]]
        SCANS.insert(0, rec)
    INDEX_PATH.write_text(json.dumps(SCANS, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / f'{job["id"]}.json').write_text(
        json.dumps(job.get("workspace", {}), ensure_ascii=False), encoding="utf-8")


def _workspace_of(job_id: str):
    """Current in-memory workspace, else load from disk."""
    job = JOBS.get(job_id)
    if job and job.get("workspace"):
        return job["workspace"]
    p = DATA_DIR / f"{job_id}.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return None
    return None


def _run_job(job_id: str, url: str):
    job = JOBS[job_id]

    def emit(event, tool, message="", level="info"):
        entry = {"event": event, "tool": tool, "message": message, "level": level, "ts": time.time()}
        job["logs"].append(entry)
        job["queue"].put(entry)

    try:
        target = scanner.run_scan(url, emit)
        ranking = rank.rank_target(target)
        target["ranking"] = ranking
        workspace = faraday_model.normalize_target(target)
        workspace["ranking"] = ranking
        job["target"] = target
        job["ranking"] = ranking
        job["workspace"] = workspace
        job["status"] = "done"
        _save_scan(job)
    except Exception as exc:  # noqa: BLE001
        job["status"] = "error"
        job["error"] = str(exc)
        emit("log", "app", f"Error: {exc}", "warn")
        emit("done", "app", "", "")
    finally:
        job["queue"].put(None)  # sentinel -> end SSE


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scans")
def scans():
    with LOCK:
        return jsonify({"ok": True, "scans": SCANS})


@app.route("/api/scan", methods=["POST"])
def start_scan():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"ok": False, "error": "url is required"}), 400
    name = (data.get("name") or "").strip()
    job_id = uuid.uuid4().hex[:12]
    job = {
        "id": job_id, "name": name or url, "url": url,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "logs": [], "queue": queue.Queue(), "target": None,
        "ranking": [], "workspace": None, "status": "running", "error": None,
    }
    with LOCK:
        JOBS[job_id] = job
    threading.Thread(target=_run_job, args=(job_id, url), daemon=True).start()
    return jsonify({"ok": True, "job_id": job_id})


@app.route("/api/scan/<job_id>/stream")
def stream(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return Response("{}", status=404)

    def gen():
        while True:
            item = job["queue"].get()
            if item is None:
                yield "event: done\ndata: {}\n\n"
                break
            yield f"data: {json.dumps(item)}\n\n"

    return Response(gen(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"})


@app.route("/api/scan/<job_id>/result")
def result(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"ok": True, "status": "done",
                        "workspace": _workspace_of(job_id), "ranking": [],
                        "target": (_workspace_of(job_id) or {}).get("target", {})})
    if not job["target"]:
        return jsonify({"ok": False, "error": job.get("error") or "scan not finished", "status": job["status"]})
    return jsonify({"ok": True, "target": job["target"], "ranking": job["ranking"],
                    "workspace": job["workspace"], "status": job["status"]})


@app.route("/api/scan/<job_id>/report")
def report(job_id: str):
    """Machine-consumable report (schema 1.0) for MCP/AI: target, services,
    vulnerabilities, and an executable attack_order."""
    w = _workspace_of(job_id)
    if not w:
        return jsonify({"ok": False, "error": "not found"}), 404
    meta = next((s for s in SCANS if s["id"] == job_id), None)
    return jsonify({"schema_version": w["schema_version"], "id": job_id,
                    "url": w.get("target", {}).get("url", ""),
                    "name": (meta or {}).get("name", ""),
                    "created_at": (meta or {}).get("created_at", ""),
                    **{k: w[k] for k in ("target", "services", "vulnerabilities", "attack_order", "summary", "workflow")},
                    "ranking": w.get("ranking", [])})


if __name__ == "__main__":
    # ponytail: port 5050 avoids macOS AirPlay Receiver squatting on 5000.
    app.run(host="127.0.0.1", port=5050, debug=False, threaded=True)
