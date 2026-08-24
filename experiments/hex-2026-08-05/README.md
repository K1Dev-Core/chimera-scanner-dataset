# Hex 2026-08-05 Import

โฟลเดอร์นี้รวมข้อมูลที่คัดจาก branch `Hex` เข้ามาใน `Dec` แบบไม่ merge ทั้ง branch

อ่านรายละเอียดที่:

`../../docs/status/HEX-BRANCH-PROGRESS-2026-08-05.md`

## โครงสร้าง

| path | ใช้ทำอะไร |
| --- | --- |
| `vulhub-cve-bulk/` | metadata จาก Vulhub 160 labs ใช้เลือก target เพิ่ม |
| `vulhub-expanded-metadata/` | metadata เพิ่มและ candidate label |
| `vulhub-redo/` | active scanner seed 8 labs |
| `active-scanner-suite/` | scanner suite summary และ target features |
| `multi-vuln-web/` | dataset ทดลองหลาย vulnerability family |
| `demo-feature-label-model/` | demo feature-label model pack |

ข้อมูลนี้เป็นข้อมูลเสริมและ weak label ควร normalize เข้า schema ปัจจุบันก่อนใช้ train รวมกับชุดหลัก
