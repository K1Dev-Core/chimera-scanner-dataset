from __future__ import annotations

import os
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, redirect, render_template_string, request, session, url_for


APP_ROOT = Path(__file__).parent
DB_PATH = APP_ROOT / "acme.db"
REPORT_DIR = APP_ROOT / "reports"

app = Flask(__name__)
app.secret_key = "chimera-local-lab-secret"


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            role TEXT,
            team TEXT
        );

        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY,
            hostname TEXT,
            owner TEXT,
            service TEXT,
            version TEXT,
            environment TEXT
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY,
            title TEXT,
            requester TEXT,
            priority TEXT,
            internal_note TEXT,
            status TEXT
        );

        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            author TEXT,
            body TEXT,
            created_at TEXT
        );
        """
    )
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO users(username,password,role,team) VALUES(?,?,?,?)",
            [
                ("helpdesk", "helpdesk2026", "analyst", "support"),
                ("admin", "rotate-me-later", "admin", "platform"),
                ("audit", "readonly", "auditor", "risk"),
            ],
        )
        conn.executemany(
            "INSERT INTO assets(hostname,owner,service,version,environment) VALUES(?,?,?,?,?)",
            [
                ("portal-web-01", "support", "Flask", "3.0.3", "prod"),
                ("db-core-01", "platform", "SQLite", "3.x", "prod"),
                ("legacy-vpn-01", "network", "OpenSSH", "8.x", "legacy"),
                ("billing-api-02", "finance", "Gunicorn", "21.x", "stage"),
            ],
        )
        conn.executemany(
            "INSERT INTO tickets(title,requester,priority,internal_note,status) VALUES(?,?,?,?,?)",
            [
                ("VPN user cannot login", "nina@acme.local", "high", "Check legacy-vpn-01 local admin fallback", "open"),
                ("Invoice export failed", "finance@acme.local", "medium", "Billing API token cached in reports folder", "open"),
                ("SSO redirect loop", "ops@acme.local", "low", "Temporary bypass flag exists for admin role", "triage"),
                ("Customer portal slow", "sales@acme.local", "medium", "Review WAF rule exceptions before Friday", "open"),
            ],
        )
        conn.execute(
            "INSERT INTO comments(author,body,created_at) VALUES(?,?,?)",
            ("system", "Welcome to Acme Support Portal. This lab is intentionally vulnerable.", datetime.utcnow().isoformat()),
        )
    conn.commit()
    conn.close()


BASE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }} | Acme Support Portal</title>
  <link rel="stylesheet" href="/static/app.css">
</head>
<body>
  <aside>
    <div class="brand">ACME<span>Support</span></div>
    <nav>
      <a href="/">Dashboard</a>
      <a href="/tickets">Tickets</a>
      <a href="/assets">Assets</a>
      <a href="/comments">Comments</a>
      <a href="/diagnostics">Diagnostics</a>
      <a href="/reports">Reports</a>
    </nav>
  </aside>
  <main>
    <header>
      <div>
        <p class="eyebrow">Internal service desk</p>
        <h1>{{ title }}</h1>
      </div>
      <div class="session">{{ session.get("user", "guest") }}</div>
    </header>
    {{ body|safe }}
  </main>
</body>
</html>
"""


def page(title: str, body: str) -> str:
    return render_template_string(BASE, title=title, body=body)


@app.route("/")
def dashboard():
    body = """
    <section class="grid">
      <div class="card"><b>Open tickets</b><strong>4</strong><small>2 high priority</small></div>
      <div class="card"><b>Managed assets</b><strong>4</strong><small>prod + legacy</small></div>
      <div class="card"><b>Risk queue</b><strong>7</strong><small>needs review</small></div>
    </section>
    <section class="panel">
      <h2>Operator note</h2>
      <p>This is a realistic local lab for Chimera / Exploit-DL. It is intentionally vulnerable and should only run on localhost.</p>
      <p>Try scanning the surface first, then let the model rank likely exploit families from the fingerprint.</p>
    </section>
    """
    return page("Dashboard", body)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        try:
            row = db().execute(query).fetchone()
            if row:
                session["user"] = row["username"]
                session["role"] = row["role"]
                return redirect(url_for("dashboard"))
            message = "Invalid username or password"
        except Exception as exc:
            message = f"Login query error: {exc}"
    body = f"""
    <section class="panel narrow">
      <form method="post">
        <label>Username <input name="username" value="helpdesk"></label>
        <label>Password <input name="password" type="password" value=""></label>
        <button>Sign in</button>
      </form>
      <p class="error">{message}</p>
    </section>
    """
    return page("Login", body)


@app.route("/tickets")
def tickets():
    q = request.args.get("q", "")
    query = f"SELECT * FROM tickets WHERE title LIKE '%{q}%' OR requester LIKE '%{q}%' ORDER BY priority DESC"
    try:
        rows = db().execute(query).fetchall()
        error = ""
    except Exception as exc:
        rows = []
        error = str(exc)
    items = "\n".join(
        f"<tr><td><a href='/ticket/{r['id']}'>#{r['id']}</a></td><td>{r['title']}</td><td>{r['requester']}</td><td>{r['priority']}</td><td>{r['status']}</td></tr>"
        for r in rows
    )
    body = f"""
    <section class="panel">
      <form class="search"><input name="q" placeholder="Search requester or title" value="{q}"><button>Search</button></form>
      <p class="error">{error}</p>
      <table><tr><th>ID</th><th>Title</th><th>Requester</th><th>Priority</th><th>Status</th></tr>{items}</table>
    </section>
    """
    return page("Tickets", body)


@app.route("/ticket/<int:ticket_id>")
def ticket_detail(ticket_id: int):
    row = db().execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    if not row:
        return page("Ticket not found", "<section class='panel'>No ticket</section>"), 404
    body = f"""
    <section class="panel">
      <h2>#{row['id']} {row['title']}</h2>
      <p><b>Requester:</b> {row['requester']}</p>
      <p><b>Priority:</b> {row['priority']}</p>
      <p><b>Status:</b> {row['status']}</p>
      <hr>
      <p><b>Internal note:</b> {row['internal_note']}</p>
      <p class="muted">This endpoint intentionally omits authorization checks for lab purposes.</p>
    </section>
    """
    return page("Ticket Detail", body)


@app.route("/assets")
def assets():
    rows = db().execute("SELECT * FROM assets ORDER BY environment, hostname").fetchall()
    items = "\n".join(
        f"<tr><td>{r['hostname']}</td><td>{r['owner']}</td><td>{r['service']}</td><td>{r['version']}</td><td>{r['environment']}</td></tr>"
        for r in rows
    )
    return page("Assets", f"<section class='panel'><table><tr><th>Host</th><th>Owner</th><th>Service</th><th>Version</th><th>Env</th></tr>{items}</table></section>")


@app.route("/comments", methods=["GET", "POST"])
def comments():
    if request.method == "POST":
        author = request.form.get("author", "anonymous")
        body = request.form.get("body", "")
        db().execute(
            "INSERT INTO comments(author,body,created_at) VALUES(?,?,?)",
            (author, body, datetime.utcnow().isoformat()),
        ).connection.commit()
        return redirect(url_for("comments"))
    rows = db().execute("SELECT * FROM comments ORDER BY id DESC").fetchall()
    comments_html = "\n".join(f"<div class='comment'><b>{r['author']}</b><p>{r['body']}</p><small>{r['created_at']}</small></div>" for r in rows)
    body = f"""
    <section class="panel narrow">
      <form method="post">
        <label>Name <input name="author" value="analyst"></label>
        <label>Comment <textarea name="body">Looks normal from the dashboard.</textarea></label>
        <button>Post comment</button>
      </form>
    </section>
    <section class="panel">{comments_html}</section>
    """
    return page("Comments", body)


@app.route("/diagnostics", methods=["GET", "POST"])
def diagnostics():
    output = ""
    host = request.form.get("host", "127.0.0.1")
    if request.method == "POST":
        cmd = f"ping -c 1 {host}"
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=4).decode(errors="ignore")
        except Exception as exc:
            output = str(exc)
    body = f"""
    <section class="panel narrow">
      <form method="post">
        <label>Host/IP <input name="host" value="{host}"></label>
        <button>Run ping</button>
      </form>
      <pre>{output}</pre>
    </section>
    """
    return page("Diagnostics", body)


@app.route("/reports")
def reports():
    files = "".join(f"<li><a href='/download?file={p.name}'>{p.name}</a></li>" for p in REPORT_DIR.glob("*"))
    return page("Reports", f"<section class='panel'><ul>{files}</ul></section>")


@app.route("/download")
def download():
    filename = request.args.get("file", "summary.txt")
    path = REPORT_DIR / filename
    try:
        data = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        return page("Download error", f"<section class='panel'><pre>{exc}</pre></section>"), 404
    return Response(data, mimetype="text/plain")


@app.route("/healthz")
def healthz():
    return {"status": "ok", "app": "acme-support-portal"}


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)
