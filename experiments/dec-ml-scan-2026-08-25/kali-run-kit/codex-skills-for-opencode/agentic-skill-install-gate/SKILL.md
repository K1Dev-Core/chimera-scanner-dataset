---
name: agentic-skill-install-gate
description: Pre-install security gate for Codex skills using the OWASP Agentic Skills Top 10. Use before installing, linking, syncing, or updating a skill from a file, folder, repository, URL, archive, or generated draft.
---

# Agentic Skill Install Gate

Use this skill before installing, linking, syncing, or materially updating any Codex skill. The goal is a fast security screen that catches malicious behavior, unsafe metadata, overbroad privileges, supply-chain risk, and governance gaps before the skill becomes available to future agents.

This gate does not replace user approval or sandbox permissions. It decides whether the skill is safe enough to install or whether the user should explicitly accept risk first.

## Workflow

1. Build the candidate inventory.
   - Identify source type: local folder, generated draft, Git repo, downloaded archive, marketplace/plugin, or copied skill.
   - List files that affect behavior: `SKILL.md`, `agents/openai.yaml`, scripts, references, assets, package manifests, shell helpers, binaries, archives, symlinks/junctions, and generated metadata.
   - Prefer static inspection first. Do not execute candidate scripts during the gate unless the user explicitly asks and the execution is sandboxed.

2. Run the AST10 screen.
   - Read [references/ast10-checklist.md](references/ast10-checklist.md).
   - Classify every finding as `block`, `caution`, or `note`.
   - When the candidate includes executable scripts, network access, secrets handling, or installation hooks, also read [references/review-patterns.md](references/review-patterns.md).

3. Decide.
   - `allow`: no blocking findings, and cautions are minor or already mitigated.
   - `caution`: install only after reporting the residual risk and mitigation.
   - `block`: do not install until the issue is removed or the user explicitly overrides with informed consent.

4. Install or update only after the decision.
   - If allowed, install into the shared skill hub when appropriate instead of duplicating task-local copies.
   - If caution/block, keep the candidate in a quarantine/workspace location and report what must change.
   - Preserve provenance: source URL/path, date checked, version/commit/hash when available, and the gate decision.

## Required Output

When this skill is used, report:

- `Decision`: `allow`, `caution`, or `block`
- `Top risks`: the most important AST IDs found
- `Checked`: files/surfaces inspected
- `Required changes`: concrete edits or mitigations before install
- `Provenance`: source path/URL and date checked

Keep the report short enough to be useful in the install flow.

## References

- Read [references/ast10-checklist.md](references/ast10-checklist.md) for the OWASP Agentic Skills Top 10 screening checklist.
- Read [references/review-patterns.md](references/review-patterns.md) for practical static-analysis patterns and block conditions.
