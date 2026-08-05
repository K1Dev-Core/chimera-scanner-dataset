```bash
nikto -ask=no -Tuning=x4567890ac -nointeractive -host http://127.0.0.1:8080 2>&1 | tee "/home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_nikto.txt"
```

[/home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_nikto.txt](file:///home/kali/dataset/raw/autorecon/2026-08-04/jackson_7525/127.0.0.1/scans/tcp8080/tcp_8080_http_nikto.txt):

```
- Nikto v2.6.0
---------------------------------------------------------------------------
+ Target IP:          127.0.0.1
+ Target Hostname:    127.0.0.1
+ Target Port:        8080
+ Platform:           Unknown
+ Start Time:         2026-08-04 18:02:45 (GMT-4)
---------------------------------------------------------------------------
+ Server: No banner retrieved
+ ERROR: Failed to check for updates: 403
+ No CGI Directories found (use '-C all' to force check all possible dirs). CGI tests skipped.
+ [013587] /: Suggested security header missing: referrer-policy. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy
+ [013587] /: Suggested security header missing: content-security-policy. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
+ [013587] /: Suggested security header missing: permissions-policy. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy
+ [013587] /: Suggested security header missing: x-content-type-options. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options
+ [013587] /: Suggested security header missing: strict-transport-security. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security
+ [007342] /: X-Frame-Options header is deprecated and was replaced with the Content-Security-Policy HTTP header with the frame-ancestors directive. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Frame-Options
+ [007352] /: The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type. See: https://www.netsparker.com/web-vulnerability-scanner/vulnerabilities/missing-content-type-header/
+ 7598 requests: 0 errors and 7 items reported on the remote host
+ End Time:           2026-08-04 18:04:30 (GMT-4) (105 seconds)
---------------------------------------------------------------------------
+ 1 host(s) tested

```
