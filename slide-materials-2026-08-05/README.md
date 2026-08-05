# Chimera / Exploit-DL — ชุดข้อมูลสำหรับทำสไลด์อัปเดตโปรเจกต์

โฟลเดอร์นี้แยกไว้สำหรับเปิดดูเวลาเตรียมสไลด์โดยเฉพาะ ไม่ใช่ raw dataset ทั้งหมด แต่เป็น “ข้อมูลสำคัญที่ควรหยิบไปอธิบาย” จากงานที่ทำไปแล้ว

## ควรเปิดไฟล์ไหนก่อน

1. `SLIDE_READY_SUMMARY_TH.md`  
   สรุปภาพรวมโปรเจกต์แบบภาษาไทย เอาไปทำสไลด์ได้ทันที

2. `DATASET_FEATURE_LABEL_GUIDE_TH.md`  
   อธิบายว่า dataset, feature, label ของเราคืออะไร มาจากไหน และใช้ยังไง

3. `tables/dataset_inventory.csv`  
   ตารางสรุปจำนวน dataset/rows/features สำหรับแคปลงสไลด์

4. `tables/vulnerability_family_distribution.csv`  
   ตาราง distribution ของ vulnerability family ที่มีตอนนี้

5. `tables/feature_groups.csv`  
   ตารางกลุ่ม feature ที่ควรพูดในพรีเซนต์

6. `tables/label_status.csv`  
   ตารางสถานะ label ปัจจุบันและ label ที่ควรเพิ่มต่อ

7. `OPEN_IMPORTANT_FILES.md`  
   รวม path ไฟล์ต้นทางที่ควรเปิด ถ้าต้องการดูข้อมูลจริงแบบละเอียด

## ข้อความสั้นสำหรับพูดในสไลด์

> Chimera / Exploit-DL เป็นระบบจัดอันดับ vulnerability/exploit family จาก fingerprint ของเป้าหมาย โดยนำข้อมูลจาก Vulhub, Docker lab ที่สร้างเอง, และผล scanner/passive fingerprint มาแปลงเป็น feature vector แล้วใช้ baseline model เพื่อช่วยแนะนำว่าควรตรวจช่องโหว่กลุ่มใดก่อน

## สถานะปัจจุบัน

- มี dataset seed จาก Vulhub จำนวน 66 labs
- มี training/ranking rows รวม 264 rows ในชุด expanded metadata
- มี feature matrix 84 columns ในชุด expanded metadata
- มี prototype dataset สำหรับ baseline model จำนวน 43 rows / 54 feature columns
- มี label แบบ weak/heuristic เช่น `is_recommended`, `is_top1`, `is_known_family`
- ขั้นต่อไปควรเพิ่ม label จริงแบบ `exploit_success_observed = 1/0`

## หมายเหตุสำคัญสำหรับนำเสนอ

ตอนนี้ dataset ใช้ได้ดีสำหรับ proof-of-concept และ baseline model แต่ยังไม่ควรเคลมว่าโมเดลแม่นจาก exploit จริงทั้งหมด เพราะ label ส่วนใหญ่ยังเป็น weak label จาก metadata, lab prior และ scanner signal

