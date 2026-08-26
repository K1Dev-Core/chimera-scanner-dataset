# รายงานทดสอบ ML จากผลสแกน Kali 29 Targets

รายงานนี้ใช้ชุด `experiments/dec-ml-scan-2026-08-25/` เพื่อทดสอบว่า feature ที่ได้จาก scanner/fingerprint ช่วยเรียงลำดับ candidate family ได้ถูกต้องแค่ไหน

สิ่งสำคัญ: นี่ไม่ใช่การยืนยันว่า exploit สำเร็จ แต่เป็นการวัดว่า evidence จาก scanner พาเราไปหา family ที่ตรงกับ weak label ได้เร็วขึ้นหรือไม่

## Dataset

- target records: 29
- candidate rows: 783
- candidate families: 27
- label counts: `{"positive_family_match": 29, "negative_family": 754}`
- label mode: `merged`
- effective label rows: 29
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
| ML logistic ranker | 0.931 | 0.966 | 1.000 | 0.955 | 1.172 |
| Scanner heuristic | 0.931 | 1.000 | 1.000 | 0.960 | 1.103 |
| Random expected | 0.037 | 0.111 | 0.185 | n/a | 14.000 |

คำอ่าน: ถ้า Top-1 สูง แปลว่าโมเดล/heuristic เลือก family แรกถูกบ่อย ถ้า mean attempts ต่ำ แปลว่าต้องลอง candidate น้อยก่อนเจอตัวที่ถูก

## Feature Ablation

| Profile | Top-1 | Top-3 | mean attempts | ความหมาย |
| --- | ---: | ---: | ---: | --- |
| `current` | 0.931 | 0.966 | 1.172 | ใช้ scanner fingerprint หลักทั้งหมด: title/server/nmap/body/evidence/protocol/port/tool coverage |
| `no_body_text` | 0.931 | 1.000 | 1.103 | ตัด body text ออก แต่ยังใช้ evidence จาก scanner/raw-curated ที่ normalize แล้ว |
| `port_protocol_only` | 0.414 | 0.552 | 4.655 | ใช้แค่ port/protocol เพื่อดู baseline ที่หยาบมากและเสี่ยงชนกัน |
| `text_only` | 0.793 | 0.966 | 1.724 | ใช้เฉพาะคำจาก scanner evidence ไม่ใช้ port |

## จุดที่พลาดหรือเสี่ยง

- `appweb_CVE-2018-8715` label=`appweb` แต่ ML วาง positive ไว้อันดับ 5; top3=goahead#1, thinkphp#2, tomcat#3

## สรุปสำหรับโปรเจกต์

- การเพิ่มผล scan มีผลจริง เพราะทำให้เราเห็นว่า fingerprint แบบไหนช่วย/ไม่ช่วยแยก family
- ค่าคะแนนที่ดีมากยังต้องระวัง เพราะ label ยังมาจากชื่อ lab/folder ของ Vulhub ไม่ใช่ exploit success
- สิ่งที่ควรทำต่อคือเพิ่ม negative controls และทำ exploit validation เฉพาะ target ที่มี PoC ชัด เช่น Joomla, Grafana, Redis, Aria2, ThinkPHP
