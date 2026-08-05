```bash
nikto -ask=no -Tuning=x4567890ac -nointeractive -host http://127.0.0.1:18083 2>&1 | tee "/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/tcp_18083_http_nikto.txt"
```

[/home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/tcp_18083_http_nikto.txt](file:///home/kali/dataset/raw/autorecon/2026-08-04/elfinder_32682/127.0.0.1/scans/tcp18083/tcp_18083_http_nikto.txt):

```
- Nikto v2.6.0
---------------------------------------------------------------------------
+ Target IP:          127.0.0.1
+ Target Hostname:    127.0.0.1
+ Target Port:        18083
+ Platform:           Linux/Unix
+ Start Time:         2026-08-04 16:45:34 (GMT-4)
---------------------------------------------------------------------------
+ Server: Apache/2.4.52 (Debian)
+ ERROR: Failed to check for updates: 403
+ No CGI Directories found (use '-C all' to force check all possible dirs). CGI tests skipped.
+ [999984] /: Server may leak inodes via ETags, header found with file /, inode: df6, size: 5d8efd05b9700, mtime: gzip. See: https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2003-1418
+ [013587] /: Suggested security header missing: referrer-policy. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy
+ [013587] /: Suggested security header missing: content-security-policy. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
+ [013587] /: Suggested security header missing: x-content-type-options. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options
+ [013587] /: Suggested security header missing: strict-transport-security. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security
+ [013587] /: Suggested security header missing: permissions-policy. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy
+ [600050] Apache/2.4.52 appears to be outdated (current is at least 2.4.66).
+ [999990] OPTIONS: Allowed HTTP Methods: GET, POST, OPTIONS, HEAD .
+ [007094] /composer.json: PHP Composer configuration file reveals configuration information. See: https://getcomposer.org/
+ [007224] /.gitignore: .gitignore file found. It is possible to grasp the directory structure.
+ [007302] /README.md: Readme Found.
+ [007342] /: X-Frame-Options header is deprecated and was replaced with the Content-Security-Policy HTTP header with the frame-ancestors directive. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Frame-Options
+ [007352] /: The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type. See: https://www.netsparker.com/web-vulnerability-scanner/vulnerabilities/missing-content-type-header/
+ 7721 requests: 16 errors and 13 items reported on the remote host
+ End Time:           2026-08-04 16:52:11 (GMT-4) (397 seconds)
---------------------------------------------------------------------------
+ 1 host(s) tested

```
