# รายงานทดสอบ ML จากผลสแกน Kali 29 Targets

รายงานนี้ใช้ชุด `experiments/dec-ml-scan-2026-08-25/` เพื่อทดสอบว่า feature ที่ได้จาก scanner/fingerprint ช่วยเรียงลำดับ candidate family ได้ถูกต้องแค่ไหน

สิ่งสำคัญ: นี่ไม่ใช่การยืนยันว่า exploit สำเร็จ แต่เป็นการวัดว่า evidence จาก scanner พาเราไปหา family ที่ตรงกับ weak label ได้เร็วขึ้นหรือไม่

## Dataset

- target records: 29
- candidate rows: 728
- candidate families: 26
- label counts: `{"positive_family_match": 28, "negative_family": 700}`
- label mode: `merged`
- effective label rows: 28

## Input ที่ใช้ทดสอบ

ใช้ข้อมูลจาก scanner/fingerprint เท่านั้น เช่น `title`, `server`, `x_powered_by`, `nmap_service_line`, `port`, `protocol_kind`, และ flag ว่ามี output จาก tool ไหนบ้าง

ไม่ใช้ field ที่เฉลยคำตอบโดยตรง:

- `target_id`
- `candidate_family`
- `positive_family`
- `CVE in target_id`

## ผลเทียบ Baseline

| วิธี | Top-1 | Top-3 | Top-5 | MRR | mean attempts |
| --- | ---: | ---: | ---: | ---: | ---: |
| ML logistic ranker | 0.786 | 0.857 | 0.893 | 0.833 | 2.500 |
| Scanner heuristic | 0.786 | 0.857 | 0.893 | 0.834 | 2.357 |
| Random expected | 0.038 | 0.115 | 0.192 | n/a | 13.500 |

คำอ่าน: ถ้า Top-1 สูง แปลว่าโมเดล/heuristic เลือก family แรกถูกบ่อย ถ้า mean attempts ต่ำ แปลว่าต้องลอง candidate น้อยก่อนเจอตัวที่ถูก

## Feature Ablation

| Profile | Top-1 | Top-3 | mean attempts | ความหมาย |
| --- | ---: | ---: | ---: | --- |
| `current` | 0.786 | 0.857 | 2.500 | ใช้ scanner fingerprint หลักทั้งหมด: title/server/nmap/body/protocol/port/tool coverage |
| `no_body_text` | 0.786 | 0.857 | 2.429 | ตัด body/probe text ออก เหลือเฉพาะ metadata ที่มักนิ่งกว่า |
| `port_protocol_only` | 0.429 | 0.571 | 4.321 | ใช้แค่ port/protocol เพื่อดู baseline ที่หยาบมากและเสี่ยงชนกัน |
| `text_only` | 0.714 | 0.750 | 4.571 | ใช้เฉพาะคำจาก scanner evidence ไม่ใช้ port |

## จุดที่พลาดหรือเสี่ยง

- `goahead_CVE-2017-17562` label=`goahead` แต่ ML วาง positive ไว้อันดับ 4; top3=adminer#1, appweb#2, drupal#3
- `joomla_CVE-2023-23752` label=`joomla` แต่ ML วาง positive ไว้อันดับ 17; top3=aria2#1, redis#2, tomcat#3
- `shiro_CVE-2016-4437` label=`shiro` แต่ ML วาง positive ไว้อันดับ 10; top3=adminer#1, appweb#2, drupal#3
- `thinkphp_5-rce` label=`thinkphp` แต่ ML วาง positive ไว้อันดับ 12; top3=adminer#1, appweb#2, drupal#3

## สรุปสำหรับโปรเจกต์

- การเพิ่มผล scan มีผลจริง เพราะทำให้เราเห็นว่า fingerprint แบบไหนช่วย/ไม่ช่วยแยก family
- ค่าคะแนนที่ดีมากยังต้องระวัง เพราะ label ยังมาจากชื่อ lab/folder ของ Vulhub ไม่ใช่ exploit success
- สิ่งที่ควรทำต่อคือเพิ่ม negative controls และทำ exploit validation เฉพาะ target ที่มี PoC ชัด เช่น Joomla, Grafana, Redis, Aria2, ThinkPHP
