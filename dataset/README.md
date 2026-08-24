# Dataset Evidence

โฟลเดอร์นี้เก็บ evidence ดิบและ curated raw ที่ใช้ตรวจย้อนกลับจาก normalized records

## ใช้ก่อน

`raw-curated/`

เป็น raw scanner output ที่คัดเฉพาะผล scan จริง เช่น nuclei, nikto, nmap, httpx, naabu, wapiti, sqlmap, metasploit, zap

## ระวัง

`raw/` เป็น raw เก่าที่ยังไม่ได้ curate ทั้งหมด โดยเฉพาะ `raw/autorecon/**` มี path ยาวมากบน Windows จึงยังไม่ควรนำไปใช้ตรง ๆ หรือเพิ่มเข้า commit รอบใหม่

## แนวทางรอบถัดไป

ถ้าสแกน target ใหม่ ให้สร้าง raw curated package ใหม่ เช่น:

`raw-curated/dec-vulhub-YYYY-MM-DD/`

และเก็บเฉพาะผล scan จริง ไม่เก็บ cache, runtime dependency, `.pyc`, `__pycache__`, `.zaphome`, chromedriver หรือ `.jar` ที่เป็น dependency
