```bash
curl -sSik http://127.0.0.11:18080/
```

[/home/kali/dataset/raw/autorecon/2026-08-04/struts2_s2045/127.0.0.11/scans/tcp18080/tcp_18080_http_curl.html](file:///home/kali/dataset/raw/autorecon/2026-08-04/struts2_s2045/127.0.0.11/scans/tcp18080/tcp_18080_http_curl.html):

```
HTTP/1.1 200 OK
Date: Tue, 04 Aug 2026 20:31:56 GMT
Content-Type: text/html; charset=ISO-8859-1
Set-Cookie: JSESSIONID=1ehdc0tkosn5f1sc1z0tuuf8k6;Path=/
Expires: Thu, 01 Jan 1970 00:00:00 GMT
Content-Length: 1078
Server: Jetty(9.2.11.v20150529)


<html>
<head>
   <title>Struts2 Showcase - Fileupload sample</title>
</head>

<body>
<div class="page-header">
   <h1>Fileupload sample</h1>
</div>

<div class="container-fluid">
   <div class="row-fluid">
      <div class="span12">


         <form id="doUpload" name="doUpload" action="/doUpload.action;jsessionid=1ehdc0tkosn5f1sc1z0tuuf8k6" method="POST" enctype="multipart/form-data">
<table class="wwFormTable">
            <tr>
    <td class="tdLabel"><label for="doUpload_upload" class="label">File:</label></td>
    <td
><input type="file" name="upload" value="" id="doUpload_upload"/></td>
</tr>


            <tr>
    <td class="tdLabel"><label for="doUpload_caption" class="label">Caption:</label></td>
    <td
><input type="text" name="caption" value="" id="doUpload_caption"/></td>
</tr>


            <tr>
    <td colspan="2"><div align="right"><input type="submit" value="Submit" id="doUpload_0" class="btn btn-primary"/>
</div></td>
</tr>


         </table></form>



      </div>
   </div>
</div>
</body>
</html>


```
