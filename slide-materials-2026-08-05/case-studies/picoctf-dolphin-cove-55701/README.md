# Case Study — picoCTF dolphin-cove login target

Target ที่ใช้ทดสอบ:

```text
http://dolphin-cove.picoctf.net:55701/login
```

เคสนี้ใช้เป็นตัวอย่างสำหรับ A/B test ระหว่าง:

- กลุ่ม A: ได้ URL อย่างเดียว
- กลุ่ม B: ได้ URL + Chimera model report

ข้อมูลในโฟลเดอร์นี้เป็น passive fingerprint + weak-prior ranking เท่านั้น ไม่ใช่ผลยืนยันว่า exploit สำเร็จ

## Fingerprint ที่เก็บได้

| Field | Value |
|---|---|
| target | `http://dolphin-cove.picoctf.net:55701/login` |
| status_code | `200` |
| title | `The New Twitter` |
| server | `Werkzeug/3.1.5 Python/3.12.4` |
| content_type | `text/html; charset=utf-8` |
| form_count | `1` |
| input_names | `password, username` |
| discovered_links | `/register`, `/static/login-register.css` |

## Ranked vulnerability families

| rank | family | score | เหตุผล |
|---:|---|---:|---|
| 1 | `auth-bypass` | 0.78 | มี login/register flow เป็น surface หลัก |
| 2 | `sqli` | 0.68 | มี username/password form ที่อาจเกี่ยวกับ query handling |
| 3 | `broken-access-control` | 0.62 | เว็บแนว social/account/session มักเกี่ยวกับ authorization checks |
| 4 | `xss` | 0.48 | เว็บแนว social อาจมีพื้นที่ post/profile แต่ยังไม่เห็นจากหน้า login |
| 5 | `sensitive-data-exposure` | 0.35 | เห็น framework/version header |
| 6 | `csrf` | 0.28 | มี state-changing form แต่ยังไม่เห็น token evidence |

## ใช้ในสไลด์ยังไง

เหมาะเอาไปใส่ในสไลด์หัวข้อ “Live Ranking Report / A/B Test Example”

ประโยคสั้น:

> จาก passive fingerprint ของหน้า login ระบบ Chimera จัดอันดับให้เริ่มตรวจ auth-bypass, SQLi และ broken access control ก่อน เพราะ surface หลักคือ login/register flow พร้อม username/password form

## Limitation

Ranking นี้เป็น safe weak-prior ranking จาก passive fingerprint เท่านั้น ยังไม่ใช่ exploit success label และไม่ควรใช้เป็นหลักฐานว่าช่องโหว่นั้นมีอยู่จริง

