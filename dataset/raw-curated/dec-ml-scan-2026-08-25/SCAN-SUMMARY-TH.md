# สรุปผลสแกน Dec ML scan 2026-08-25

สร้างเมื่อ: 2026-08-24T17:02:32
จำนวน target records: 29
จำนวน scan_success: 29

## ภาพรวมหลักฐาน

- nmap service detection: 29 records
- probe/evidence file: 24 records
- nikto output: 3 records
- wapiti output: 1 records
- compose failure records: 0

## รายการ target

- `adminer_CVE-2021-21311`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Login - Adminer`, server=`Apache/2.4.54 (Debian)`, service=``, mode=`fast_fingerprint_wave3`
- `apache_druid_CVE-2021-25646`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Apache Druid`, server=``, service=``, mode=`fast_fingerprint_wave3`
- `appweb_CVE-2018-8715`: success=True, compose_exit=`0`, nmap_exit=`124`, title=`Unauthorized`, server=``, service=``, mode=`fast_fingerprint`
- `aria2_rce`: success=True, compose_exit=`0`, nmap_exit=`0`, title=``, server=``, service=`6800/tcp open  http    aria2 downloader JSON-RPC`, mode=`fast_fingerprint_wave5`
- `couchdb_CVE-2017-12635`: success=True, compose_exit=`0`, nmap_exit=`0`, title=``, server=`CouchDB/2.1.0 (Erlang OTP/17)`, service=``, mode=`fast_fingerprint_wave2`
- `couchdb_CVE-2017-12636`: success=True, compose_exit=`0`, nmap_exit=`0`, title=``, server=`CouchDB/1.6.0 (Erlang OTP/17)`, service=``, mode=`fast_fingerprint_wave4`
- `drupal_CVE-2018-7600`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Choose language | Drupal`, server=`Apache/2.4.25 (Debian)`, service=``, mode=`fast_fingerprint`
- `elasticsearch_CVE-2015-1427`: success=True, compose_exit=`0`, nmap_exit=`0`, title=``, server=``, service=``, mode=`fast_fingerprint_wave2`
- `flask_ssti`: success=True, compose_exit=`0`, nmap_exit=`0`, title=``, server=`gunicorn/20.0.0`, service=``, mode=`fast_fingerprint`
- `goahead_CVE-2017-17562`: success=True, compose_exit=`0`, nmap_exit=`124`, title=`Home Page`, server=``, service=``, mode=`fast_fingerprint_wave3`
- `gogs_CVE-2018-18925`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Installation - Gogs`, server=``, service=``, mode=`fast_fingerprint_wave4`
- `grafana_CVE-2021-43798`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Grafana`, server=``, service=``, mode=`fast_fingerprint_wave3`
- `jenkins_CVE-2018-1000861`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Starting Jenkins`, server=`Jetty(9.4.z-SNAPSHOT)`, service=``, mode=`fast_fingerprint_wave4`
- `jetty_CVE-2021-28164`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Example Domain`, server=`Jetty(9.4.37.v20210219)`, service=`8080/tcp open  http    Jetty 9.4.37.v20210219`, mode=`fast_fingerprint_wave5`
- `joomla_CVE-2023-23752`: success=True, compose_exit=``, nmap_exit=`0`, title=``, server=`Apache/2.4.54 (Debian)`, service=``, mode=`full_or_mixed`
- `nextjs_CVE-2025-29927`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Admin Dashboard`, server=``, service=``, mode=``
- `nexus_CVE-2019-7238`: success=True, compose_exit=`0`, nmap_exit=`0`, title=``, server=``, service=``, mode=`fast_fingerprint_retry`
- `nginx_CVE-2017-7529`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Welcome to nginx!`, server=`nginx/1.13.2`, service=``, mode=``
- `phpmyadmin_CVE-2018-12613`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Access denied!`, server=`Apache/2.4.25 (Debian)`, service=``, mode=`fast_fingerprint`
- `rails_CVE-2018-3760`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Ruby on Rails`, server=``, service=``, mode=`fast_fingerprint_wave4`
- `rails_CVE-2019-5418`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Ruby on Rails`, server=``, service=``, mode=`fast_fingerprint_wave2`
- `redis_CVE-2022-0543`: success=True, compose_exit=`0`, nmap_exit=`0`, title=``, server=``, service=`6379/tcp open  redis   Redis key-value store 5.0.7`, mode=`fast_fingerprint_wave5`
- `shiro_CVE-2016-4437`: success=True, compose_exit=`0`, nmap_exit=`124`, title=`Login Page`, server=``, service=``, mode=`fast_fingerprint`
- `solr_CVE-2017-12629-RCE`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Solr Admin`, server=``, service=``, mode=`fast_fingerprint`
- `spring_CVE-2022-22965`: success=True, compose_exit=`0`, nmap_exit=`0`, title=``, server=``, service=``, mode=`fast_fingerprint`
- `struts2_s2-045`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Struts2 Showcase - Fileupload sample`, server=`Jetty(9.2.11.v20150529)`, service=``, mode=`fast_fingerprint`
- `thinkphp_5-rce`: success=True, compose_exit=`0`, nmap_exit=`0`, title=``, server=`Apache/2.4.38 (Debian)`, service=``, mode=`fast_fingerprint`
- `tomcat_CVE-2017-12615`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Apache Tomcat/8.5.19`, server=``, service=``, mode=`fast_fingerprint`
- `webmin_CVE-2019-15107`: success=True, compose_exit=`0`, nmap_exit=`0`, title=`Login to Webmin`, server=`MiniServ/1.910`, service=``, mode=`fast_fingerprint_wave2`

## ใช้กับ ML ยังไง

- `features.csv` มี `scan_success`, `protocol_kind`, `candidate_family`, `nmap_service_line` เพื่อใช้ทดสอบ ranking model ได้ทันที
- `labels-draft.jsonl` เป็น weak label จาก Vulhub path ยังไม่ใช่ exploit-success
- non-HTTP target เช่น Redis/Aria2 ช่วยให้โมเดลไม่ bias เฉพาะเว็บ

## ข้อจำกัด

- Nexus มี nmap สำเร็จ แต่ HTTP ยังไม่ตอบในเวลารอ อาจต้องเพิ่ม startup wait
- เหลือ disk น้อย ควร export แล้วล้าง container ก่อน pull ชุดใหญ่
- ต้องติดตั้ง ProjectDiscovery httpx ตัวจริงและจูน nuclei รอบหน้า
