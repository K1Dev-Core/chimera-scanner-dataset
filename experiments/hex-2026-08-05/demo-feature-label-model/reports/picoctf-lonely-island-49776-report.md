# รายงาน Chimera A/B Test Model

- generated_at: `2026-08-05T04:33:39.202638+00:00`
- target: `http://lonely-island.picoctf.net:49776/`
- status_code: `200`
- title: `Login - picoCTF demo`
- server: `Apache/2.4.66 (Debian)`
- content_type: `text/html; charset=UTF-8`
- form_count: `1`
- input_names: `password, username, viewport`
- discovered_links: `http://lonely-island.picoctf.net:49776/assets/css/styles.css`, `http://lonely-island.picoctf.net:49776/register.php`

## Vulnerability families ที่ model จัดอันดับ

| rank | family | score | เหตุผล |
| ---: | --- | ---: | --- |
| 1 | `auth-bypass` | 0.78 | หน้า login/register เป็น attack surface หลักที่เห็น |
| 2 | `sqli` | 0.68 | form username/password อาจเกี่ยวกับ backend query handling |
| 3 | `broken-access-control` | 0.62 | flow แบบ account/session มักมีจุดเสี่ยงด้าน authorization |
| 4 | `xss` | 0.48 | social/profile surface เป็นไปได้ แต่ยังไม่เห็นจาก login page |
| 5 | `sensitive-data-exposure` | 0.35 | server/version header เปิดเผยข้อมูลบางส่วน ต้องมี evidence เพิ่ม |
| 6 | `csrf` | 0.28 | มี state-changing form แต่ยังไม่พบหลักฐาน token |

## ข้อจำกัด

รายงานนี้เป็นตัวช่วยจัดลำดับจาก passive fingerprint เท่านั้น ใช้บอกว่าควรตรวจอะไรก่อน ไม่ใช่ proof ว่า exploit ได้จริง
