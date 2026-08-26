# AST10 Checklist

Source material:

- OWASP Agentic Skills Top 10 project page: `https://owasp.org/www-project-agentic-skills-top-10/`
- OWASP whitepaper requested by the user: `https://owasp.org/www-project-agentic-skills-top-10/assets/publications/ast10-top10-whitepaper-2.pdf`
- OWASP GitHub repository: `https://github.com/OWASP/www-project-agentic-skills-top-10`

Use this as a pre-install checklist. It is adapted for Codex skills and local shared-skill hubs.

## Decision Levels

- `block`: do not install or link the skill until fixed or explicitly overridden.
- `caution`: install only after telling the user the residual risk.
- `note`: record the risk but do not stop install.

## AST01 Malicious Skills

- Look for instructions that exfiltrate secrets, bypass user approval, hide behavior, persist outside the skill folder, tamper with other skills, or disable security controls.
- Block when scripts or instructions attempt credential theft, destructive actions, covert network calls, persistence, obfuscation, or self-modification.
- Mitigate with static review, known-source provenance, hashes, and no execution during review.

## AST02 Supply Chain Compromise

- Check origin, maintainer, commit/tag, archive source, dependency manifests, install scripts, and recent unexpected changes.
- Block unknown remote code with install hooks, binary blobs, or dependency fetches that cannot be traced.
- Mitigate with pinned commits, verified upstreams, registry transparency when available, and local review before linking.

## AST03 Over-Privileged Skills

- Check whether the skill asks for broad filesystem, shell, network, credential, browser, or external-account access beyond its stated task.
- Block skills that request blanket access like whole home-directory writes, unrestricted shell execution, or secret-store reads without a narrow use case.
- Mitigate with least privilege, scoped paths, explicit user approval before mutating commands, and documented permission boundaries.

## AST04 Insecure Metadata

- Review YAML/frontmatter, `agents/openai.yaml`, manifests, package metadata, and generated descriptions.
- Block metadata that impersonates trusted vendors, hides dangerous behavior in benign descriptions, contains parser tricks, or smuggles tool instructions into fields not meant as instructions.
- Mitigate with safe parsing, exact naming, no misleading display names, and consistency between description and actual files.

## AST05 Untrusted External Instructions

- Check whether the skill loads live URLs, remote docs, model prompts, or unpinned content and treats them as instructions.
- Block skills that automatically obey remote content or prompt-like text from websites without source pinning and instruction-boundary handling.
- Mitigate with source inventory, content pinning, quotes/summaries as data, and explicit rules that remote text cannot override system/developer/user instructions.

## AST06 Weak Isolation

- Check whether scripts run outside sandbox, use host-mode containers, launch background services, write global config, or alter PATH/profile files.
- Block install flows that require host-level execution, startup persistence, or broad environment mutation without a clear need.
- Mitigate with workspace-local execution, containers/sandboxes, no background helpers unless user-approved, and narrow cleanup instructions.

## AST07 Update Drift

- Check whether the skill auto-updates, pulls latest branches, downloads fresh scripts, or has no recorded version.
- Caution or block when behavior can change after review.
- Mitigate with pinned versions, hashes, changelog review, and re-running this gate on every material update.

## AST08 Poor Scanning

- Check beyond simple keyword matching: read instructions, metadata, scripts, hidden files, generated assets, and cross-file behavior.
- Caution when only a shallow scan was possible.
- Mitigate with semantic review plus pattern searches for shell, network, credentials, filesystem mutation, encoded payloads, and prompt injection.

## AST09 No Governance

- Check whether the install leaves no inventory record, no owner/source, no review result, or unclear purpose.
- Caution when a skill is installed without provenance or a route for future maintenance.
- Mitigate by recording source, date, reviewer/agent, decision, and location in the shared skill hub or workspace notes.

## AST10 Cross-Platform Reuse

- Check whether a skill was ported from Claude/OpenClaw/Cursor/VS Code and lost security metadata, permission constraints, or trust boundaries.
- Caution or block when a ported skill retains incompatible assumptions such as automatic hook execution or broader tool permissions.
- Mitigate by translating permissions and metadata explicitly for Codex, then re-reviewing as a Codex-native skill.
