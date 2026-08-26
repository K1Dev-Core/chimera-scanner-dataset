---
name: dec-subagent-coordinator
description: Coordinate multiple opencode/sub-agent roles for Dec local scanning while keeping outputs consistent and safe.
---

# Dec Sub-Agent Coordinator

Use this skill when the platform can run multiple agents or when one agent wants to simulate separate roles.

The goal is to split work without losing schema quality.

## Roles

Use these roles:

- `scan-runner`: starts/stops local labs and runs safe commands.
- `evidence-reader`: reads raw outputs and extracts observable signals.
- `validator`: writes `validation-results.jsonl` status and confidence.
- `curator`: removes cache/runtime/dependency files from output.
- `summarizer`: writes Thai summary and next-scan recommendation.

If real sub-agents are unavailable, do these roles sequentially in one opencode session.

## Handoff Contract

Every role must write machine-readable notes under:

```text
logs/<role>.md
```

Use this format:

```text
# role-name

## Done
- ...

## Evidence
- path: ...
- signal: ...

## Blockers
- ...

## Next
- ...
```

## Coordination Rules

- The `scan-runner` never decides final labels alone.
- The `evidence-reader` must cite file paths for every signal.
- The `validator` must not use target name, CVE name, or folder name as evidence.
- The `curator` must remove cache/runtime/dependency only inside the current output folder.
- The `summarizer` must report uncertainty honestly.

## Parallelization

If multiple agents are available:

- Agent A: Spring deep fingerprint scan.
- Agent B: Shiro/GoAhead quick confirmation.
- Agent C: positive controls and output/schema validation.

Merge outputs only after checking:

- no duplicate JSONL rows for the same target unless intentionally replaced
- every evidence_file exists
- `destructive_action` is false
- raw-curated has no forbidden cache/runtime/dependency files

## Stop Conditions

Stop and ask for help if:

- the target appears to be public/non-local
- a tool recommends destructive exploitation
- the lab requires credentials/brute force
- Docker/lab setup would take most of the timebox

## Final Output

The coordinator is done when these exist:

```text
validation-results.jsonl
SCAN-SUMMARY-TH.md
derived/target-evidence-graph.jsonl
logs/scan-runner.md
logs/evidence-reader.md
logs/validator.md
logs/curator.md
logs/summarizer.md
```

