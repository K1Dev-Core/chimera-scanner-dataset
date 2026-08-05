```bash
nmap -vv --reason -Pn -T4 -sV -p 8888 --script="banner,(http* or ssl*) and not (brute or broadcast or dos or external or http-slowloris* or fuzzer)" -oN "/home/kali/dataset/raw/autorecon/2026-08-04/druid_25646/127.0.0.1/scans/tcp8888/tcp_8888_http_nmap.txt" -oX "/home/kali/dataset/raw/autorecon/2026-08-04/druid_25646/127.0.0.1/scans/tcp8888/xml/tcp_8888_http_nmap.xml" 127.0.0.1
```

[/home/kali/dataset/raw/autorecon/2026-08-04/druid_25646/127.0.0.1/scans/tcp8888/tcp_8888_http_nmap.txt](file:///home/kali/dataset/raw/autorecon/2026-08-04/druid_25646/127.0.0.1/scans/tcp8888/tcp_8888_http_nmap.txt):

```
# Nmap 7.99 scan initiated Tue Aug  4 16:31:06 2026 as: /usr/lib/nmap/nmap -vv --reason -Pn -T4 -sV -p 8888 "--script=banner,(http* or ssl*) and not (brute or broadcast or dos or external or http-slowloris* or fuzzer)" -oN /home/kali/dataset/raw/autorecon/2026-08-04/druid_25646/127.0.0.1/scans/tcp8888/tcp_8888_http_nmap.txt -oX /home/kali/dataset/raw/autorecon/2026-08-04/druid_25646/127.0.0.1/scans/tcp8888/xml/tcp_8888_http_nmap.xml 127.0.0.1
Nmap scan report for localhost (127.0.0.1)
Host is up, received user-set (0.00027s latency).
Scanned at 2026-08-04 16:31:06 EDT for 56s

PORT     STATE SERVICE REASON         VERSION
8888/tcp open  http    syn-ack ttl 64 Jetty
| http-security-headers: 
|   Cache_Control: 
|_    Header: Cache-Control: must-revalidate,no-cache,no-store
|_http-litespeed-sourcecode-download: Request with null byte did not work. This web server might not be vulnerable
|_http-errors: ERROR: Script execution failed (use -d to debug)
| http-useragent-tester: 
|   Status for browser useragent: 200
|   Redirected To: http://localhost:8888/unified-console.html
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
| http-php-version: Logo query returned unknown hash cb96148a634ca842a2a8b3aa357995af
|_Credits query returned unknown hash cb96148a634ca842a2a8b3aa357995af
| http-vhosts: 
|_128 names had status 405
|_http-fetch: Please enter the complete path of the directory to save data in.
|_http-devframework: Couldn't determine the underlying framework or CMS. Try increasing 'httpspider.maxpagecount' value to spider more pages.
|_http-feed: Couldn't find any feeds.
|_http-date: Tue, 04 Aug 2026 20:31:14 GMT; -2s from local time.
| http-sitemap-generator: 
|   Directory structure:
|     /
|       html: 1; js: 1
|   Longest directory structure:
|     Depth: 0
|     Dir: /
|   Total files found (by extension):
|_    html: 1; js: 1
| http-waf-detect: IDS/IPS/WAF detected:
|_localhost:8888/?p4yl04d3=<script>alert(document.cookie)</script>
|_http-jsonp-detection: Couldn't find any JSONP endpoints.
| http-headers: 
|   Connection: close
|   Date: Tue, 04 Aug 2026 20:31:14 GMT
|   Last-Modified: Thu, 08 Oct 2020 21:58:58 GMT
|   Content-Type: text/html
|   Accept-Ranges: bytes
|   Vary: Accept-Encoding, User-Agent
|   Content-Length: 1377
|   
|_  (Request type: GET)
| http-internal-ip-disclosure: 
|_  Internal IP Leaked: 172.28.0.2
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-malware-host: Host appears to be clean
| http-title: Apache Druid
|_Requested resource was http://localhost:8888/unified-console.html
|_http-wordpress-users: [Error] Wordpress installation was not found. We couldn't find wp-login.php
| http-enum: 
|_  /status/: Potentially interesting folder
|_http-referer-checker: Couldn't find any cross-domain scripts.
| http-methods: 
|_  Supported Methods: GET POST
|_http-wordpress-enum: Nothing found amongst the top 100 resources,use --script-args search-limit=<number|all> for deeper analysis)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-mobileversion-checker: No mobile version detected.
| http-comments-displayer: 
| Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=localhost
|     
|     Path: http://localhost:8888/console-config.js
|     Line number: 1
|     Comment: 
|         /*
|          * Licensed to the Apache Software Foundation (ASF) under one
|          * or more contributor license agreements.  See the NOTICE file
|          * distributed with this work for additional information
|          * regarding copyright ownership.  The ASF licenses this file
|          * to you under the Apache License, Version 2.0 (the
|          * "License"); you may not use this file except in compliance
|          * with the License.  You may obtain a copy of the License at
|          *
|          *     http://www.apache.org/licenses/LICENSE-2.0
|          *
|          * Unless required by applicable law or agreed to in writing, software
|          * distributed under the License is distributed on an "AS IS" BASIS,
|          * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
|          * See the License for the specific language governing permissions and
|          * limitations under the License.
|          */
|     
|     Path: http://localhost:8888/unified-console.html
|     Line number: 2
|     Comment: 
|         <!--
|           ~ Licensed to the Apache Software Foundation (ASF) under one
|           ~ or more contributor license agreements.  See the NOTICE file
|           ~ distributed with this work for additional information
|           ~ regarding copyright ownership.  The ASF licenses this file
|           ~ to you under the Apache License, Version 2.0 (the
|           ~ "License"); you may not use this file except in compliance
|           ~ with the License.  You may obtain a copy of the License at
|           ~
|           ~   http://www.apache.org/licenses/LICENSE-2.0
|           ~
|           ~ Unless required by applicable law or agreed to in writing,
|           ~ software distributed under the License is distributed on an
|           ~ "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
|           ~ KIND, either express or implied.  See the License for the
|           ~ specific language governing permissions and limitations
|           ~ under the License.
|           -->
|     
|     Path: http://localhost:8888/console-config.js
|     Line number: 21
|     Comment: 
|_        /* future configs may go here */
|_http-chrono: Request times for /unified-console.html; avg: 271.86ms; min: 217.82ms; max: 305.59ms
|_http-drupal-enum: Nothing found amongst the top 100 resources,use --script-args number=<number|all> for deeper analysis)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.

Read data files from: /usr/share/nmap
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Tue Aug  4 16:32:02 2026 -- 1 IP address (1 host up) scanned in 56.20 seconds

```
