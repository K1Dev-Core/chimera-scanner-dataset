```bash
nmap -vv --reason -Pn -T4 -sV -sC --version-all -A --osscan-guess -p 3000 -oN "/home/kali/dataset/raw/autorecon/2026-08-04/gogs_18925/127.0.0.1/scans/_full_tcp_nmap.txt" -oX "/home/kali/dataset/raw/autorecon/2026-08-04/gogs_18925/127.0.0.1/scans/xml/_full_tcp_nmap.xml" 127.0.0.1

nmap -vv --reason -Pn -T4 -sU -A --osscan-guess -p 3000 -oN "/home/kali/dataset/raw/autorecon/2026-08-04/gogs_18925/127.0.0.1/scans/_custom_ports_udp_nmap.txt" -oX "/home/kali/dataset/raw/autorecon/2026-08-04/gogs_18925/127.0.0.1/scans/xml/_custom_ports_udp_nmap.xml" 127.0.0.1


```