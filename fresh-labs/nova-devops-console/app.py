from __future__ import annotations

import os
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

import yaml
from flask import Flask, Response, redirect, render_template_string, request, session, url_for


ROOT = Path(__file__).parent
DB_PATH = ROOT / "nova.db"
SEED_DIR = ROOT / "seed"

app = Flask(__name__)
app.secret_key = "nova-local-lab-secret"


def conn() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db() -> None:
    db = conn()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY,
          username TEXT,
          password TEXT,
          role TEXT
        );

        CREATE TABLE IF NOT EXISTS deployments (
          id INTEGER PRIMARY KEY,
          service TEXT,
          owner TEXT,
          version TEXT,
          status TEXT,
          secret_note TEXT
        );

        CREATE TABLE IF NOT EXISTS audit_log (
          id INTEGER PRIMARY KEY,
          actor TEXT,
          action TEXT,
          created_at TEXT
        );
        """
    )
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        db.executemany(
            "INSERT INTO users(username,password,role) VALUES(?,?,?)",
            [
                ("operator", "operator2026", "ops"),
                ("platform-admin", "change-me", "admin"),
                ("observer", "observer", "readonly"),
            ],
        )
        db.executemany(
            "INSERT INTO deployments(service,owner,version,status,secret_note) VALUES(?,?,?,?,?)",
            [
                ("nova-api", "platform", "2.6.1", "healthy", "legacy deploy hook still enabled"),
                ("worker-sync", "automation", "1.14.0", "degraded", "local shell health check allowed"),
                ("billing-proxy", "finance", "4.3.2", "healthy", "internal token cached in config backup"),
                ("edge-renderer", "frontend", "0.9.8", "review", "template preview enabled for support team"),
            ],
        )
        db.execute(
            "INSERT INTO audit_log(actor, action, created_at) VALUES(?,?,?)",
            ("system", "Nova DevOps Console bootstrapped", datetime.utcnow().isoformat()),
        )
    db.commit()
    db.close()


BASE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }} | Nova DevOps Console</title>
  <link rel="stylesheet" href="/static/app.css">
</head>
<body>
<div class="shell">
  <aside>
    <div class="brand">Nova<span>DevOps Console</span></div>
    <nav>
      <a href="/">Overview</a>
      <a href="/deployments">Deployments</a>
      <a href="/search">Search</a>
      <a href="/renderer">Template Preview</a>
      <a href="/healthcheck">Healthcheck</a>
      <a href="/fetch">Webhook Fetcher</a>
      <a href="/config">Config Viewer</a>
    </nav>
  </aside>
  <main>
    <header>
      <div>
        <p class="eyebrow">Platform operations</p>
        <h1>{{ title }}</h1>
      </div>
      <div class="status">local lab</div>
    </header>
    {{ body|safe }}
  </main>
</div>
</body>
</html>
"""


def page(title: str, body: str) -> str:
    return render_template_string(BASE, title=title, body=body)


@app.route("/")
def overview():
    body = """
    <section class="grid">
      <div class="card"><span class="muted">Deployments</span><strong>4</strong><small>1 degraded</small></div>
      <div class="card"><span class="muted">Pipelines</span><strong>12</strong><small>3 queued</small></div>
      <div class="card"><span class="muted">Risk hints</span><strong>6</strong><small>local lab only</small></div>
    </section>
    <section class="panel">
      <h2>Operator brief</h2>
      <p>Nova is a fresh unseen local lab for Chimera Exploit-DL ranking tests. It looks like a small internal DevOps console.</p>
      <p class="muted">The goal is to compare manual prioritization against model-assisted exploit-family ranking. The flag is inside the container filesystem.</p>
    </section>
    """
    return page("Overview", body)


@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        try:
            user = conn().execute(query).fetchone()
            if user:
                session["user"] = user["username"]
                session["role"] = user["role"]
                return redirect(url_for("overview"))
            msg = "Invalid login"
        except Exception as exc:
            msg = f"Query error: {exc}"
    body = f"""
    <section class="panel">
      <form method="post">
        <input name="username" placeholder="username" value="operator">
        <input name="password" placeholder="password" type="password">
        <button>Sign in</button>
      </form>
      <p class="danger">{msg}</p>
    </section>
    """
    return page("Login", body)


@app.route("/deployments")
def deployments():
    rows = conn().execute("SELECT * FROM deployments ORDER BY service").fetchall()
    html = "".join(
        f"<tr><td>{r['service']}</td><td>{r['owner']}</td><td>{r['version']}</td><td>{r['status']}</td><td><a href='/deployment/{r['id']}'>details</a></td></tr>"
        for r in rows
    )
    return page("Deployments", f"<section class='panel'><table><tr><th>Service</th><th>Owner</th><th>Version</th><th>Status</th><th></th></tr>{html}</table></section>")


@app.route("/deployment/<int:deployment_id>")
def deployment_detail(deployment_id: int):
    row = conn().execute("SELECT * FROM deployments WHERE id=?", (deployment_id,)).fetchone()
    if not row:
        return page("Not found", "<section class='panel'>No deployment</section>"), 404
    body = f"""
    <section class="panel">
      <h2>{row['service']}</h2>
      <p><b>Owner:</b> {row['owner']}</p>
      <p><b>Version:</b> {row['version']}</p>
      <p><b>Status:</b> {row['status']}</p>
      <p><b>Internal note:</b> {row['secret_note']}</p>
      <p class="muted">This detail endpoint intentionally has weak access-control assumptions for lab use.</p>
    </section>
    """
    return page("Deployment Detail", body)


@app.route("/search")
def search():
    q = request.args.get("q", "")
    sql = f"SELECT service, owner, version, status FROM deployments WHERE service LIKE '%{q}%' OR owner LIKE '%{q}%'"
    try:
        rows = conn().execute(sql).fetchall()
        error = ""
    except Exception as exc:
        rows = []
        error = str(exc)
    result = "".join(f"<tr><td>{r['service']}</td><td>{r['owner']}</td><td>{r['version']}</td><td>{r['status']}</td></tr>" for r in rows)
    body = f"""
    <section class="panel">
      <form><input name="q" placeholder="Search deployment" value="{q}"><button>Search</button></form>
      <p class="danger">{error}</p>
      <table><tr><th>Service</th><th>Owner</th><th>Version</th><th>Status</th></tr>{result}</table>
    </section>
    """
    return page("Search", body)


@app.route("/renderer", methods=["GET", "POST"])
def renderer():
    template = request.form.get("template", "Release {{ release }} is ready for {{ team }}.")
    rendered = ""
    if request.method == "POST":
        rendered = render_template_string(template, release="nova-2.6.1", team="platform")
    body = f"""
    <section class="panel">
      <p class="muted">Preview release notification templates before sending to operators.</p>
      <form method="post">
        <textarea name="template">{template}</textarea>
        <button>Render preview</button>
      </form>
      <h3>Preview</h3>
      <pre>{rendered}</pre>
    </section>
    """
    return page("Template Preview", body)


@app.route("/healthcheck", methods=["GET", "POST"])
def healthcheck():
    host = request.form.get("host", "127.0.0.1")
    output = ""
    if request.method == "POST":
        command = f"curl -m 2 -I http://{host}"
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=5).decode(errors="ignore")
        except Exception as exc:
            output = str(exc)
    body = f"""
    <section class="panel">
      <p class="muted">Run a quick HTTP reachability check from the container.</p>
      <form method="post">
        <input name="host" value="{host}">
        <button>Run healthcheck</button>
      </form>
      <pre>{output}</pre>
    </section>
    """
    return page("Healthcheck", body)


@app.route("/fetch")
def fetch():
    url = request.args.get("url", "http://127.0.0.1:8080/healthz")
    data = ""
    try:
        with urlopen(url, timeout=3) as res:
            data = res.read(1000).decode(errors="ignore")
    except Exception as exc:
        data = str(exc)
    body = f"""
    <section class="panel">
      <form><input name="url" value="{url}"><button>Fetch webhook URL</button></form>
      <pre>{data}</pre>
      <p class="muted">Designed as a lab SSRF-style signal, not for external targets.</p>
    </section>
    """
    return page("Webhook Fetcher", body)


@app.route("/config")
def config():
    filename = request.args.get("file", "deployments.yaml")
    path = SEED_DIR / filename
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        content = str(exc)
    body = f"""
    <section class="panel">
      <form><input name="file" value="{filename}"><button>Open config</button></form>
      <pre>{content}</pre>
    </section>
    """
    return page("Config Viewer", body)


@app.route("/import-yaml", methods=["GET", "POST"])
def import_yaml():
    result = ""
    sample = (SEED_DIR / "deployments.yaml").read_text()
    raw = request.form.get("yaml", sample)
    if request.method == "POST":
        try:
            loaded = yaml.load(raw, Loader=yaml.Loader)
            result = repr(loaded)
        except Exception as exc:
            result = str(exc)
    body = f"""
    <section class="panel">
      <p class="muted">Legacy YAML import preview for deployment metadata.</p>
      <form method="post">
        <textarea name="yaml">{raw}</textarea>
        <button>Import preview</button>
      </form>
      <pre>{result}</pre>
    </section>
    """
    return page("YAML Import", body)


@app.route("/healthz")
def healthz():
    return {"status": "ok", "service": "nova-devops-console", "version": "2.6.1"}


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)
