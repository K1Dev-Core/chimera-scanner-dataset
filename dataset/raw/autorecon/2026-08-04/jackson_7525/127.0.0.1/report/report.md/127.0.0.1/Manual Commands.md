```bash
[*] http-proxy on tcp/8080

	[-] (feroxbuster) Multi-threaded recursive directory/file enumeration for web servers using various wordlists:

		feroxbuster -u http://127.0.0.1:8080 -t 10 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x "txt,html,php,asp,aspx,jsp" -v -k -n -e -r -o /home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_feroxbuster_dirbuster.txt

	[-] Credential bruteforcing commands (don't run these without modifying them):

		hydra -L "/usr/share/seclists/Usernames/top-usernames-shortlist.txt" -P "/usr/share/seclists/Passwords/darkweb2017-top100.txt" -e nsr -s 8080 -o "/home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_auth_hydra.txt" http-get://127.0.0.1/path/to/auth/area

		medusa -U "/usr/share/seclists/Usernames/top-usernames-shortlist.txt" -P "/usr/share/seclists/Passwords/darkweb2017-top100.txt" -e ns -n 8080 -O "/home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_auth_medusa.txt" -M http -h 127.0.0.1 -m DIR:/path/to/auth/area

		hydra -L "/usr/share/seclists/Usernames/top-usernames-shortlist.txt" -P "/usr/share/seclists/Passwords/darkweb2017-top100.txt" -e nsr -s 8080 -o "/home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_form_hydra.txt" http-post-form://127.0.0.1/path/to/login.php:"username=^USER^&password=^PASS^":"invalid-login-message"

		medusa -U "/usr/share/seclists/Usernames/top-usernames-shortlist.txt" -P "/usr/share/seclists/Passwords/darkweb2017-top100.txt" -e ns -n 8080 -O "/home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_form_medusa.txt" -M web-form -h 127.0.0.1 -m FORM:/path/to/login.php -m FORM-DATA:"post?username=&password=" -m DENY-SIGNAL:"invalid login message"

	[-] (wpscan) WordPress Security Scanner (useful if WordPress is found):

		wpscan --url http://127.0.0.1:8080/ --no-update -e vp,vt,tt,cb,dbe,u,m --plugins-detection aggressive --plugins-version-detection aggressive -f cli-no-color 2>&1 | tee "/home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_wpscan.txt"


```