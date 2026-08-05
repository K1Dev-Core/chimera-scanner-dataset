```bash
nmap -vv --reason -Pn -T4 -sV -sC --version-all -A --osscan-guess -p 3000 -oN "/home/kali/dataset/raw/autorecon/2026-08-04/gogs_18925/127.0.0.1/scans/_full_tcp_nmap.txt" -oX "/home/kali/dataset/raw/autorecon/2026-08-04/gogs_18925/127.0.0.1/scans/xml/_full_tcp_nmap.xml" 127.0.0.1
```

[/home/kali/dataset/raw/autorecon/2026-08-04/gogs_18925/127.0.0.1/scans/_full_tcp_nmap.txt](file:///home/kali/dataset/raw/autorecon/2026-08-04/gogs_18925/127.0.0.1/scans/_full_tcp_nmap.txt):

```
# Nmap 7.99 scan initiated Tue Aug  4 16:40:22 2026 as: /usr/lib/nmap/nmap -vv --reason -Pn -T4 -sV -sC --version-all -A --osscan-guess -p 3000 -oN /home/kali/dataset/raw/autorecon/2026-08-04/gogs_18925/127.0.0.1/scans/_full_tcp_nmap.txt -oX /home/kali/dataset/raw/autorecon/2026-08-04/gogs_18925/127.0.0.1/scans/xml/_full_tcp_nmap.xml 127.0.0.1
adjust_timeouts2: packet supposedly had rtt of -164994 microseconds.  Ignoring time.
adjust_timeouts2: packet supposedly had rtt of -164994 microseconds.  Ignoring time.
adjust_timeouts2: packet supposedly had rtt of -468933 microseconds.  Ignoring time.
adjust_timeouts2: packet supposedly had rtt of -468933 microseconds.  Ignoring time.
adjust_timeouts2: packet supposedly had rtt of -417880 microseconds.  Ignoring time.
adjust_timeouts2: packet supposedly had rtt of -417880 microseconds.  Ignoring time.
Nmap scan report for localhost (127.0.0.1)
Host is up, received user-set (0.000086s latency).
Scanned at 2026-08-04 16:40:23 EDT for 280s

PORT     STATE SERVICE         REASON         VERSION
3000/tcp open  hadoop-datanode syn-ack ttl 64 Apache Hadoop
| hadoop-datanode-info: 
|_  Logs: log_root_path
|_http-favicon: Unknown favicon MD5: 337372B7EC33DE7D431936311BCAF5EF
|_http-trane-info: Problem with XML parsing of /evox/about
| http-title: Installation - Gogs
|_Requested resource was /install
| hadoop-tasktracker-info: 
|_  Logs: log_root_path
| http-methods: 
|_  Supported Methods: GET HEAD
| fingerprint-strings: 
|   GenericLines, Help: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest: 
|     HTTP/1.0 302 Found
|     Content-Type: text/html; charset=utf-8
|     Location: /install
|     Set-Cookie: lang=en-US; Path=/; Max-Age=2147483647
|     Set-Cookie: i_like_gogits=eb64b925bafc809d; Path=/; HttpOnly
|     Set-Cookie: _csrf=tyNy_Mr-F4O9PYvunkxCM1hpEnc6MTc4NTg3NjAyOTYxNTc5ODA0OA%3D%3D; Path=/; Expires=Wed, 05 Aug 2026 20:40:29 GMT; HttpOnly
|     Date: Tue, 04 Aug 2026 20:40:29 GMT
|     Content-Length: 31
|     href="/install">Found</a>.
|   HTTPOptions: 
|     HTTP/1.0 404 Not Found
|     Content-Type: text/html; charset=UTF-8
|     Set-Cookie: lang=en-US; Path=/; Max-Age=2147483647
|     Set-Cookie: i_like_gogits=03f8a292e2049af2; Path=/; HttpOnly
|     Set-Cookie: _csrf=76l7rW1rqieSVsSdVZE62QC1KYc6MTc4NTg3NjAzNDY3Mzc3OTM2NA%3D%3D; Path=/; Expires=Wed, 05 Aug 2026 20:40:34 GMT; HttpOnly
|     Date: Tue, 04 Aug 2026 20:40:34 GMT
|     <!DOCTYPE html>
|     <html>
|     <head data-suburl="">
|     <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
|     <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
|     <meta name="author" content="Gogs" />
|     <meta name="description" content="Gogs is a painless self-hosted Git service" />
|     <meta name="keywords" content="go, git, self-hosted, gogs">
|     <meta name="referrer" content="no-referrer" />
|     <meta name="_csrf" content="76l7rW1rqieSVsSdVZE62QC1KYc6MTc4NTg3NjAzNDY3Mzc3OTM2NA==" />
|_    <meta name="_suburl" content="" />
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
OS fingerprint not ideal because: Missing a closed TCP port so results incomplete
Aggressive OS guesses: Linux 5.0 - 6.2 (97%), Linux 3.7 - 4.19 (93%), Linux 6.8 (93%), Linux 2.6.32 (92%), Linux 3.8 - 3.9 (92%), Linux 5.7 (92%), Linux 4.1 (92%), Linux 5.15 (92%), Linux 4.10 (92%), Linux 5.10 - 5.11 (91%)
No exact OS matches for host (test conditions non-ideal).
TCP/IP fingerprint:
SCAN(V=7.99%E=4%D=8/4%OT=3000%CT=%CU=42764%PV=Y%DS=0%DC=L%G=N%TM=6A724F4F%P=x86_64-pc-linux-gnu)
SEQ(SP=102%GCD=1%ISR=10B%TI=Z%CI=Z%TS=21)
SEQ(SP=10A%GCD=1%ISR=109%TI=Z%CI=Z%II=I%TS=22)
OPS(O1=MFFD7ST11NWA%O2=MFFD7ST11NWA%O3=MFFD7NNT11NWA%O4=MFFD7ST11NWA%O5=MFFD7ST11NWA%O6=MFFD7ST11)
WIN(W1=FFCB%W2=FFCB%W3=FFCB%W4=FFCB%W5=FFCB%W6=FFCB)
ECN(R=Y%DF=Y%T=40%W=FFD7%O=MFFD7NNSNWA%CC=Y%Q=)
T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS%RD=0%Q=)
T2(R=N)
T3(R=N)
T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)
T5(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)
T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)
T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)
U1(R=Y%DF=N%T=40%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)
IE(R=Y%DFI=N%T=40%CD=S)

Uptime guess: 0.000 days (since Tue Aug  4 16:44:46 2026)
Network Distance: 0 hops
TCP Sequence Prediction: Difficulty=258 (Good luck!)
IP ID Sequence Generation: All zeros

Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Tue Aug  4 16:45:03 2026 -- 1 IP address (1 host up) scanned in 280.64 seconds

```
