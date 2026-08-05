```bash
whatweb --color=never --no-errors -a 3 -v http://127.0.0.1:8888 2>&1
```

[/home/kali/dataset/raw/autorecon/2026-08-04/druid_25646/127.0.0.1/scans/tcp8888/tcp_8888_http_whatweb.txt](file:///home/kali/dataset/raw/autorecon/2026-08-04/druid_25646/127.0.0.1/scans/tcp8888/tcp_8888_http_whatweb.txt):

```
WhatWeb report for http://127.0.0.1:8888
Status    : 302 Found
Title     : <None>
IP        : 127.0.0.1
Country   : RESERVED, ZZ

Summary   : RedirectLocation[http://127.0.0.1:8888/unified-console.html]

Detected Plugins:
[ RedirectLocation ]
	HTTP Server string location. used with http-status 301 and
	302

	String       : http://127.0.0.1:8888/unified-console.html (from location)

HTTP Headers:
	HTTP/1.1 302 Found
	Connection: close
	Date: Tue, 04 Aug 2026 20:31:08 GMT
	Location: http://127.0.0.1:8888/unified-console.html
	Content-Length: 0

WhatWeb report for http://127.0.0.1:8888/unified-console.html
Status    : 200 OK
Title     : Apache Druid
IP        : 127.0.0.1
Country   : RESERVED, ZZ

Summary   : HTML5, Script

Detected Plugins:
[ HTML5 ]
	HTML version 5, detected by the doctype declaration


[ Script ]
	This plugin detects instances of script HTML elements and
	returns the script language/type.


HTTP Headers:
	HTTP/1.1 200 OK
	Connection: close
	Date: Tue, 04 Aug 2026 20:31:12 GMT
	Last-Modified: Thu, 08 Oct 2020 21:58:58 GMT
	Content-Type: text/html
	Accept-Ranges: bytes
	Vary: Accept-Encoding, User-Agent
	Content-Encoding: gzip
	Content-Length: 753



```
