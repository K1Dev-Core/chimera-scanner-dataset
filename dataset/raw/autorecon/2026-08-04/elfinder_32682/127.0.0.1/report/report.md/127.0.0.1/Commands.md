```bash
nmap -vv --reason -Pn -T4 -sV -sC --version-all -A --osscan-guess -p 18083 -oN "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/_full_tcp_nmap.txt" -oX "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/xml/_full_tcp_nmap.xml" 127.0.0.1

nmap -vv --reason -Pn -T4 -sU -A --osscan-guess -p 18083 -oN "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/_custom_ports_udp_nmap.txt" -oX "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/xml/_custom_ports_udp_nmap.xml" 127.0.0.1

feroxbuster -u http://127.0.0.1:18083/ -t 10 -w /root/.local/share/AutoRecon/wordlists/dirbuster.txt -x "txt,html,php,asp,aspx,jsp" -v -k -n -q -e -r -o "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/tcp_18083_http_feroxbuster_dirbuster.txt"

curl -sSikf http://127.0.0.1:18083/.well-known/security.txt

curl -sSikf http://127.0.0.1:18083/robots.txt

curl -sSik http://127.0.0.1:18083/

nikto -ask=no -Tuning=x4567890ac -nointeractive -host http://127.0.0.1:18083 2>&1 | tee "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/tcp_18083_http_nikto.txt"

nmap -vv --reason -Pn -T4 -sV -p 18083 --script="banner,(http* or ssl*) and not (brute or broadcast or dos or external or http-slowloris* or fuzzer)" -oN "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/tcp_18083_http_nmap.txt" -oX "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/xml/tcp_18083_http_nmap.xml" 127.0.0.1

whatweb --color=never --no-errors -a 3 -v http://127.0.0.1:18083 2>&1


```