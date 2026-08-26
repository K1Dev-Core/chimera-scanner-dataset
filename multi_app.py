# Multi-vuln demo target: a single Flask app whose routes replicate the HTTP
# fingerprints of MANY vulnerable/over-exposed components that nuclei templates
# detect (actuator, swagger, graphql, jenkins, tomcat-manager, phpmyadmin, ...).
# Port 8090.
from flask import Flask, Response, jsonify, request

app = Flask(__name__)


def html(b):
    return Response(b, mimetype="text/html")


# Spring Boot Actuator exposed
@app.route("/actuator")
@app.route("/actuator/health")
def act_health():
    return jsonify({"status": "UP", "components": {"db": {"status": "UP"}}})


@app.route("/actuator/env")
def act_env():
    return jsonify({"activeProfiles": ["prod"], "propertySources": [
        {"name": "server.ports", "properties": {"local.server.port": {"value": "8090"}}}]})


@app.route("/actuator/mappings")
def act_map():
    return jsonify({"contexts": {"application": {"mappings": {"dispatcherServlets": {"dispatcherServlet": [{"handler": "index()"}]}}}}})


@app.route("/heapdump")
def heapdump():
    return Response("JAVA PROFILE DUMP PLACEHOLDER", mimetype="application/octet-stream")


# Swagger / OpenAPI exposure
@app.route("/swagger-ui.html")
@app.route("/swagger-ui/index.html")
def swagger():
    return html("<html><head><title>Swagger UI</title></head><body>Swagger UI</body></html>")


@app.route("/v2/api-docs")
@app.route("/v3/api-docs")
def apidocs():
    return jsonify({"swagger": "2.0", "info": {"title": "API", "version": "1.0"}, "paths": {}})


# GraphQL introspection
@app.route("/graphql", methods=["GET", "POST"])
def graphql():
    if request.method == "POST":
        return jsonify({"data": {"__schema": {"types": [{"name": "Query", "fields": [{"name": "ping"}]}]}}})
    return html("<html><body>GraphQL</body></html>")


# Jenkins
@app.route("/jenkins")
@app.route("/login")
def jenkins():
    r = Response(html("<html><head><title>Dashboard [Jenkins]</title></head><body>Jenkins</body></html>"),
                 mimetype="text/html")
    r.headers["X-Jenkins"] = "2.440.3"
    r.headers["X-Hudson"] = "1.395"
    r.headers["X-Jenkins-Session"] = "abc"
    return r


# Apache Tomcat manager (basic auth prompt)
@app.route("/manager/html")
@app.route("/manager/status")
def tomcat():
    return Response("Unauthorized", status=401, headers={"WWW-Authenticate": 'Basic realm="Tomcat Manager Application"'})


# phpMyAdmin
@app.route("/phpmyadmin/")
@app.route("/phpmyadmin/index.php")
def phpmyadmin():
    return html("<html><title>phpMyAdmin</title><body>phpMyAdmin</body></html>")


# Apache server-status
@app.route("/server-status")
@app.route("/server-info")
def server_status():
    return Response("Apache Server Status", status=403)


# H2 / console
@app.route("/h2-console")
@app.route("/console")
def console_page():
    return html("<html><body>H2 Console</body></html>")


# Druid / Nacos / Solr admin
@app.route("/druid/index.html")
def druid():
    return html("<html><body>Druid Monitor</body></html>")


@app.route("/nacos")
def nacos():
    return html("<html><body>Nacos</body></html>")


@app.route("/solr")
def solr():
    return html("<html><body>Apache Solr</body></html>")


@app.route("/")
def index():
    return jsonify({"app": "chimera-multi-vuln-demo", "port": 8090})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8090, debug=False)
