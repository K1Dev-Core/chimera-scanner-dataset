---
name: ctf-auto-enrich
description: Enrich solved or nearly solved CTF challenges into reproducible, evidence-backed deliverables. Use when Codex has a CTF flag, exploit primitive, solve script, challenge URL, archive, command log, or partial writeup and the user asks to auto-enrich, verify, polish, document, hand off, produce final submission material, or ensure the flag was not guessed.
---

# CTF Auto Enrich

Use this skill after the primary solve path is known or strongly suspected. Keep the work grounded in artifacts: target responses, local files, scripts, command output, screenshots, decoded data, or logs.

## Workflow

1. Reconstruct the solved path from the raw evidence.
   - Identify challenge category and vulnerability class.
   - Name the exact primitive used: leak, auth bypass, code execution, file read, crypto recovery, parsing oracle, etc.
   - Separate confirmed facts from hypotheses.

2. Verify the flag from the real source.
   - Re-run the smallest command or script that obtains the flag.
   - Prefer a fresh account/session/input when the challenge allows it.
   - Do not report a flag unless it appears in verified output or a verified artifact.

3. Make the solve reproducible.
   - Save a minimal solve script when the exploit needs multiple requests, parsing, decoding, or nontrivial state.
   - Include hardcoded target constants only when they are challenge-provided or necessary.
   - Avoid local machine paths in scripts unless the challenge depends on a local attachment.
   - Use only required dependencies; prefer standard library for simple HTTP or parsing.

4. Enrich the explanation.
   - Explain why the payload or technique works, not only what command was run.
   - Include one benign proof before the final exploit when useful, such as `{{7*7}} -> 49` for SSTI.
   - Record negative checks that matter, such as "common flag files were empty" or "the archive had no usable attachment."

5. Produce the final answer in the user's requested format.
   - Include category/concept, reproducible steps, commands or solve script, and confirmed flag.
   - Keep the final concise; link deliverables from the workspace output directory when available.

## Deliverables

For projectless Codex tasks, place user-facing solve scripts, reports, or enriched notes in the task `outputs/` directory. Use `work/` only for probes, scratch scripts, and intermediate notes.

Name scripts predictably:

```text
outputs/solve_<challenge_slug>.py
outputs/writeup_<challenge_slug>.md
```

## Evidence Rules

- Preserve the exact final command used to verify the flag.
- Mention the runtime and dependency assumptions.
- If network or a remote service is unavailable, say which verification step could not be repeated.
- Never sanitize away exploit payloads that are necessary for reproducibility.
- Never invent source code, routes, files, or flags that were not observed.

## Optional Resources

Read `references/enrichment-checklist.md` when the solve is messy, multi-stage, or needs organizer-quality handoff.

Use `scripts/enrich_ctf_report.py` when you have raw notes or terminal output and want a first-pass Markdown skeleton to edit.
