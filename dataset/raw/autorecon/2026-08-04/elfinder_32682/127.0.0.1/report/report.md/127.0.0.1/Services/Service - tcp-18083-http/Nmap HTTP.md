```bash
nmap -vv --reason -Pn -T4 -sV -p 18083 --script="banner,(http* or ssl*) and not (brute or broadcast or dos or external or http-slowloris* or fuzzer)" -oN "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/tcp_18083_http_nmap.txt" -oX "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/xml/tcp_18083_http_nmap.xml" 127.0.0.1
```

[/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/tcp_18083_http_nmap.txt](file:///home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/tcp_18083_http_nmap.txt):

```
# Nmap 7.99 scan initiated Tue Aug  4 16:45:32 2026 as: /usr/lib/nmap/nmap -vv --reason -Pn -T4 -sV -p 18083 "--script=banner,(http* or ssl*) and not (brute or broadcast or dos or external or http-slowloris* or fuzzer)" -oN /home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/tcp_18083_http_nmap.txt -oX /home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/xml/tcp_18083_http_nmap.xml 127.0.0.1
Nmap scan report for localhost (127.0.0.1)
Host is up, received user-set (0.000048s latency).
Scanned at 2026-08-04 16:45:33 EDT for 25s

Bug in http-security-headers: no string output.
PORT      STATE SERVICE REASON         VERSION
18083/tcp open  http    syn-ack ttl 64 Apache httpd 2.4.52 ((Debian))
| http-headers: 
|   Date: Tue, 04 Aug 2026 20:45:47 GMT
|   Server: Apache/2.4.52 (Debian)
|   Last-Modified: Sat, 26 Feb 2022 18:16:28 GMT
|   ETag: "df6-5d8efd05b9700"
|   Accept-Ranges: bytes
|   Content-Length: 3574
|   Vary: Accept-Encoding
|   Connection: close
|   Content-Type: text/html
|   
|_  (Request type: HEAD)
|_http-chrono: Request times for /; avg: 230.06ms; min: 179.96ms; max: 319.99ms
|_http-malware-host: Host appears to be clean
|_http-jsonp-detection: Couldn't find any JSONP endpoints.
| http-vhosts: 
|_128 names had status 200
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-wordpress-users: [Error] Wordpress installation was not found. We couldn't find wp-login.php
| http-useragent-tester: 
|   Status for browser useragent: 200
|   Allowed User Agents: 
|     Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)
|     libwww
|     lwp-trivial
|     libcurl-agent/1.0
|     PHP/
|     Python-urllib/2.5
|     GT::WWW
|     Snoopy
|     MFC_Tear_Sample
|     HTTP::Lite
|     PHPCrawl
|     URI::Fetch
|     Zend_Http_Client
|     http client
|     PECL::HTTP
|     Wget/1.13.4 (linux-gnu)
|_    WWW-Mechanize/1.34
|_http-fetch: Please enter the complete path of the directory to save data in.
| http-sitemap-generator: 
|   Directory structure:
|     /
|       Other: 1
|   Longest directory structure:
|     Depth: 0
|     Dir: /
|   Total files found (by extension):
|_    Other: 1
|_http-server-header: Apache/2.4.52 (Debian)
|_http-title: elFinder 2.1.x source version with PHP connector
|_http-litespeed-sourcecode-download: Request with null byte did not work. This web server might not be vulnerable
|_http-date: Tue, 04 Aug 2026 20:45:45 GMT; 0s from local time.
| http-methods: 
|_  Supported Methods: GET POST OPTIONS HEAD
|_http-errors: Couldn't find any error pages.
| http-php-version: Logo query returned unknown hash 17b55942ed1aea3901b42b00420bdd2d
|_Credits query returned unknown hash 17b55942ed1aea3901b42b00420bdd2d
|_http-devframework: Couldn't determine the underlying framework or CMS. Try increasing 'httpspider.maxpagecount' value to spider more pages.
| http-enum: 
|_  /.gitignore: Revision control ignore file
|_http-mobileversion-checker: No mobile version detected.
| http-referer-checker: 
| Spidering limited to: maxpagecount=30
|_  http://cdnjs.cloudflare.com:80/ajax/libs/require.js/2.3.6/require.min.js
|_http-drupal-enum: Nothing found amongst the top 100 resources,use --script-args number=<number|all> for deeper analysis)
|_http-feed: Couldn't find any feeds.
| http-comments-displayer: 
| Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=localhost
|     
|     Path: http://localhost:18083/
|     Line number: 61
|     Comment: 
|         /* elFinder options of this DOM Element */
|     
|     Path: http://localhost:18083/
|     Line number: 42
|     Comment: 
|         /* any bind functions etc. */
|     
|     Path: http://localhost:18083/
|     Line number: 18
|     Comment: 
|          // or connector.maximal.php : connector URL (REQUIRED)
|     
|     Path: http://localhost:18083/
|     Line number: 69
|     Comment: 
|         <!-- Element where elFinder will be created (REQUIRED) -->
|     
|     Path: http://localhost:18083/
|     Line number: 10
|     Comment: 
|         <!-- Rename "main.default.js" to "main.js" and edit it if you need configure elFInder options or any things -->
|     
|     Path: http://localhost:18083/
|     Line number: 9
|     Comment: 
|_        <!-- Require JS (REQUIRED) -->
|_http-wordpress-enum: Nothing found amongst the top 100 resources,use --script-args search-limit=<number|all> for deeper analysis)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.

Read data files from: /usr/share/nmap
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Tue Aug  4 16:45:58 2026 -- 1 IP address (1 host up) scanned in 26.43 seconds

```
