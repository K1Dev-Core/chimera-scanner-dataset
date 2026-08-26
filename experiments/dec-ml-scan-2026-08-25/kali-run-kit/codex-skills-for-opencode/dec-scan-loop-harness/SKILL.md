---
name: dec-scan-loop-harness
description: Run Dec local Vulhub/Kali validation work as a tight scan-evaluate-rescan loop. Use when opencode is collecting scanner evidence for ML ranking and must decide what to scan next without wasting time.
---

# Dec Scan Loop Harness

Use this skill when working on the Dec `chimera-scanner-dataset` Kali side.

The goal is not to scan everything. The goal is to improve ML ranking by adding evidence exactly where the model is uncertain or wrong.

## Safety Scope

- Only local Vulhub/Docker labs controlled by the user.
- No public IP/domain scanning.
- No brute force.
- No destructive exploit.
- No webshell or persistence.
- If a probe might change state, skip it and record why.

## Loop

Run work in short loops:

1. Read the queue.
2. Pick the highest-priority unresolved target.
3. Open only that lab/container.
4. Collect safe scanner/probe evidence.
5. Classify the target as `validated_positive`, `inconclusive`, `validated_negative`, or `not_run`.
6. Write one JSONL row immediately.
7. Add raw-curated evidence files.
8. Stop the lab/container before moving to the next target.
9. Summarize what should be rescanned next.

## Timebox Rules

For a 1-hour run:

- Spend 35-40 minutes on the highest-value unresolved target.
- Spend 10-15 minutes confirming one or two positive controls.
- Spend 10 minutes writing clean output and copying to shared folder.
- If a target does not reveal useful evidence after 15 minutes, mark it `inconclusive` and explain the missing fingerprint.

## Evidence Quality

Good evidence:

- A scanner output, header, body, error page, safe endpoint response, version banner, or read-only protocol response.
- Specific enough to distinguish the family from similar services.
- Stored under `raw-curated/<target_id>/raw/`.

Weak evidence:

- Port alone.
- Generic title like Login Page or Home Page.
- Scanner success without vulnerability/fingerprint evidence.
- A file path or target name that merely repeats the label.

Never use target_id, CVE text, folder name, or expected label as evidence.

## Output Contract

Each run must produce:

```text
validation-results.jsonl
SCAN-SUMMARY-TH.md
raw-curated/<target_id>/raw/*
logs/*
```

Each JSONL row must include:

```text
target_id, weak_label, validation_status, confidence, evidence_summary,
evidence_files, tools_used, safe_poc_used, destructive_action, notes
```

`destructive_action` must be `false`.

## Decision Rules

Use `validated_positive` when evidence specifically supports the expected family.

Use `inconclusive` when:

- The service is alive, but fingerprints are generic.
- Only port/title/basic response exists.
- The lab may be correct but the scanner did not expose a safe signal.

Use `not_run` when:

- The lab could not start.
- No reachable service was found.
- Required local target data is missing.

Use `validated_negative` only when evidence clearly contradicts the expected label.

## After The Run

Copy output to:

```text
/media/sf_kali-share/dataset/<run-id>
```

Then report only:

- output path
- status counts
- important evidence files
- blockers
- next target recommendation

