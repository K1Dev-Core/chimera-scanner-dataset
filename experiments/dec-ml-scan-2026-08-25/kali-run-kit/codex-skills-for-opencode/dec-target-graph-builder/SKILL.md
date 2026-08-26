---
name: dec-target-graph-builder
description: Build a lightweight target-service-evidence graph from local Vulhub/Kali scan results so Dec can understand which evidence supports which vulnerability family.
---

# Dec Target Graph Builder

Use this skill when a run has multiple targets, services, ports, tools, and evidence files.

The goal is to create a simple graph-like map that Codex can later inspect without rereading every raw file.

## Graph Concepts

Nodes:

- `target`: one lab target, e.g. `shiro_CVE-2016-4437`
- `service`: host + port + protocol, e.g. `127.0.0.1:8081/http`
- `tool`: scanner/probe, e.g. `curl`, `nmap`, `nuclei`
- `evidence`: raw output file path
- `family`: expected candidate family, e.g. `shiro`
- `signal`: keyword or behavior, e.g. `rememberMe=deleteMe`

Edges:

- target `HAS_SERVICE` service
- service `SCANNED_BY` tool
- tool `WROTE` evidence
- evidence `CONTAINS_SIGNAL` signal
- signal `SUPPORTS_FAMILY` family
- target `VALIDATED_AS` family

## Required Artifact

Write:

```text
derived/target-evidence-graph.jsonl
```

Each line should be a simple edge:

```json
{"source":"shiro_CVE-2016-4437","edge":"HAS_SERVICE","target":"127.0.0.1:8081/http","evidence_file":"","notes":"local lab"}
{"source":"raw-curated/shiro_CVE-2016-4437/raw/shiro_rememberme_cookie_probe.txt","edge":"CONTAINS_SIGNAL","target":"rememberMe=deleteMe","evidence_file":"raw-curated/shiro_CVE-2016-4437/raw/shiro_rememberme_cookie_probe.txt","notes":"Shiro cookie fingerprint"}
{"source":"rememberMe=deleteMe","edge":"SUPPORTS_FAMILY","target":"shiro","evidence_file":"raw-curated/shiro_CVE-2016-4437/raw/shiro_rememberme_cookie_probe.txt","notes":"validated positive"}
```

## Signal Rules

Prefer signals that are:

- observable in raw evidence
- specific to a family
- safe/read-only
- reusable as ML features

Avoid signals that are:

- just the target name
- just the CVE name
- only a path created by the dataset
- copied from the expected label without scanner evidence

## Minimal Signals For Current Dec Work

- Shiro: `rememberMe=deleteMe`, `rememberMe`, `JSESSIONID` plus login redirect
- GoAhead: `Document Error`, `Access Error`, `GoAhead`, `goform`
- Spring: `spring`, `spring boot`, `springframework`, `actuator`, `Whitelabel Error Page`
- Joomla: `JoomlaAPI`, `joomla`, `api/index.php`
- Redis: `redis_version`
- Aria2: `aria2.getVersion`, JSON-RPC version response
- Grafana: `Grafana`, `/api/health`
- Tomcat: `Apache Tomcat`, `Catalina`
- Nginx: `Server: nginx`

## Summary

Mention in `SCAN-SUMMARY-TH.md`:

- which signals were found
- which family they support
- which target still lacks a specific signal

