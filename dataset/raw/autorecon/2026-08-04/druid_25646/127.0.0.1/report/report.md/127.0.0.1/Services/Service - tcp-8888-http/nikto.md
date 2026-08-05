```bash
nikto -ask=no -Tuning=x4567890ac -nointeractive -host http://127.0.0.1:8888 2>&1 | tee "/home/kali/dataset/raw/autorecon/2026-08-04/druid_25646/127.0.0.1/scans/tcp8888/tcp_8888_http_nikto.txt"
```

[/home/kali/dataset/raw/autorecon/2026-08-04/druid_25646/127.0.0.1/scans/tcp8888/tcp_8888_http_nikto.txt](file:///home/kali/dataset/raw/autorecon/2026-08-04/druid_25646/127.0.0.1/scans/tcp8888/tcp_8888_http_nikto.txt):

```
- Nikto v2.6.0
---------------------------------------------------------------------------
+ Target IP:          127.0.0.1
+ Target Hostname:    127.0.0.1
+ Target Port:        8888
+ Platform:           Unknown
+ Start Time:         2026-08-04 16:31:08 (GMT-4)
---------------------------------------------------------------------------
+ Server: No banner retrieved
+ ERROR: Failed to check for updates: 403
+ No CGI Directories found (use '-C all' to force check all possible dirs). CGI tests skipped.
+ [999979] /: RFC-1918 IP address found in the 'location' header. The IP is "172.28.0.2". See: https://portswigger.net/kb/issues/00600300_private-ip-addresses-disclosed
+ [999988] /: The web server may reveal its internal or real IP in the Location header via a request to with HTTP/1.0. The value is "172.28.0.2". See: https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2000-0649
+ [013587] /: Suggested security header missing: strict-transport-security. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security
+ [013587] /: Suggested security header missing: content-security-policy. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
+ [013587] /: Suggested security header missing: permissions-policy. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy
+ [013587] /: Suggested security header missing: x-content-type-options. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options
+ [013587] /: Suggested security header missing: referrer-policy. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy
+ [001873] /status/: This might be interesting.
+ [007342] /: X-Frame-Options header is deprecated and was replaced with the Content-Security-Policy HTTP header with the frame-ancestors directive. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Frame-Options
+ [007352] /: The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type. See: https://www.netsparker.com/web-vulnerability-scanner/vulnerabilities/missing-content-type-header/
+ 7825 requests: 0 errors and 10 items reported on the remote host
+ End Time:           2026-08-04 16:32:40 (GMT-4) (92 seconds)
---------------------------------------------------------------------------
+ 1 host(s) tested

```
