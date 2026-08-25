# สรุปความคืบหน้า branch Hex - 2026-08-05

ไฟล์นี้สรุปว่าเราเอาอะไรจาก `origin/Hex` เข้ามาใน `Dec` แล้วบ้าง โดยไม่ได้ merge ทั้ง branch

## ทำไมไม่ merge `Hex` ทั้งก้อน

`Hex` มีงานทดลองที่มีประโยชน์ แต่ถ้า merge ตรง ๆ จะเสี่ยงและทำให้ `Dec` อ่านยาก เพราะ:

- มีการลบ generated dataset และเอกสารบางส่วนที่ `Dec` ใช้อยู่
- มี path dataset ลึกมากจน Windows เจอปัญหา `Filename too long`
- บาง record เป็น metadata หรือ weak label ไม่ใช่ผล scan จริง
- มี demo labs, slide material, fresh lab source code และ dataset records ปนกัน

ดังนั้นใน `Dec` เรานำเข้าเฉพาะส่วนที่ compact และใช้ต่อได้ง่าย ได้แก่ records, feature tables, manifests และ raw evidence ที่คัดแล้ว

## ของที่ import จาก `Hex`

| path | ใช้ทำอะไร |
| --- | --- |
| `experiments/hex-2026-08-05/vulhub-cve-bulk/` | metadata จาก Vulhub 160 labs, feature seed, weak label, rank candidates และ feature matrix |
| `experiments/hex-2026-08-05/vulhub-expanded-metadata/` | metadata เพิ่มและ candidate label ฝั่ง exploit |
| `experiments/hex-2026-08-05/vulhub-redo/` | active scanner seed 8 labs มี labels/features แต่ยังไม่เอา raw tree ทั้งก้อน |
| `experiments/hex-2026-08-05/active-scanner-suite/` | สรุป scanner suite records และ target features |
| `experiments/hex-2026-08-05/multi-vuln-web/` | dataset ทดลองหลาย vulnerability family สำหรับ exploit ranking |
| `experiments/hex-2026-08-05/demo-feature-label-model/` | ชุด demo feature-label model พร้อม report/table ขนาดเล็ก |
| `dataset/raw-curated/hex-exp-2026-08-05/` | raw scanner/manual PoC outputs ที่คัดแล้วจาก 12 experimental targets |

## สถานะของ `Hex` ตอนที่ดึงมา

- branch head ของ `Hex`: `a471f55 Add bulk Vulhub CVE dataset and active scanner suite`
- bulk Vulhub CVE dataset: 160 labs, 640 training/ranking rows, 117 feature columns, 1120 total records
- Vulhub redo active scan seed: 8 labs ใช้ `naabu`, `nmap`, `httpx`, `nuclei`, `nikto`
- multi-vulnerability web dataset: มี records และ feature matrix สำหรับทดลอง exploit ranking
- demo feature-label model pack: มีตาราง/report เล็ก ๆ สำหรับอธิบาย pipeline
- fresh lab ideas ที่ยังไม่ได้ import: Acme support portal, Nova DevOps console, Grafana CVE-2024-9264, TeamCity CVE-2024-27198

## ตรวจซ้ำจาก `origin/Hex` วันที่ 2026-08-25

ตรวจด้วย `git ls-remote`, `git fetch origin Hex:refs/remotes/origin/Hex` และอ่าน tree โดยไม่ checkout branch อื่น ยืนยันว่าเรายังอยู่บน `Dec`

สถานะ remote:

- `origin/Dec`: `1f26ea88208617325b0b70c1d24cfe1b7ef25d41`
- `origin/Hex`: `a471f557fc01e8732e259be0b0b8d9524d69b6db`

สรุป tree ของ `Hex`:

| top-level path | จำนวนไฟล์โดยประมาณ | ความหมาย |
| --- | ---: | --- |
| `chimera-tools-name-date-2026-08-05-vulhub-cve-bulk/` | 1452 | bulk metadata/README/compose map จาก Vulhub 160 labs |
| `chimera-tools-name-date-2026-08-05-vulhub-redo/` | 160 | active scan seed 8 labs |
| `chimera-tools-name-date-2026-08-05-multi-vuln-web/` | 146 | multi-vulnerability web experiment และ baseline model |
| `chimera-tools-name-date-2026-08-05-active-scanner-suite/` | 55 | active scanner suite 2 local labs |
| `fresh-labs/` | 26 | lab source code ใหม่ เช่น Acme, Nova, Grafana, TeamCity |
| `demo-feature-label-model-2026-08-05/` | 11 | demo feature-label model pack |

ข้อสรุป:

- ไม่ควร merge `Hex` ทั้ง branch เพราะ diff แสดงว่า Hex จะลบ/ย้ายไฟล์ Dec หลักจำนวนมาก รวมถึง generated dataset, docs และ scripts
- สิ่งที่ควรดึงต่อคือ metadata/target candidate ที่ compact และ active scanner features ที่ normalize แล้ว
- สิ่งที่ยังไม่ควรดึงคือ raw tree ทั้งก้อน, folder ที่มี output runtime เยอะ, และ lab source code ที่ยังไม่ผ่าน schema Dec

ไฟล์ shortlist ที่สร้างไว้สำหรับรอบถัดไป:

```text
experiments/dec-ml-scan-2026-08-25/hex-next-target-candidates.csv
```

ไฟล์นี้เลือก 20 targets จาก bulk Vulhub metadata เพื่อเพิ่ม product/family ใหม่ให้ Dec ก่อนนำไปสแกนจริงใน Kali

## ใช้ของจาก `Hex` ใน `Dec` ยังไง

ให้มองของจาก `Hex` เป็นข้อมูลเสริม ไม่ใช่ dataset หลัก

ใช้ได้ดีสำหรับ:

- เลือก target รอบถัดไป
- หา feature vocabulary เพิ่ม
- ดู weak label เบื้องต้น
- วิเคราะห์ scanner coverage
- ทำตัวอย่าง demo/ranking

ยังไม่ควรใช้เป็น ground truth สุดท้าย เพราะ:

- `label-candidates` และ `exploit-labels` หลายตัวมาจาก lab identity จึงเป็น weak label
- `feature-seeds` บางตัวอาจเฉลยคำตอบ เช่น target name, CVE string, lab name
- record จาก `Hex` ควร normalize เข้า schema ปัจจุบันของ `Dec` ก่อนนำไป train รวมกับชุดหลัก

## ขั้นตอนต่อไป

ใช้ไฟล์นี้เพื่อเลือก target เพิ่ม:

`experiments/hex-2026-08-05/vulhub-cve-bulk/records/lab-index.jsonl`

แนวทางคือเลือก 10-20 targets ที่น่าสแกนต่อใน Kali แล้วเก็บ output รอบใหม่เป็น `raw-curated` package แยก จากนั้นค่อย normalize เข้า schema ของ `Dec`
