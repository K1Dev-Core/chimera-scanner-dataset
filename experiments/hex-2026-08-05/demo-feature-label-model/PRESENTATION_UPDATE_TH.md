# Presentation Update — Chimera / Exploit-DL

## 1. เราทำอะไรเพิ่มในรอบนี้

รอบนี้เพิ่มข้อมูล target CTF ใหม่:

```text
http://lonely-island.picoctf.net:49776/
```

และรวมข้อมูล target ก่อนหน้า:

```text
http://dolphin-cove.picoctf.net:55701/login
```

ทั้งสองตัวถูกเก็บเป็น passive fingerprint + ranked vulnerability family report เพื่อใช้เป็นตัวอย่างใน A/B test และสไลด์ความคืบหน้า

## 2. ข้อมูลที่ได้จาก target ใหม่

| Field | Value |
|---|---|
| target | `http://lonely-island.picoctf.net:49776/` |
| status_code | `200` |
| title | `Login - picoCTF demo` |
| server | `Apache/2.4.66 (Debian)` |
| content_type | `text/html; charset=UTF-8` |
| form_count | `1` |
| input_names | `password, username, viewport` |
| discovered_links | `/register.php`, `/assets/css/styles.css` |

## 3. Ranking ที่ได้

| Rank | Family | Score | เหตุผล |
|---:|---|---:|---|
| 1 | auth-bypass | 0.78 | มี login/register flow เป็น surface หลัก |
| 2 | sqli | 0.68 | มี username/password form ที่อาจเกี่ยวกับ query handling |
| 3 | broken-access-control | 0.62 | เว็บมี account/session flow |
| 4 | xss | 0.48 | เว็บแนว user/session อาจมี surface เพิ่มหลัง login/register |
| 5 | sensitive-data-exposure | 0.35 | เห็น server/version header |
| 6 | csrf | 0.28 | มี form ที่เปลี่ยน state แต่ยังไม่เห็น token evidence |

## 4. จุดที่เอาไปเล่าในสไลด์

ประโยคสั้น:

> จาก URL เป้าหมาย ระบบ Chimera เก็บ passive fingerprint เช่น title, server, form และ input จากนั้นสร้าง candidate vulnerability family แล้วจัดอันดับว่าควรตรวจ auth-bypass, SQLi และ broken access control ก่อน

## 5. ทำไมข้อมูลนี้สำคัญ

- เป็น target ใหม่ที่ไม่ได้อยู่ใน training dataset เดิม
- มี login/register surface ชัดเจน เหมาะกับการทดสอบ A/B
- แสดงว่า report ของระบบอ่านง่ายและช่วยลด search space ให้ผู้ทดสอบ
- ใช้เป็นตัวอย่างว่าจากข้อมูลน้อย ๆ ระบบยังสร้าง prioritization report ได้

## 6. ข้อจำกัดที่ต้องพูดให้ชัด

Ranking นี้ยังเป็น passive/weak-prior report ไม่ใช่ proof ว่าช่องโหว่มีจริง และยังไม่ใช่ exploit success label

ขั้นต่อไปต้องเก็บ:

```text
exploit_success_observed = 1/0
time_to_success_seconds
attempt_count_before_success
manual_vs_model_group
```

เพื่อวัดว่า model-assisted testing ช่วยได้จริงแค่ไหน

