---
name: ctf-novel-auto-enrich
description: Triage and enrich unfamiliar, hybrid, or emerging CTF challenges that do not clearly fit existing ctf-* skills. Use when Codex has a CTF prompt, URL, archive, partial notes, odd category label, new platform primitive, or "misc but not really misc" challenge and must identify the best route, verify evidence, produce reproducible steps, and create reusable guidance for future similar challenges.
---

# CTF Novel Auto Enrich

Use this skill when the challenge shape is unclear or newer than the current CTF skill set. The goal is not to force every task into a known category; it is to preserve evidence, find the nearest useful technique, and turn the solve into a reusable handoff.

## Workflow

1. Build a compact evidence map.
   - Record the challenge title, category label, prompt text, URLs, files, service endpoints, and visible UI behavior.
   - Separate target material from platform noise such as leaderboard, hint UI, solved-by lists, and challenge metadata.
   - If the input contains only links, visit or query only in-scope CTF targets and keep exact URLs and responses needed for reproducibility.

2. Route before solving.
   - Use a specific skill when the dominant path is obvious: `ctf-web`, `ctf-reverse`, `ctf-pwn`, `ctf-crypto`, `ctf-forensics`, `ctf-ai-ml`, `ctf-osint`, `ctf-malware`, or `ctf-misc`.
   - Stay in this skill when the task combines several domains or suggests an emerging primitive, such as browser state puzzles, AI agent/tool misuse, Web3 frontend/backend mismatch, zk circuits, cloud metadata, CI/CD artifacts, weird protocol APIs, WASM-in-browser, or challenge-specific DSLs.
   - If another skill becomes clearly dominant after triage, switch to it and keep the evidence map.

3. Create a first-pass hypothesis table.
   - List 3-6 plausible solve paths with the observable evidence for each.
   - Include one cheap validation command or browser/API check per hypothesis.
   - Drop hypotheses quickly when evidence contradicts them; do not keep ornamental guesses.

4. Verify with smallest reproducible probes.
   - Prefer read-only checks first: static inspection, HTTP GET/OPTIONS, source maps, bundled JS search, strings, metadata, schema introspection, local parsing.
   - Escalate to active payloads only inside the CTF target scope.
   - Preserve exact commands, payloads, request bodies, filenames, hashes, and response snippets that prove the path.

5. Enrich into reusable output.
   - Produce the final answer with category/concept, reproducible steps, commands or solve script, and confirmed flag.
   - If the challenge reveals a reusable new technique, add a short "Future skill seed" section: trigger signals, key probes, common false leads, and a minimal verification recipe.
   - If no flag is reached, hand off the strongest remaining hypotheses and the next concrete probes instead of pretending the task is solved.

## Emerging Pattern Hints

Read `references/emerging-patterns.md` when the category label is vague, the challenge spans multiple surfaces, or the first route fails.

## Evidence Rules

- Never guess a flag. Report a flag only when it appears in verified output or a verified artifact.
- Keep target URLs in the prompt or notes when the challenge is web/API-based; do not replace them with nonexistent local file paths.
- Do not download or archive files unless the user asked for artifacts. Links and exact commands are often enough for agent handoff.
- State what could not be verified when network access, credentials, or platform state blocks a check.
