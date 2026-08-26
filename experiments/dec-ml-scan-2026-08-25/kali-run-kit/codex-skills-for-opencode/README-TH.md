# Codex Skills สำหรับ opencode ฝั่ง Kali

โฟลเดอร์นี้เป็นชุด skill ที่คัดมาให้ opencode ใช้ช่วยงาน Dec ML validation scan และ CTF/pentest evidence collection

## วิธีใช้

ให้ opencode อ่าน skill ที่เกี่ยวข้องก่อนทำงาน แล้วใช้เป็นแนวทาง ไม่ต้อง import ทุกตัวพร้อมกันถ้าไม่จำเป็น

```bash
cd /media/sf_kali-share/dataset/dec-kali-validation-run-kit/codex-skills-for-opencode
find . -maxdepth 2 -name SKILL.md -print
```

ถ้าจะใช้ skill ใด ให้เปิดอ่าน:

```bash
cat <skill-name>/SKILL.md
```

## Skill ที่ส่งให้

- `agentic-skill-install-gate`: ใช้ตรวจความเสี่ยงก่อน import/install skill จากแหล่งอื่น
- `ctf-auto-enrich`: ใช้ enrich ผล CTF/lab ที่มีหลักฐานแล้วให้เป็นรายงานซ้ำได้
- `ctf-novel-auto-enrich`: ใช้ triage challenge/lab ที่ยังไม่รู้ว่าเข้าหมวดไหน
- `ctf-ssti-auto-enrich`: ใช้กับ web target ที่สงสัย SSTI
- `ctf-graphql-introspection`: ใช้กับ GraphQL endpoint ที่อาจเปิด introspection
- `ctf-flag-reporter`: ใช้ format ผลลัพธ์/flag/proof แบบสะอาด
- `dec-scan-loop-harness`: ใช้คุม loop scan -> evidence -> validation -> rescan แบบประหยัดเวลา
- `dec-target-graph-builder`: ใช้สร้าง graph เบา ๆ ว่า target/service/tool/evidence/signal/family เชื่อมกันยังไง
- `dec-subagent-coordinator`: ใช้แบ่งงาน scan-runner/evidence-reader/validator/curator/summarizer ถ้ามี sub-agent หรือทำทีละ role ใน session เดียว

## ข้อกำหนดสำหรับโปรเจกต์ Dec

- ใช้เฉพาะ local Vulhub/Docker lab
- ห้ามสแกน public target
- ห้าม brute force, destructive exploit, persistence หรือ webshell
- เก็บเฉพาะ raw-curated evidence ที่เป็นผล scan/probe จริง
- ถ้า skill แนะนำ action ที่เกิน scope ให้ข้ามและจดใน summary

## Skill ที่ไม่ส่ง

- `tctt-2026-ctfd-replay` ไม่ได้ส่ง เพราะเป็น skill เฉพาะงานแข่ง ไม่เกี่ยวกับ Dec dataset
- skill ระบบ/ปลั๊กอินที่ไม่เกี่ยวกับ scan ไม่ได้ส่ง เพื่อลด noise
