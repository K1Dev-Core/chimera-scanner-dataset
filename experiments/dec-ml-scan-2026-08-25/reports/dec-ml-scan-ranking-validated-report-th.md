# รายงานทดสอบ ML จากผลสแกน Kali 29 Targets

รายงานนี้ใช้ชุด `experiments/dec-ml-scan-2026-08-25/` เพื่อทดสอบว่า feature ที่ได้จาก scanner/fingerprint ช่วยเรียงลำดับ candidate family ได้ถูกต้องแค่ไหน

สิ่งสำคัญ: นี่ไม่ใช่การยืนยันว่า exploit สำเร็จ แต่เป็นการวัดว่า evidence จาก scanner พาเราไปหา family ที่ตรงกับ weak label ได้เร็วขึ้นหรือไม่

## Dataset

- target records: 29
- candidate rows: 64
- candidate families: 8
- label counts: `{"positive_family_match": 8, "negative_family": 56}`
- label mode: `validated`
- effective label rows: 8
- features file: `experiments\dec-ml-scan-2026-08-25\features-enriched.csv`

## Input ที่ใช้ทดสอบ

ใช้ข้อมูลจาก scanner/fingerprint เท่านั้น เช่น `title`, `server`, `x_powered_by`, `nmap_service_line`, `port`, `protocol_kind`, `evidence_text` ที่ตัด target/CVE leakage แล้ว และ flag ว่ามี output จาก tool ไหนบ้าง

ไม่ใช้ field ที่เฉลยคำตอบโดยตรง:

- `target_id`
- `candidate_family`
- `positive_family`
- `CVE in target_id`

## ผลเทียบ Baseline

| วิธี | Top-1 | Top-3 | Top-5 | MRR | mean attempts |
| --- | ---: | ---: | ---: | ---: | ---: |
| ML logistic ranker | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| Scanner heuristic | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| Random expected | 0.125 | 0.375 | 0.625 | n/a | 4.500 |

คำอ่าน: ถ้า Top-1 สูง แปลว่าโมเดล/heuristic เลือก family แรกถูกบ่อย ถ้า mean attempts ต่ำ แปลว่าต้องลอง candidate น้อยก่อนเจอตัวที่ถูก

## Feature Ablation

| Profile | Top-1 | Top-3 | mean attempts | ความหมาย |
| --- | ---: | ---: | ---: | --- |
| `current` | 1.000 | 1.000 | 1.000 | ใช้ scanner fingerprint หลักทั้งหมด: title/server/nmap/body/evidence/protocol/port/tool coverage |
| `no_body_text` | 1.000 | 1.000 | 1.000 | ตัด body text ออก แต่ยังใช้ evidence จาก scanner/raw-curated ที่ normalize แล้ว |
| `port_protocol_only` | 0.500 | 0.750 | 2.375 | ใช้แค่ port/protocol เพื่อดู baseline ที่หยาบมากและเสี่ยงชนกัน |
| `text_only` | 1.000 | 1.000 | 1.000 | ใช้เฉพาะคำจาก scanner evidence ไม่ใช้ port |

## จุดที่พลาดหรือเสี่ยง

- ไม่พบ target ที่ positive หลุดเกิน Top-3 ในรอบนี้

## สรุปสำหรับโปรเจกต์

- การเพิ่มผล scan มีผลจริง เพราะทำให้เราเห็นว่า fingerprint แบบไหนช่วย/ไม่ช่วยแยก family
- ค่าคะแนนที่ดีมากยังต้องระวัง เพราะ label ยังมาจากชื่อ lab/folder ของ Vulhub ไม่ใช่ exploit success
- สิ่งที่ควรทำต่อคือเพิ่ม negative controls และทำ exploit validation เฉพาะ target ที่มี PoC ชัด เช่น Joomla, Grafana, Redis, Aria2, ThinkPHP
