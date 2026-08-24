# รายงานทดสอบ ML Ranking ของ Dec

เป้าหมายคือทดสอบว่า model ช่วยเรียง candidate exploit family ได้ดีกว่าการสุ่มหรือไล่ทีละตัวหรือไม่

## Dataset

- rows: 602
- targets: 43
- candidate families: 14
- label counts: `{"unknown": 562, "positive_family_match": 40}`

## Feature ที่ใช้

ใช้เฉพาะ feature ที่ไม่เฉลยคำตอบตรง ๆ:

- `candidate_product_match_score`
- `candidate_service_match_score`
- `candidate_port_match_score`
- `candidate_technology_match_score`
- `candidate_scanner_signal_score`
- `candidate_family(one-hot)`

feature ที่ตั้งใจไม่ใช้:

- `is_ground_truth_family`
- `candidate_cve_match_score`
- `candidate_validation_available`

## ผลเทียบกับ baseline

| Method | Top-1 hit | Top-3 hit | Top-5 hit | MRR |
| --- | ---: | ---: | ---: | ---: |
| ML logistic ranker | 1.000 | 1.000 | 1.000 | 1.000 |
| Heuristic weighted score | 1.000 | 1.000 | 1.000 | 1.000 |
| Random expected | 0.071 | 0.214 | 0.357 | n/a |

## คำวินิจฉัยเบื้องต้น

ผลรอบนี้ดีมากจนควรมองเป็น red flag มากกว่าชัยชนะสุดท้าย เพราะ ML และ heuristic ได้ Top-1 เท่ากันที่ 1.000 แปลว่า feature กลุ่ม `candidate_*_match_score` น่าจะมี signal ที่ใกล้กับ family label มากอยู่แล้ว

สรุปคือ model เรียงถูกบน dataset นี้ แต่ยังตอบไม่ได้เต็มที่ว่า generalize ไป target ใหม่จริงหรือไม่ ต้องทดสอบรอบถัดไปด้วย feature ที่อ่อนลง, negative controls, และ exploit validation จริง

## จุดที่ model ยังพลาด

- ไม่พบ target ที่ positive หลุดเกิน Top-3 ในรอบนี้

## ข้อควรระวัง

- label ยังเป็น weak label จาก family/lab identity ไม่ใช่ exploit success ทุกแถว
- metric สูงไม่ได้แปลว่า exploit ได้จริง ต้อง validate ด้วย manual PoC/Metasploit/sqlmap เพิ่ม
- ขั้นถัดไปควรเพิ่ม positive/negative controls และวัดกับ target ใหม่จาก Kali
