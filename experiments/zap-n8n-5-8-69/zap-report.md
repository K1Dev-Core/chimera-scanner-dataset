# รายงานสรุป ZAP Scan

รายงานนี้เป็นสรุปภาษาไทยจาก ZAP scan ของ target:

`http://host.docker.internal:15678`

raw detail ยังอยู่ในไฟล์:

- `zap-report.json`
- `zap-report.html`
- `console.txt`
- `zap.yaml`

## สรุปจำนวน alerts

| Risk level | จำนวน alerts |
| --- | ---: |
| High | 0 |
| Medium | 3 |
| Low | 6 |
| Informational | 4 |

## Medium alerts

| Alert | จำนวน instance | ความหมาย |
| --- | ---: | --- |
| `CSP: Failure to Define Directive with No Fallback` | 2 | CSP ขาด directive สำคัญ เช่น `frame-ancestors`, `form-action` |
| `Content Security Policy (CSP) Header Not Set` | 1 | response บางส่วนไม่มี CSP header |
| `Missing Anti-clickjacking Header` | 1 | ไม่มี header ป้องกัน clickjacking เช่น `X-Frame-Options` หรือ CSP `frame-ancestors` |

## Low alerts

| Alert | จำนวน instance | ความหมาย |
| --- | ---: | --- |
| `Cross-Origin-Embedder-Policy Header Missing or Invalid` | 1 | COEP header หายหรือไม่ถูกต้อง |
| `Cross-Origin-Opener-Policy Header Missing or Invalid` | 1 | COOP header หายหรือไม่ถูกต้อง |
| `Cross-Origin-Resource-Policy Header Missing or Invalid` | 5 | CORP header หายหรือไม่ถูกต้อง |
| `Permissions Policy Header Not Set` | 5 | ไม่ได้จำกัด browser features ด้วย Permissions Policy |
| `Timestamp Disclosure - Unix` | systemic | response มี Unix timestamp ที่อาจเผยข้อมูลระบบ |
| `X-Content-Type-Options Header Missing` | 5 | ไม่มี `X-Content-Type-Options: nosniff` |

## Informational alerts

| Alert | จำนวน instance | ความหมาย |
| --- | ---: | --- |
| `Information Disclosure - Suspicious Comments` | 8 | พบ comment ที่อาจมีข้อมูลภายใน |
| `Modern Web Application` | 1 | ZAP มองว่าเป็น modern web app |
| `Storable and Cacheable Content` | 3 | content ถูก cache ได้ |
| `Storable but Non-Cacheable Content` | 3 | content store ได้แต่ไม่ cache ตาม policy |

## Insight จาก scan

- endpoints ทั้งหมดที่พบ: 6
- method ที่เห็น: `GET` 100%
- response 2xx ประมาณ 75%
- response 4xx ประมาณ 25%
- content types ที่พบ: JavaScript, favicon, CSS, HTML

## ใช้กับ dataset ยังไง

รายงานนี้เหมาะเป็น `finding`/`observation` สำหรับ web hardening และ scanner coverage

ไม่ควรตีความว่าเป็น exploit success เพราะ alerts ส่วนใหญ่เป็น security header/configuration findings ไม่ใช่ RCE หรือ CVE validation
