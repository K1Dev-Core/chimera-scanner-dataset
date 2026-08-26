from __future__ import annotations

# Vulnerable test target for the ChimeraScanner prototype.
# Serves on port 8080. Deliberately has a SQL injection (no parameterization).
import sqlite3

from flask import Flask, Response, request

app = Flask(__name__)

DB = "/tmp/chimera_vuln.db"


def init_db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER, name TEXT)")
    con.executemany("INSERT INTO users(id,name) VALUES(?,?)", [(1, "admin"), (2, "bob"), (3, "eve")])
    con.commit()
    con.close()


@app.route("/")
def index():
    return "ChimeraScanner vulnerable target. GET /items?id=1"


@app.route("/items")
def items():
    item_id = request.args.get("id", "1")  # noqa: S608 -> intentionally vulnerable
    con = sqlite3.connect(DB)
    # ponytail: intentionally vulnerable on purpose (a test target).
    rows = con.execute(f"SELECT id, name FROM users WHERE id = {item_id}").fetchall()
    con.close()
    if not rows:
        return "no rows", 404
    out = ", ".join(f"{r[0]}:{r[1]}" for r in rows)
    return Response(out, mimetype="text/plain")


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=8080, debug=False)
