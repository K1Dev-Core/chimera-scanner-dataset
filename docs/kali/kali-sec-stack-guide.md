# คู่มือ Kali Security Stack

ตรวจจาก upstream docs และ project pages เมื่อ 2026-08-03

## ชุดเครื่องมือที่ใช้

Platform / vulnerability management:

- `Faraday`
- `DefectDojo`
- `Reconmap`

Scanner:

- `Greenbone Community Edition / GVM`
- `OWASP ZAP`
- `Nuclei`
- `Wapiti`

Recon / attack surface:

- `Subfinder`
- `httpx-toolkit`
- `Naabu`
- `AutoRecon`
- `Amass`

Exploitation / web testing:

- `Metasploit Framework`
- `sqlmap`
- `Nikto`

Lab:

- `Docker Engine`
- `Vulhub`

## Flow ที่แนะนำบน Kali

1. ติดตั้ง Docker ก่อน
2. ติดตั้ง CLI tools จาก Kali repo
3. ติดตั้ง `GVM` แล้วรัน `gvm-setup`
4. clone `Faraday`, `DefectDojo`, `Reconmap`, `Vulhub`
5. เปิดเฉพาะ stack ที่ต้องใช้ เพราะเปิดทั้งหมดพร้อมกันอาจกิน RAM และชน port

## One-shot installer

script อยู่ที่:

`docs/kali/kali-sec-stack-install.sh`

ตัวอย่างการรันบน Kali:

```bash
chmod +x ~/kali-sec-stack-install.sh
sudo ~/kali-sec-stack-install.sh
```

## หมายเหตุเรื่อง Docker บน Kali

Docker official docs แนะนำให้ Kali ใช้วิธีติดตั้งแบบ Debian และเลือก Debian codename ที่ตรงกัน script นี้ใช้ `trixie` เป็นค่า default ที่ปลอดภัยสำหรับ Kali รุ่นใหม่ ถ้า image ของ Kali ถูก pin ต่างออกไป ให้แก้ `Suites:` ใน `/etc/apt/sources.list.d/docker.sources`

## คำสั่งเปิดใช้งานเร็ว

```bash
# Faraday
cd ~/sec-platforms/faraday
docker compose up -d

# DefectDojo
cd ~/sec-platforms/django-DefectDojo
docker compose up -d
docker compose logs initializer | grep "Admin password:"

# Reconmap
cd ~/sec-platforms/reconmap
docker compose up -d

# Greenbone / GVM
sudo gvm-start

# Vulhub
cd ~/labs/vulhub
find . -maxdepth 2 -name docker-compose.yml -o -name compose.yml | head
cd <scenario-dir>
docker compose up -d
```

## สิ่งที่ตรวจบนเครื่อง Windows นี้

ณ 2026-08-03:

- มี `git`
- มี binary ของ `docker` และ `docker compose`
- Docker daemon ยังไม่รัน
- ยังไม่มี WSL

ดังนั้นบนเครื่องนี้เตรียมไฟล์/คำสั่งได้ แต่การยก Kali lab จริงควรทำใน Kali VM หรือเปิด WSL ก่อน

## แหล่งอ้างอิงหลัก

- Faraday
- DefectDojo
- Reconmap
- Docker Engine on Debian
- Greenbone Community docs
- Kali tool packages
- OWASP ZAP
- sqlmap
- Nikto
- Vulhub
