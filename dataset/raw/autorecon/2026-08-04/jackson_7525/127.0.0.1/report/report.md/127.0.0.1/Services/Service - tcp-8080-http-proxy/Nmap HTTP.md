```bash
nmap -vv --reason -Pn -T4 -sV -p 8080 --script="banner,(http* or ssl*) and not (brute or broadcast or dos or external or http-slowloris* or fuzzer)" -oN "/home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_nmap.txt" -oX "/home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/xml/tcp_8080_http_nmap.xml" 127.0.0.1
```

[/home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_nmap.txt](file:///home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_nmap.txt):

```
# Nmap 7.99 scan initiated Tue Aug  4 18:02:43 2026 as: /usr/lib/nmap/nmap -vv --reason -Pn -T4 -sV -p 8080 "--script=banner,(http* or ssl*) and not (brute or broadcast or dos or external or http-slowloris* or fuzzer)" -oN /home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_nmap.txt -oX /home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/xml/tcp_8080_http_nmap.xml 127.0.0.1
Nmap scan report for localhost (127.0.0.1)
Host is up, received user-set (0.000044s latency).
Scanned at 2026-08-04 18:02:44 EDT for 47s

PORT     STATE SERVICE    REASON         VERSION
8080/tcp open  http-proxy syn-ack ttl 64
|_http-wordpress-users: [Error] Wordpress installation was not found. We couldn't find wp-login.php
|_http-favicon: Spring Java Framework
| http-waf-detect: IDS/IPS/WAF detected:
|_localhost:8080/?p4yl04d3=<script>alert(document.cookie)</script>
|_http-malware-host: Host appears to be clean
|_http-jsonp-detection: Couldn't find any JSONP endpoints.
|_http-chrono: Request times for /; avg: 203.88ms; min: 189.01ms; max: 240.52ms
|_http-date: Tue, 04 Aug 2026 22:02:55 GMT; -1s from local time.
| http-vhosts: 
|_128 names had status 404
|_http-fetch: Please enter the complete path of the directory to save data in.
|_http-title: Site doesn't have a title (application/json;charset=UTF-8).
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, RPCCheck: 
|     HTTP/1.1 400 
|     Transfer-Encoding: chunked
|     Date: Tue, 04 Aug 2026 22:02:55 GMT
|     Connection: close
|   FourOhFourRequest: 
|     HTTP/1.1 404 
|     Content-Type: application/json;charset=UTF-8
|     Date: Tue, 04 Aug 2026 22:02:51 GMT
|     Connection: close
|     ["java.util.LinkedHashMap",{"timestamp":["java.util.Date",1785880971192],"status":404,"error":"Not Found","message":"No message available","path":"/nice%20ports%2C/Tri%6Eity.txt%2ebak"}]
|   GetRequest: 
|     HTTP/1.1 404 
|     Content-Type: application/json;charset=UTF-8
|     Date: Tue, 04 Aug 2026 22:02:50 GMT
|     Connection: close
|     ["java.util.LinkedHashMap",{"timestamp":["java.util.Date",1785880971122],"status":404,"error":"Not Found","message":"No message available","path":"/"}]
|   HTTPOptions: 
|     HTTP/1.1 404 
|     Content-Type: application/json;charset=UTF-8
|     Date: Tue, 04 Aug 2026 22:02:51 GMT
|     Connection: close
|     ["java.util.LinkedHashMap",{"timestamp":["java.util.Date",1785880971183],"status":404,"error":"Not Found","message":"No message available","path":"/"}]
|   RTSPRequest, Socks4, Socks5: 
|     HTTP/1.1 400 
|     Transfer-Encoding: chunked
|     Date: Tue, 04 Aug 2026 22:02:51 GMT
|_    Connection: close
|_http-drupal-enum: Nothing found amongst the top 100 resources,use --script-args number=<number|all> for deeper analysis)
|_http-litespeed-sourcecode-download: Request with null byte did not work. This web server might not be vulnerable
|_http-wordpress-enum: Nothing found amongst the top 100 resources,use --script-args search-limit=<number|all> for deeper analysis)
| http-headers: 
|   Content-Type: application/json;charset=UTF-8
|   Transfer-Encoding: chunked
|   Date: Tue, 04 Aug 2026 22:03:00 GMT
|   Connection: close
|   
|_  (Request type: GET)
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port8080-TCP:V=7.99%I=7%D=8/4%Time=6A72618B%P=x86_64-pc-linux-gnu%r(Get
SF:Request,10E,"HTTP/1\.1\x20404\x20\r\nContent-Type:\x20application/json;
SF:charset=UTF-8\r\nDate:\x20Tue,\x2004\x20Aug\x202026\x2022:02:50\x20GMT\
SF:r\nConnection:\x20close\r\n\r\n\[\"java\.util\.LinkedHashMap\",{\"times
SF:tamp\":\[\"java\.util\.Date\",1785880971122\],\"status\":404,\"error\":
SF:\"Not\x20Found\",\"message\":\"No\x20message\x20available\",\"path\":\"
SF:/\"}\]")%r(HTTPOptions,10E,"HTTP/1\.1\x20404\x20\r\nContent-Type:\x20ap
SF:plication/json;charset=UTF-8\r\nDate:\x20Tue,\x2004\x20Aug\x202026\x202
SF:2:02:51\x20GMT\r\nConnection:\x20close\r\n\r\n\[\"java\.util\.LinkedHas
SF:hMap\",{\"timestamp\":\[\"java\.util\.Date\",1785880971183\],\"status\"
SF::404,\"error\":\"Not\x20Found\",\"message\":\"No\x20message\x20availabl
SF:e\",\"path\":\"/\"}\]")%r(RTSPRequest,6A,"HTTP/1\.1\x20400\x20\r\nTrans
SF:fer-Encoding:\x20chunked\r\nDate:\x20Tue,\x2004\x20Aug\x202026\x2022:02
SF::51\x20GMT\r\nConnection:\x20close\r\n\r\n0\r\n\r\n")%r(FourOhFourReque
SF:st,131,"HTTP/1\.1\x20404\x20\r\nContent-Type:\x20application/json;chars
SF:et=UTF-8\r\nDate:\x20Tue,\x2004\x20Aug\x202026\x2022:02:51\x20GMT\r\nCo
SF:nnection:\x20close\r\n\r\n\[\"java\.util\.LinkedHashMap\",{\"timestamp\
SF:":\[\"java\.util\.Date\",1785880971192\],\"status\":404,\"error\":\"Not
SF:\x20Found\",\"message\":\"No\x20message\x20available\",\"path\":\"/nice
SF:%20ports%2C/Tri%6Eity\.txt%2ebak\"}\]")%r(Socks5,6A,"HTTP/1\.1\x20400\x
SF:20\r\nTransfer-Encoding:\x20chunked\r\nDate:\x20Tue,\x2004\x20Aug\x2020
SF:26\x2022:02:51\x20GMT\r\nConnection:\x20close\r\n\r\n0\r\n\r\n")%r(Sock
SF:s4,6A,"HTTP/1\.1\x20400\x20\r\nTransfer-Encoding:\x20chunked\r\nDate:\x
SF:20Tue,\x2004\x20Aug\x202026\x2022:02:51\x20GMT\r\nConnection:\x20close\
SF:r\n\r\n0\r\n\r\n")%r(RPCCheck,6A,"HTTP/1\.1\x20400\x20\r\nTransfer-Enco
SF:ding:\x20chunked\r\nDate:\x20Tue,\x2004\x20Aug\x202026\x2022:02:55\x20G
SF:MT\r\nConnection:\x20close\r\n\r\n0\r\n\r\n")%r(DNSVersionBindReqTCP,6A
SF:,"HTTP/1\.1\x20400\x20\r\nTransfer-Encoding:\x20chunked\r\nDate:\x20Tue
SF:,\x2004\x20Aug\x202026\x2022:02:55\x20GMT\r\nConnection:\x20close\r\n\r
SF:\n0\r\n\r\n")%r(DNSStatusRequestTCP,6A,"HTTP/1\.1\x20400\x20\r\nTransfe
SF:r-Encoding:\x20chunked\r\nDate:\x20Tue,\x2004\x20Aug\x202026\x2022:02:5
SF:5\x20GMT\r\nConnection:\x20close\r\n\r\n0\r\n\r\n");

Read data files from: /usr/share/nmap
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Tue Aug  4 18:03:31 2026 -- 1 IP address (1 host up) scanned in 47.82 seconds

```
