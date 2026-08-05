```bash
nmap -vv --reason -Pn -T4 -sV -sC --version-all -A --osscan-guess -p 18083 -oN "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/_full_tcp_nmap.txt" -oX "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/xml/_full_tcp_nmap.xml" 127.0.0.1
```

[/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/_full_tcp_nmap.txt](file:///home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/_full_tcp_nmap.txt):

```
# Nmap 7.99 scan initiated Tue Aug  4 16:45:14 2026 as: /usr/lib/nmap/nmap -vv --reason -Pn -T4 -sV -sC --version-all -A --osscan-guess -p 18083 -oN /home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/_full_tcp_nmap.txt -oX /home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/xml/_full_tcp_nmap.xml 127.0.0.1
adjust_timeouts2: packet supposedly had rtt of -111128 microseconds.  Ignoring time.
adjust_timeouts2: packet supposedly had rtt of -111128 microseconds.  Ignoring time.
adjust_timeouts2: packet supposedly had rtt of -857098 microseconds.  Ignoring time.
adjust_timeouts2: packet supposedly had rtt of -857098 microseconds.  Ignoring time.
Nmap scan report for localhost (127.0.0.1)
Host is up, received user-set (0.000057s latency).
Scanned at 2026-08-04 16:45:15 EDT for 17s

PORT      STATE SERVICE REASON         VERSION
18083/tcp open  http    syn-ack ttl 64 Apache httpd 2.4.52 ((Debian))
| http-methods: 
|_  Supported Methods: GET POST OPTIONS HEAD
|_http-server-header: Apache/2.4.52 (Debian)
|_http-title: elFinder 2.1.x source version with PHP connector
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
OS fingerprint not ideal because: Missing a closed TCP port so results incomplete
Aggressive OS guesses: Linux 5.0 - 6.2 (97%), Linux 3.7 - 4.19 (93%), Linux 2.6.32 (93%), Linux 3.8 - 3.9 (93%), Linux 6.8 (93%), Linux 5.15 (92%), Linux 5.10 - 5.11 (92%), Linux 4.10 (92%), Asus RT-N10 router or AXIS 211A Network Camera (Linux 2.6) (91%), Linux 2.6.18 (91%)
No exact OS matches for host (test conditions non-ideal).
TCP/IP fingerprint:
SCAN(V=7.99%E=4%D=8/4%OT=18083%CT=%CU=31807%PV=Y%DS=0%DC=L%G=N%TM=6A724F6C%P=x86_64-pc-linux-gnu)
SEQ(SP=104%GCD=1%ISR=108%TI=Z%CI=Z%TS=22)
SEQ(SP=FE%GCD=1%ISR=108%TI=Z%CI=Z%II=I%TS=22)
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
IE(R=N)
IE(R=Y%DFI=N%T=40%CD=S)

Uptime guess: 0.000 days (since Tue Aug  4 16:45:28 2026)
Network Distance: 0 hops
TCP Sequence Prediction: Difficulty=260 (Good luck!)
IP ID Sequence Generation: All zeros

Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Tue Aug  4 16:45:32 2026 -- 1 IP address (1 host up) scanned in 17.37 seconds

```
