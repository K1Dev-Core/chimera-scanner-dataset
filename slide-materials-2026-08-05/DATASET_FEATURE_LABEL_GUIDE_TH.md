# Dataset / Feature / Label Guide

ไฟล์นี้อธิบายว่าถ้าจะดูข้อมูลของโปรเจกต์ Chimera / Exploit-DL ควรดูจากไหน และควรคิดเป็น feature/label ยังไง

## 1. Dataset คืออะไรในงานนี้

ในโปรเจกต์นี้ 1 แถวของ dataset ไม่ได้หมายถึงแค่ “หนึ่งเว็บ” เสมอไป แต่หมายถึง:

> หนึ่ง target/lab + หนึ่ง candidate vulnerability family ที่ระบบกำลังพิจารณา

ตัวอย่าง:

```csv
lab_id,product,candidate_exploit_family,rank,rank_score,is_recommended
bwapp,bWAPP,command-injection,1,0.815,1
bwapp,bWAPP,sqli,2,0.720,1
```

แปลว่า target เดียวกันสามารถมี candidate หลายแบบ เพื่อให้ model เรียนรู้ว่าควรจัดอันดับอะไรสูงกว่า

## 2. ควรดูข้อมูลจากไฟล์ไหน

### ไฟล์คนอ่าน

```text
chimera-tools-name-date-2026-08-05-multi-vuln-web/derived/training_examples.csv
```

ใช้ดูข้อมูลก่อนแปลงเป็นตัวเลข เช่น product, target URL, scanner evidence, service text, rank score

### ไฟล์ที่โมเดลอ่าน

```text
chimera-tools-name-date-2026-08-05-multi-vuln-web/derived/feature_matrix.csv
```

เป็นข้อมูลที่แปลงเป็นตัวเลขแล้ว เช่น one-hot encoding และ count features

### ไฟล์ชุดใหญ่จาก Vulhub

```text
chimera-tools-name-date-2026-08-05-vulhub-expanded-metadata/derived/training_examples.csv
chimera-tools-name-date-2026-08-05-vulhub-expanded-metadata/derived/feature_matrix.csv
```

ใช้ดูข้อมูลจาก CVE/lab จำนวนมากขึ้น เพื่อขยาย training data

## 3. Data Source

ข้อมูลมาจาก:

| Source | ข้อมูลที่ได้ | ใช้ทำอะไร |
|---|---|---|
| Vulhub | CVE, product, docker image, port, lab name | สร้าง metadata seed และ weak label |
| Custom Lab | เว็บจำลอง, endpoint, intended vulnerability | ทดสอบ live ranking และ demo |
| Scanner | finding count, evidence flag, detected tech | เพิ่ม feature จากหลักฐานจริง |
| Passive HTTP | title, server header, form, input, link | fingerprint เป้าหมายโดยไม่ยิงหนัก |

## 4. Feature ที่ควรใช้

### Network / Port Feature

```text
exposed_port_count
has_http_port_hint
port_80_open
port_443_open
port_3000_open
port_8080_open
```

ใช้บอกว่าเป้าหมายเปิดบริการแบบไหน

### Product / Service Feature

```text
product_grafana
product_wordpress
product_jenkins
service_apache_httpd
service_nginx
service_werkzeug
```

ใช้บอกว่าเป้าหมายเป็นระบบหรือ service อะไร

### Version / CVE Feature

```text
has_cve
cve_year
service_version_count
has_known_vulnerable_version
```

ใช้เชื่อม product/version กับช่องโหว่ที่เคยมี

### Web Surface Feature

```text
has_login_form
has_register_link
has_upload_form
input_username
input_password
input_file
form_count
link_count
```

ใช้ดู surface ของเว็บ เช่น login มักเกี่ยวกับ auth-bypass, SQLi, broken access control

### Scanner Evidence Feature

```text
has_zap_evidence
has_nuclei_evidence
has_wapiti_evidence
has_nikto_evidence
zap_finding_count
nuclei_finding_count
wapiti_finding_count
nikto_finding_count
```

ใช้เพิ่มน้ำหนักจากผล scanner จริง

## 5. Label ปัจจุบัน

| Label | ความหมาย | สถานะ |
|---|---|---|
| `is_recommended` | candidate นี้ควรถูกแนะนำหรือไม่ | มีแล้ว |
| `is_top1` | candidate นี้เป็นอันดับ 1 หรือไม่ | มีแล้ว |
| `is_known_family` | candidate ตรงกับ family จาก metadata หรือไม่ | มีแล้วในชุด Vulhub expanded |

## 6. Label ที่ควรเพิ่มต่อ

| Label | ความหมาย | ทำไมสำคัญ |
|---|---|---|
| `exploit_success_observed` | exploit/family นี้สำเร็จจริงหรือไม่ | เป็น label หลักสำหรับ Exploit-DL |
| `time_to_success_seconds` | ใช้เวลากี่วินาทีถึงเจอผล | ใช้วัดว่า model ช่วยให้เร็วขึ้นไหม |
| `attempt_count_before_success` | ลองกี่ครั้งก่อนสำเร็จ | ใช้วัดความแม่นของ ranking |
| `manual_vs_model_group` | อยู่กลุ่ม A หรือ B | ใช้ทำ A/B test |

## 7. ประโยคอธิบายบนสไลด์

> ในขั้น Fingerprint → Feature ระบบจะนำข้อมูลดิบ เช่น product, service, port, CVE, scanner finding และ web form มาแปลงเป็น feature vector แบบตัวเลข จากนั้นใช้ label เช่น is_recommended หรือ exploit_success_observed เพื่อฝึกโมเดลให้จัดอันดับ vulnerability family ที่ควรตรวจสอบก่อน

