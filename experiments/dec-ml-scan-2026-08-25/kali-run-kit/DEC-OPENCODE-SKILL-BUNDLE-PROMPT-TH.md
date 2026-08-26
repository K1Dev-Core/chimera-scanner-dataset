# Prompt ให้ opencode ใช้ Skill Bundle

ใน shared folder มี Codex skill ที่เตรียมไว้ให้:

```text
/media/sf_kali-share/dataset/dec-kali-validation-run-kit/codex-skills-for-opencode
```

ก่อนเริ่มงาน scan ให้ดูรายการ:

```bash
cd /media/sf_kali-share/dataset/dec-kali-validation-run-kit/codex-skills-for-opencode
cat README-TH.md
find . -maxdepth 2 -name SKILL.md -print
```

ใช้ skill เท่าที่เกี่ยวกับงาน ไม่ต้องเปิดทุกตัวถ้าไม่จำเป็น:

- ถ้าจะ import/install skill จากข้างนอก ให้อ่าน `agentic-skill-install-gate/SKILL.md` ก่อน
- ถ้าเป็น CTF/lab ทั่วไปและมี evidence แล้ว ให้อ่าน `ctf-auto-enrich/SKILL.md`
- ถ้า lab แปลก ยังไม่รู้หมวด ให้อ่าน `ctf-novel-auto-enrich/SKILL.md`
- ถ้าสงสัย SSTI ให้อ่าน `ctf-ssti-auto-enrich/SKILL.md`
- ถ้าเจอ GraphQL endpoint ให้อ่าน `ctf-graphql-introspection/SKILL.md`
- ถ้าต้อง format proof/flag/result ให้อ่าน `ctf-flag-reporter/SKILL.md`
- ถ้าต้องทำงานเป็นรอบ scan -> validate -> rescan ให้อ่าน `dec-scan-loop-harness/SKILL.md`
- ถ้าต้องทำแผนภาพความสัมพันธ์ target/service/evidence/family ให้อ่าน `dec-target-graph-builder/SKILL.md`
- ถ้ามีหลาย agent หรือจะแบ่ง role ใน opencode ให้อ่าน `dec-subagent-coordinator/SKILL.md`

ข้อกำหนดของโปรเจกต์ Dec สำคัญกว่า skill เสมอ:

- ทำเฉพาะ local Vulhub/Docker lab
- ห้ามสแกน public target
- ห้าม brute force
- ห้าม destructive exploit
- ห้าม persistence/webshell
- เก็บเฉพาะ raw-curated evidence ที่เป็นผล scan/probe จริง

ถ้า skill ใดแนะนำ action ที่เกิน scope ให้ข้าม แล้วจดใน `SCAN-SUMMARY-TH.md`
