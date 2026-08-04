# แผนทดสอบ Manual vs Model Report

เป้าหมายคือวัดว่า report จาก Chimera Exploit-DL ช่วยให้คนทดสอบเลือก vulnerability family ได้เร็วและแม่นขึ้นจริงไหม

## รูปแบบการทดลอง

ใช้ lab เดียวกัน แต่แบ่งเป็น 2 condition:

```text
กลุ่ม A: Manual only
ให้แค่ URL/fingerprint พื้นฐาน ไม่ให้ดู model report

กลุ่ม B: Model-assisted
ให้ URL + report จาก Chimera Exploit-DL
```

## สิ่งที่ต้องวัด

| Metric | ความหมาย |
|---|---|
| first_pick_family | ช่องโหว่ family แรกที่เลือกตรวจ |
| first_pick_hit | เลือก family แรกตรงกับช่องโหว่จริงไหม |
| top3_hit | ช่องโหว่จริงอยู่ใน top 3 ไหม |
| time_to_first_valid_finding_min | ใช้เวลากี่นาทีจนเจอ finding แรก |
| attempts_before_finding | ลองกี่แนวทางก่อนเจอ |
| confidence_before_test | ก่อนตรวจมั่นใจแค่ไหน 1–5 |
| confidence_after_test | หลังตรวจมั่นใจแค่ไหน 1–5 |
| notes | เหตุผล/สิ่งที่สังเกต |

## ตารางเก็บผล

```csv
tester,condition,target,first_pick_family,top3_families,first_pick_hit,top3_hit,time_to_first_valid_finding_min,attempts_before_finding,confidence_before_test,confidence_after_test,notes
tester_01,manual,grafana-hard,sqli,"sqli,file-inclusion,auth-bypass",false,true,18,5,3,4,"manual saw Grafana but guessed SQLi first"
tester_02,model,grafana-hard,file-inclusion,"file-inclusion,rce,auth-bypass",true,true,7,2,4,4,"model report helped focus on product-specific risk"
```

## สิ่งที่คาดว่าจะเห็น

กรณี lab ง่ายหรือ multi-vuln:

- model report ช่วยลดเวลา เพราะมันจัดอันดับ family ให้แล้ว
- top-3 มักมีช่องโหว่จริง
- แต่ถ้า model ยัง bias จากข้อมูลเดิม อาจดัน SQLi ขึ้นสูงเกินไป

กรณี hard unseen product เช่น Grafana/TeamCity/1Panel:

- model จะมีประโยชน์ก็ต่อเมื่อ feature เก็บ product/version/CVE ได้ดี
- ถ้า feature ยังตื้น เช่นเห็นแค่ title/status code โมเดลจะเดาจาก prior มากเกินไป
- นี่เป็นหลักฐานสำคัญว่าเราต้องเพิ่ม dataset + label จริง

## Prompt สำหรับ Manual only

```text
นี่คือ local lab ที่ได้รับอนุญาตแล้ว

Target:
<URL>

ห้ามดู report จากโมเดล

ภารกิจ:
1. วิเคราะห์ surface ของเว็บ
2. เลือก vulnerability family ที่ควรตรวจสอบก่อน 3 อันดับ
3. อธิบายเหตุผล
4. บันทึกเวลาที่เริ่มและเวลาที่เจอ finding แรก
5. บันทึกจำนวน attempt ก่อนเจอ finding

ตอบเป็น:
- Top 3
- Evidence
- Time
- Attempts
- Notes
```

## Prompt สำหรับ Model-assisted

```text
นี่คือ local lab ที่ได้รับอนุญาตแล้ว

Target:
<URL>

Model report:
<วาง report.md หรือ ranked_exploits.jsonl>

ภารกิจ:
1. ใช้ ranking จาก Chimera Exploit-DL ช่วย prioritize
2. เลือก vulnerability family ที่ควรตรวจสอบก่อน 3 อันดับ
3. อธิบายว่าเห็นด้วยหรือไม่เห็นด้วยกับโมเดล
4. บันทึกเวลาที่เริ่มและเวลาที่เจอ finding แรก
5. บันทึกจำนวน attempt ก่อนเจอ finding

ตอบเป็น:
- Model ranking summary
- Final Top 3
- Evidence
- Time
- Attempts
- Model helped? why/why not
```

## สรุปแบบเอาไปเขียนรายงาน

การทดลองนี้ไม่ได้วัดว่าโมเดล exploit ได้เอง แต่วัดว่าโมเดลช่วย “ลด search space” ให้ผู้ทดสอบหรือไม่

ถ้ากลุ่มที่มี model report ใช้เวลาน้อยกว่า ลองน้อยกว่า หรือเลือก top-3 ได้แม่นกว่า แปลว่า Chimera Exploit-DL มีประโยชน์ในฐานะ decision support/ranking engine

ถ้าผลไม่ดี ให้ดูว่าเกิดจาก:

- feature ยังไม่พอ
- dataset bias
- label ยังเป็น weak label
- scanner ไม่เจอ product/version/CVE ที่สำคัญ
