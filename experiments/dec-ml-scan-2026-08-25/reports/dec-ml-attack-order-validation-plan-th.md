# แผนทดสอบ ML Attack Order จากชุด Dec ML Scan

เอกสารนี้ต่อจาก `dec-ml-scan-ranking-report-th.md` เพื่อบอกว่าควรทดสอบอะไรต่อ หลังจากเราได้ผล ranking จาก scanner-derived features แล้ว

## เรากำลังไล่ตามแนวโปรเจกต์นี้อยู่ไหม

ใช่ แนวของ Dec ตอนนี้ตรงกับ pipeline ที่ควรเป็น:

1. `RECON`: เก็บผลจาก scanner เช่น nmap, curl probe, nikto, wapiti, nuclei
2. `FEATURE`: แปลงผล scan เป็น feature ที่ model อ่านได้
3. `ML DECISION`: ให้ model เรียง candidate family ว่าควรลองอะไรก่อน
4. `VALIDATION`: ตรวจว่า candidate ที่ model แนะนำตรงกับ expected vulnerability จริงหรือไม่
5. `FEEDBACK`: เอาผลถูก/ผิดกลับไปเพิ่ม label และปรับ feature

สิ่งที่ Dec ทำได้แล้วในรอบนี้คือข้อ 1-3 และเริ่มวัดข้อ 4 แบบ weak label แล้ว แต่ยังต้องเพิ่ม exploit validation แบบควบคุมใน local Vulhub เพื่อให้ label แข็งขึ้น

## Input ที่ ML ใช้จริง

ไฟล์ input หลักคือ `derived/candidate-family-features.csv`

โครงสร้างคือ 1 target ถูกขยายเป็นหลาย candidate family:

- `target_id`: target/lab ที่สแกน
- `candidate_family`: family ที่กำลังให้คะแนน เช่น `joomla`, `redis`, `spring`
- `positive_family`: weak label จากชื่อ lab/folder
- `label`: `positive_family_match` หรือ `negative_family`
- `title_alias_score`: title มีคำใบ้ตรง family แค่ไหน
- `server_alias_score`: server/header มีคำใบ้ตรง family แค่ไหน
- `nmap_alias_score`: nmap service line มีคำใบ้ตรง family แค่ไหน
- `body_alias_score`: status/probe text มีคำใบ้ตรง family แค่ไหน
- `port_score`: port ตรง pattern ของ family แค่ไหน
- `protocol_score`: protocol ตรง family แค่ไหน เช่น redis/aria2 เป็น non-http
- `http_tool_score`: มี evidence จาก tool HTTP เพิ่มไหม

สิ่งที่ไม่ควรใช้เป็น input จริง:

- `target_id`
- ชื่อ CVE ในชื่อ target
- `positive_family`
- `candidate_family` เดิมจาก `features.csv` แบบ target-level

เหตุผลคือ field เหล่านี้เฉลยคำตอบทางอ้อม ทำให้คะแนนดีเกินจริง แต่พอเจอ target ใหม่จะไม่ generalize

## ผลล่าสุดที่ต้องจำ

| วิธี | Top-1 | Top-3 | mean attempts |
| --- | ---: | ---: | ---: |
| ML logistic ranker | 0.759 | 0.862 | 2.586 |
| Scanner heuristic | 0.724 | 0.828 | 2.724 |
| Random expected | 0.037 | 0.111 | 14.000 |

คำอ่านคือ ML เรียงลำดับการโจมตีได้ดีกว่าสุ่มชัดเจน และดีกว่า heuristic เล็กน้อย แต่ยังไม่ใช่คำตอบสุดท้าย เพราะ label ตอนนี้ยังเป็น weak label

## Target ที่ควร validate ก่อน

ให้เริ่มจาก target ที่ ML พลาดเกิน Top-3 เพราะเป็นจุดที่ให้ข้อมูลย้อนกลับกับโมเดลดีที่สุด

| priority | target | weak label | ML rank | ทำไมควรทดสอบก่อน | evidence ที่ควรเก็บ |
| ---: | --- | --- | ---: | --- | --- |
| 1 | `joomla_CVE-2023-23752` | `joomla` | 17 | scanner evidence ไม่มีคำ Joomla ชัด ทำให้โมเดลหลุดหนัก | HTTP API/config response, nuclei/wapiti/nikto output, validation note |
| 2 | `spring_CVE-2022-22965` | `spring` | 13 | Spring/Tomcat ใช้ port/header คล้ายกันมาก | HTTP headers, framework fingerprint, safe PoC result |
| 3 | `shiro_CVE-2016-4437` | `shiro` | 12 | fingerprint หน้า login ไม่บอก Shiro ชัด | cookie/header/probe evidence, safe validation result |
| 4 | `goahead_CVE-2017-17562` | `goahead` | 4 | พลาดเฉียด Top-3 เพราะ port 8080 ชนหลาย family | server banner, path probe, nmap service evidence |

หลังจากนั้นค่อย validate target ที่ ML ทำถูก Top-1 เพื่อทำ positive controls:

- `redis_CVE-2022-0543`
- `aria2_rce`
- `grafana_CVE-2021-43798`
- `tomcat_CVE-2017-12615`
- `nginx_CVE-2017-7529`

## Agentic vs ML ต้องเทสยังไง

ให้วัดด้วย metric เดียวกัน ไม่ใช่เทียบจากความรู้สึก:

- `ML ranker`: เรียง candidate จาก probability
- `Agentic scanner heuristic`: agent อ่าน scanner evidence แล้วเลือก family ตาม rule
- `Fixed playbook`: ไล่ family ตามลำดับคงที่
- `Random expected`: สุ่ม candidate เป็น baseline

metric ที่ใช้:

- `Top-1`: family ที่ถูกอยู่ตัวแรกไหม
- `Top-3`: family ที่ถูกอยู่ใน 3 ตัวแรกไหม
- `mean attempts`: ต้องลองกี่ candidate โดยเฉลี่ยกว่าจะเจอ family ที่ถูก
- `failure cases`: target ไหนหลุด Top-3 และเพราะอะไร

ตอนนี้ ML ชนะ random และ fixed playbook แน่นอน แต่ยังชนะ agentic heuristic แค่เล็กน้อย จึงควรเก็บ validation label เพิ่มเพื่อดูว่า ML เริ่มชนะชัดขึ้นเมื่อข้อมูลจริงมากขึ้นหรือไม่

## สิ่งที่ต้องปรับให้แม่นขึ้น

1. เพิ่ม feature จาก scanner ที่เฉพาะ family มากขึ้น
   - cookie name
   - redirect path
   - framework-specific endpoint
   - default file/path ที่พบจริง

2. เพิ่ม negative controls
   - target ที่เปิด port เหมือนกันแต่ไม่ใช่ family นั้น
   - เช่น port 8080 ที่ไม่ใช่ Tomcat/Spring/Struts

3. แยก train/test ตาม target group เสมอ
   - ห้าม random split รายแถว เพราะ candidate rows ของ target เดียวกันจะรั่วข้าม train/test

4. เพิ่ม exploit validation label
   - `weak_label`: มาจากชื่อ lab
   - `validated_positive`: มี safe PoC/expected response ยืนยัน
   - `validated_negative`: ลองแล้วไม่ตรงหรือไม่มี evidence

## งานรอบ Kali ถัดไป

ให้ opencode/Kali ทำเฉพาะ local Vulhub เท่านั้น และเก็บ output กลับเข้า raw-curated:

1. เปิดทีละ target จาก validation queue
2. รัน scanner/fingerprint เพิ่มเฉพาะจุดที่ขาด
3. เก็บหลักฐานเป็นไฟล์ ไม่เก็บ cache/runtime/dependency
4. เติม label validation แยกจาก weak label
5. regenerate `candidate-family-features.csv`
6. rerun evaluator แล้วเทียบ Top-k/attempts ก่อนและหลัง

เป้าหมายคือทำให้ dataset ไม่ใช่แค่ "จำชื่อ lab ได้" แต่เริ่มเรียนจาก evidence ที่ scanner เห็นจริง
