# Review Patterns

Use this when the candidate skill includes executable code, remote sources, binaries, or broad permissions.

## Minimum Static Checks

Inspect:

- `SKILL.md`
- `agents/openai.yaml`
- all files under `scripts/`
- dependency manifests such as `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`
- shell files: `.ps1`, `.sh`, `.bat`, `.cmd`
- hidden files and config files
- symlinks/junctions and targets
- archives/binaries listed as assets

Search patterns:

- secrets: `api_key`, `token`, `password`, `credential`, `.env`, `auth.json`, `id_rsa`
- network: `curl`, `Invoke-WebRequest`, `fetch`, `requests`, `socket`, `wget`
- shell/process: `exec`, `spawn`, `Start-Process`, `cmd.exe`, `powershell`, `bash`
- persistence: `Run`, `Startup`, `schtasks`, `crontab`, profile files, shell rc files
- destructive ops: `Remove-Item`, `rm -rf`, `del`, `format`, `rmdir`, `git reset --hard`
- obfuscation: base64 decode plus execution, compressed payloads, char-code builders, hidden Unicode, eval-like behavior

## Block Conditions

Block installation when any of these are present and not clearly necessary, documented, and user-approved:

- secret exfiltration or reading credential stores
- hidden network calls during normal skill use
- install hooks that execute remote code
- self-modifying skill files or tampering with other skills
- persistence outside the skill folder
- broad filesystem writes outside approved shared skill paths
- misleading metadata that hides risky behavior
- binary-only behavior with no source or provenance
- unpinned remote instructions treated as authoritative

## Caution Conditions

Use `caution` when:

- the source is trusted but version/commit/hash is missing
- the skill needs network or shell access for a legitimate purpose
- the skill was ported from another agent platform
- only partial review was possible
- generated files are present but reproducible generation is not documented

## Safe Install Pattern

1. Keep candidate in a workspace or quarantine folder.
2. Run static review.
3. Record source, date, and decision.
4. Install into the shared skill hub only after `allow` or accepted `caution`.
5. Use a junction from `~/.codex/skills/<skill-name>` to the shared hub copy when possible.
6. Re-run the gate after any material update.
