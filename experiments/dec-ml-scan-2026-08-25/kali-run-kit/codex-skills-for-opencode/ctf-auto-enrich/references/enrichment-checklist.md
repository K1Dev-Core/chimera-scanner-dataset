# CTF Enrichment Checklist

Use this checklist for nontrivial challenges, team handoff, or when the final result needs stronger auditability.

## Classification

- Challenge name, category, points, target URL or attachment names.
- Dominant bug family and any secondary bug family.
- Trust boundary crossed by the exploit.
- Location of the flag: HTTP response, environment, file, database, binary output, blockchain state, etc.

## Reproducibility

- Fresh setup steps from a clean workspace.
- Commands to inspect attachments.
- Commands to start local services or connect to remotes.
- Exact exploit command or script invocation.
- Expected proof output before the flag.
- Expected final flag output.

## Script Quality

- Minimal dependencies.
- Clear constants at top: target URL, file paths, username/password, payload.
- No stale cookies, tokens, timestamps, or account IDs unless intentionally generated.
- Deterministic parsing with useful failure errors.
- Output only the important result by default; verbose mode is optional.

## Validation

- Re-run the final exploit after script cleanup.
- Confirm the flag matches the CTF flag pattern.
- Check that the solve does not depend on cached files or prior session state.
- Record any unavailable checks honestly.

## Final Report Shape

1. ประเภทและแนวคิดของช่องโหว่/โจทย์
2. ขั้นตอนวิเคราะห์แบบทำซ้ำได้
3. คำสั่งหรือ solve script ที่ใช้
4. Flag ที่ยืนยันแล้ว
