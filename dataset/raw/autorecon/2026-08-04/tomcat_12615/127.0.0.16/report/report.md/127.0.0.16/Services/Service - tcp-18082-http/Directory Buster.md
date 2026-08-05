```bash
feroxbuster -u http://127.0.0.16:18082/ -t 10 -w /root/.local/share/AutoRecon/wordlists/dirbuster.txt -x "txt,html,php,asp,aspx,jsp" -v -k -n -q -e -r -o "/home/kali/dataset/raw/autorecon/2026-08-04/tomcat_12615/127.0.0.16/scans/tcp18082/tcp_18082_http_feroxbuster_dirbuster.txt"
```

[/home/kali/dataset/raw/autorecon/2026-08-04/tomcat_12615/127.0.0.16/scans/tcp18082/tcp_18082_http_feroxbuster_dirbuster.txt](file:///home/kali/dataset/raw/autorecon/2026-08-04/tomcat_12615/127.0.0.16/scans/tcp18082/tcp_18082_http_feroxbuster_dirbuster.txt):

```
Configuration {
    kind: "configuration",
    wordlist: "/root/.local/share/AutoRecon/wordlists/dirbuster.txt",
    config: "/etc/feroxbuster/ferox-config.toml",
    proxy: "",
    replay_proxy: "",
    server_certs: [],
    client_cert: "",
    client_key: "",
    target_url: "http://127.0.0.16:18082/",
    status_codes: [
        100,
        101,
        102,
        200,
        201,
        202,
        203,
        204,
        205,
        206,
        207,
        208,
        226,
        300,
        301,
        302,
        303,
        304,
        305,
        307,
        308,
        400,
        401,
        402,
        403,
        404,
        405,
        406,
        407,
        408,
        409,
        410,
        411,
        412,
        413,
        414,
        415,
        416,
        417,
        418,
        421,
        422,
        423,
        424,
        426,
        428,
        429,
        431,
        451,
        500,
        501,
        502,
        503,
        504,
        505,
        506,
        507,
        508,
        510,
        511,
        103,
        425,
    ],
    replay_codes: [
        100,
        101,
        102,
        200,
        201,
        202,
        203,
        204,
        205,
        206,
        207,
        208,
        226,
        300,
        301,
        302,
        303,
        304,
        305,
        307,
        308,
        400,
        401,
        402,
        403,
        404,
        405,
        406,
        407,
        408,
        409,
        410,
        411,
        412,
        413,
        414,
        415,
        416,
        417,
        418,
        421,
        422,
        423,
        424,
        426,
        428,
        429,
        431,
        451,
        500,
        501,
        502,
        503,
        504,
        505,
        506,
        507,
        508,
        510,
        511,
        103,
        425,
    ],
    filter_status: [],
    client: Client {
        accepts: Accepts,
        proxies: [
            Matcher,
        ],
        redirect_policy: "Policy(Custom)",
        referer: true,
        default_headers: {
            "accept": "*/*",
            "user-agent": "feroxbuster/2.13.1",
        },
        reqwest::config::RequestTimeout: 7s,
    },
    replay_client: None,
    threads: 10,
    timeout: 7,
    verbosity: 1,
    silent: false,
    quiet: true,
    output_level: Quiet,
    auto_bail: false,
    auto_tune: false,
    requester_policy: Default,
    json: false,
    output: "/home/kali/dataset/raw/autorecon/2026-08-04/tomcat_12615/127.0.0.16/scans/tcp18082/tcp_18082_http_feroxbuster_dirbuster.txt",
    debug_log: "",
    user_agent: "feroxbuster/2.13.1",
    random_agent: false,
    redirects: true,
    insecure: true,
    extensions: [
        "txt",
        "html",
        "php",
        "asp",
        "aspx",
        "jsp",
    ],
    methods: [
        "GET",
    ],
    data: [],
    headers: {},
    queries: [],
    no_recursion: true,
    extract_links: true,
    add_slash: false,
    stdin: false,
    cached_stdin: [],
    depth: 4,
    scan_limit: 0,
    parallel: 0,
    rate_limit: 0,
    filter_size: [],
    filter_line_count: [],
    filter_word_count: [],
    filter_regex: [],
    dont_filter: false,
    resumed: false,
    resume_from: "",
    save_state: true,
    time_limit: "",
    filter_similar: [],
    url_denylist: [],
    regex_denylist: [],
    scope: [
        Url {
            scheme: "http",
            cannot_be_a_base: false,
            username: "",
            password: None,
            host: Some(
                Ipv4(
                    127.0.0.16,
                ),
            ),
            port: Some(
                18082,
            ),
            path: "/",
            query: None,
            fragment: None,
        },
    ],
    collect_extensions: false,
    dont_collect: [
        "woff2",
        "woff",
        "ttf",
        "otf",
        "eot",
        "tif",
        "tiff",
        "ico",
        "cur",
        "bmp",
        "webp",
        "svg",
        "png",
        "jpg",
        "jpeg",
        "jfif",
        "gif",
        "avif",
        "apng",
        "pjpeg",
        "pjp",
        "mov",
        "wav",
        "mpg",
        "mpeg",
        "mp3",
        "mp4",
        "m4a",
        "m4p",
        "m4v",
        "ogg",
        "webm",
        "ogv",
        "oga",
        "flac",
        "aac",
        "3gp",
        "css",
        "zip",
        "xls",
        "xml",
        "gz",
        "tgz",
    ],
    collect_backups: false,
    backup_extensions: [
        "~",
        ".bak",
        ".bak2",
        ".old",
        ".1",
    ],
    collect_words: false,
    force_recursion: false,
    update_app: false,
    scan_dir_listings: false,
    request_file: "",
    protocol: "https",
    limit_bars: 0,
    unique: false,
    response_size_limit: 4194304,
}
200      GET      168l     1111w    12880c http://127.0.0.16:18082/docs/setup.html
200      GET       18l      126w     9193c http://127.0.0.16:18082/tomcat.png
200      GET      177l      935w     7064c http://127.0.0.16:18082/docs/RELEASE-NOTES.txt
200      GET      351l      786w     5581c http://127.0.0.16:18082/tomcat.css
200      GET       22l       93w    42556c http://127.0.0.16:18082/favicon.ico
200      GET      351l     2076w    22688c http://127.0.0.16:18082/docs/deployer-howto.html
403      GET       83l      431w     3420c http://127.0.0.16:18082/manager/html
403      GET       83l      431w     3420c http://127.0.0.16:18082/manager/status
200      GET     1223l     6948w    63145c http://127.0.0.16:18082/docs/realm-howto.html
200      GET       34l      158w     1155c http://127.0.0.16:18082/docs/api/index.html
403      GET       73l      389w     3022c http://127.0.0.16:18082/host-manager/html
200      GET      676l     3577w    35168c http://127.0.0.16:18082/docs/jndi-datasource-examples-howto.html
200      GET      669l     4114w    43713c http://127.0.0.16:18082/docs/cluster-howto.html
200      GET      543l     3927w    36867c http://127.0.0.16:18082/docs/security-howto.html
200      GET     1405l     7670w    72733c http://127.0.0.16:18082/docs/manager-howto.html
200      GET     3075l    16518w   177464c http://127.0.0.16:18082/docs/changelog.html
200      GET      202l      498w    11230c http://127.0.0.16:18082/
200      GET      278l     1402w    15813c http://127.0.0.16:18082/docs/building.html
200      GET      249l     1630w    17891c http://127.0.0.16:18082/docs/class-loader-howto.html
200      GET      155l     1127w    13219c http://127.0.0.16:18082/docs/proxy-howto.html
200      GET      107l      697w     9146c http://127.0.0.16:18082/docs/config/index.html
200      GET      173l      951w    12762c http://127.0.0.16:18082/docs/apr.html
200      GET     1056l     5305w    53611c http://127.0.0.16:18082/docs/jndi-resources-howto.html
200      GET       34l      158w     1145c http://127.0.0.16:18082/docs/jspapi/index.html
200      GET     1136l     3029w    39095c http://127.0.0.16:18082/docs/monitoring.html
200      GET      136l      879w    10846c http://127.0.0.16:18082/docs/cgi-howto.html
200      GET      340l     2030w    22437c http://127.0.0.16:18082/docs/windows-auth-howto.html
200      GET      302l     1430w    18306c http://127.0.0.16:18082/docs/default-servlet.html
200      GET       34l      158w     1149c http://127.0.0.16:18082/docs/servletapi/index.html
200      GET      472l     2017w    22485c http://127.0.0.16:18082/docs/windows-service-howto.html
200      GET       97l      688w     9113c http://127.0.0.16:18082/docs/aio.html
200      GET      122l      855w    10180c http://127.0.0.16:18082/docs/comments.html
200      GET       34l      158w     1144c http://127.0.0.16:18082/docs/elapi/index.html
200      GET       77l      370w     5219c http://127.0.0.16:18082/docs/architecture/index.html
200      GET      125l      839w    11521c http://127.0.0.16:18082/docs/web-socket-howto.html
200      GET      303l      768w     5780c http://127.0.0.16:18082/docs/images/docs-stylesheet.css
200      GET       18l      126w     9193c http://127.0.0.16:18082/docs/images/tomcat.png
200      GET       80l      487w     6198c http://127.0.0.16:18082/docs/funcspecs/index.html
200      GET       34l      158w     1151c http://127.0.0.16:18082/docs/websocketapi/index.html
200      GET       86l      652w     8721c http://127.0.0.16:18082/docs/connectors.html
200      GET      210l      566w    19698c http://127.0.0.16:18082/docs/images/asf-logo.svg
200      GET       61l      468w     7641c http://127.0.0.16:18082/docs/balancer-howto.html
200      GET      147l      994w    11849c http://127.0.0.16:18082/docs/introduction.html
200      GET       89l      556w     8645c http://127.0.0.16:18082/docs/developers.html
200      GET       89l      499w     8242c http://127.0.0.16:18082/docs/mbeans-descriptors-howto.html
200      GET      418l     2177w    24407c http://127.0.0.16:18082/docs/logging.html
200      GET      506l     2579w    29731c http://127.0.0.16:18082/docs/security-manager-howto.html
200      GET      579l     3866w    36572c http://127.0.0.16:18082/docs/ssl-howto.html
200      GET      717l     3212w    35176c http://127.0.0.16:18082/docs/rewrite.html
200      GET      929l     6166w    66772c http://127.0.0.16:18082/docs/jdbc-pool.html
200      GET      128l      775w    10450c http://127.0.0.16:18082/docs/extras.html
200      GET      232l     1279w    16866c http://127.0.0.16:18082/docs/index.html
200      GET      398l     1727w    17421c http://127.0.0.16:18082/docs/ssi-howto.html
200      GET      140l      762w    11471c http://127.0.0.16:18082/docs/virtual-hosting-howto.html
200      GET       87l      468w     6204c http://127.0.0.16:18082/docs/appdev/index.html
200      GET       32l      149w     1268c http://127.0.0.16:18082/examples/websocket/index.xhtml
200      GET      408l     2319w    23686c http://127.0.0.16:18082/docs/jasper-howto.html
200      GET       69l      475w     8164c http://127.0.0.16:18082/docs/maven-jars.html
200      GET      277l     2312w    19320c http://127.0.0.16:18082/docs/tribes/introduction.html
200      GET      232l     1279w    16866c http://127.0.0.16:18082/docs/
200      GET       30l      141w     1126c http://127.0.0.16:18082/examples/
403      GET       73l      389w     3022c http://127.0.0.16:18082/host-manager/text/css
403      GET       73l      389w     3022c http://127.0.0.16:18082/host-manager/host-manager/html
403      GET       73l      389w     3022c http://127.0.0.16:18082/host-manager/
200      GET      202l      498w    11230c http://127.0.0.16:18082/index.jsp
403      GET       83l      431w     3420c http://127.0.0.16:18082/manager/docs/manager-howto.html
403      GET       83l      431w     3420c http://127.0.0.16:18082/manager/text/css
403      GET       83l      431w     3420c http://127.0.0.16:18082/manager/manager/html
403      GET       83l      431w     3420c http://127.0.0.16:18082/manager/
Configuration {
    kind: "configuration",
    wordlist: "/root/.local/share/AutoRecon/wordlists/dirbuster.txt",
    config: "/etc/feroxbuster/ferox-config.toml",
    proxy: "",
    replay_proxy: "",
    server_certs: [],
    client_cert: "",
    client_key: "",
    target_url: "http://127.0.0.16:18082/",
    status_codes: [
        100,
        101,
        102,
        200,
        201,
        202,
        203,
        204,
        205,
        206,
        207,
        208,
        226,
        300,
        301,
        302,
        303,
        304,
        305,
        307,
        308,
        400,
        401,
        402,
        403,
        404,
        405,
        406,
        407,
        408,
        409,
        410,
        411,
        412,
        413,
        414,
        415,
        416,
        417,
        418,
        421,
        422,
        423,
        424,
        426,
        428,
        429,
        431,
        451,
        500,
        501,
        502,
        503,
        504,
        505,
        506,
        507,
        508,
        510,
        511,
        103,
        425,
    ],
    replay_codes: [
        100,
        101,
        102,
        200,
        201,
        202,
        203,
        204,
        205,
        206,
        207,
        208,
        226,
        300,
        301,
        302,
        303,
        304,
        305,
        307,
        308,
        400,
        401,
        402,
        403,
        404,
        405,
        406,
        407,
        408,
        409,
        410,
        411,
        412,
        413,
        414,
        415,
        416,
        417,
        418,
        421,
        422,
        423,
        424,
        426,
        428,
        429,
        431,
        451,
        500,
        501,
        502,
        503,
        504,
        505,
        506,
        507,
        508,
        510,
        511,
        103,
        425,
    ],
    filter_status: [],
    client: Client {
        accepts: Accepts,
        proxies: [
            Matcher,
        ],
        redirect_policy: "Policy(Custom)",
        referer: true,
        default_headers: {
            "accept": "*/*",
            "user-agent": "feroxbuster/2.13.1",
        },
        reqwest::config::RequestTimeout: 7s,
    },
    replay_client: None,
    threads: 10,
    timeout: 7,
    verbosity: 1,
    silent: false,
    quiet: true,
    output_level: Quiet,
    auto_bail: false,
    auto_tune: false,
    requester_policy: Default,
    json: false,
    output: "/home/kali/dataset/raw/autorecon/2026-08-04/tomcat_12615/127.0.0.16/scans/tcp18082/tcp_18082_http_feroxbuster_dirbuster.txt",
    debug_log: "",
    user_agent: "feroxbuster/2.13.1",
    random_agent: false,
    redirects: true,
    insecure: true,
    extensions: [
        "txt",
        "html",
        "php",
        "asp",
        "aspx",
        "jsp",
    ],
    methods: [
        "GET",
    ],
    data: [],
    headers: {},
    queries: [],
    no_recursion: true,
    extract_links: true,
    add_slash: false,
    stdin: false,
    cached_stdin: [],
    depth: 4,
    scan_limit: 0,
    parallel: 0,
    rate_limit: 0,
    filter_size: [],
    filter_line_count: [],
    filter_word_count: [],
    filter_regex: [],
    dont_filter: false,
    resumed: false,
    resume_from: "",
    save_state: true,
    time_limit: "",
    filter_similar: [],
    url_denylist: [],
    regex_denylist: [],
    scope: [
        Url {
            scheme: "http",
            cannot_be_a_base: false,
            username: "",
            password: None,
            host: Some(
                Ipv4(
                    127.0.0.16,
                ),
            ),
            port: Some(
                18082,
            ),
            path: "/",
            query: None,
            fragment: None,
        },
    ],
    collect_extensions: false,
    dont_collect: [
        "woff2",
        "woff",
        "ttf",
        "otf",
        "eot",
        "tif",
        "tiff",
        "ico",
        "cur",
        "bmp",
        "webp",
        "svg",
        "png",
        "jpg",
        "jpeg",
        "jfif",
        "gif",
        "avif",
        "apng",
        "pjpeg",
        "pjp",
        "mov",
        "wav",
        "mpg",
        "mpeg",
        "mp3",
        "mp4",
        "m4a",
        "m4p",
        "m4v",
        "ogg",
        "webm",
        "ogv",
        "oga",
        "flac",
        "aac",
        "3gp",
        "css",
        "zip",
        "xls",
        "xml",
        "gz",
        "tgz",
    ],
    collect_backups: false,
    backup_extensions: [
        "~",
        ".bak",
        ".bak2",
        ".old",
        ".1",
    ],
    collect_words: false,
    force_recursion: false,
    update_app: false,
    scan_dir_listings: false,
    request_file: "",
    protocol: "https",
    limit_bars: 0,
    unique: false,
    response_size_limit: 4194304,
}
403      GET       83l      431w     3420c http://127.0.0.16:18082/manager/status
200      GET      168l     1111w    12880c http://127.0.0.16:18082/docs/setup.html
200      GET       34l      158w     1155c http://127.0.0.16:18082/docs/api/index.html
403      GET       73l      389w     3022c http://127.0.0.16:18082/host-manager/html
200      GET      669l     4114w    43713c http://127.0.0.16:18082/docs/cluster-howto.html
403      GET       83l      431w     3420c http://127.0.0.16:18082/manager/html
200      GET      351l      786w     5581c http://127.0.0.16:18082/tomcat.css
200      GET       22l       93w    42556c http://127.0.0.16:18082/favicon.ico
200      GET      351l     2076w    22688c http://127.0.0.16:18082/docs/deployer-howto.html
200      GET       18l      126w     9193c http://127.0.0.16:18082/tomcat.png
200      GET     1223l     6948w    63145c http://127.0.0.16:18082/docs/realm-howto.html
200      GET      177l      935w     7064c http://127.0.0.16:18082/docs/RELEASE-NOTES.txt
200      GET      676l     3577w    35168c http://127.0.0.16:18082/docs/jndi-datasource-examples-howto.html
200      GET     1405l     7670w    72733c http://127.0.0.16:18082/docs/manager-howto.html
200      GET      543l     3927w    36867c http://127.0.0.16:18082/docs/security-howto.html
200      GET     3075l    16518w   177464c http://127.0.0.16:18082/docs/changelog.html
200      GET      202l      498w    11230c http://127.0.0.16:18082/
200      GET      136l      879w    10846c http://127.0.0.16:18082/docs/cgi-howto.html
200      GET       34l      158w     1151c http://127.0.0.16:18082/docs/websocketapi/index.html
200      GET      232l     1279w    16866c http://127.0.0.16:18082/docs/index.html
200      GET      210l      566w    19698c http://127.0.0.16:18082/docs/images/asf-logo.svg
200      GET      249l     1630w    17891c http://127.0.0.16:18082/docs/class-loader-howto.html
200      GET       86l      652w     8721c http://127.0.0.16:18082/docs/connectors.html
200      GET      140l      762w    11471c http://127.0.0.16:18082/docs/virtual-hosting-howto.html
200      GET      277l     2312w    19320c http://127.0.0.16:18082/docs/tribes/introduction.html
200      GET       18l      126w     9193c http://127.0.0.16:18082/docs/images/tomcat.png
200      GET       69l      475w     8164c http://127.0.0.16:18082/docs/maven-jars.html
200      GET      147l      994w    11849c http://127.0.0.16:18082/docs/introduction.html
200      GET      408l     2319w    23686c http://127.0.0.16:18082/docs/jasper-howto.html
200      GET      278l     1402w    15813c http://127.0.0.16:18082/docs/building.html
200      GET       80l      487w     6198c http://127.0.0.16:18082/docs/funcspecs/index.html
200      GET     1136l     3029w    39095c http://127.0.0.16:18082/docs/monitoring.html
200      GET       34l      158w     1149c http://127.0.0.16:18082/docs/servletapi/index.html
200      GET      579l     3866w    36572c http://127.0.0.16:18082/docs/ssl-howto.html
200      GET       77l      370w     5219c http://127.0.0.16:18082/docs/architecture/index.html
200      GET      107l      697w     9146c http://127.0.0.16:18082/docs/config/index.html
200      GET      472l     2017w    22485c http://127.0.0.16:18082/docs/windows-service-howto.html
200      GET      506l     2579w    29731c http://127.0.0.16:18082/docs/security-manager-howto.html
200      GET       89l      499w     8242c http://127.0.0.16:18082/docs/mbeans-descriptors-howto.html
200      GET      125l      839w    11521c http://127.0.0.16:18082/docs/web-socket-howto.html
200      GET      418l     2177w    24407c http://127.0.0.16:18082/docs/logging.html
200      GET      398l     1727w    17421c http://127.0.0.16:18082/docs/ssi-howto.html
200      GET      303l      768w     5780c http://127.0.0.16:18082/docs/images/docs-stylesheet.css
200      GET      717l     3212w    35176c http://127.0.0.16:18082/docs/rewrite.html
200      GET      122l      855w    10180c http://127.0.0.16:18082/docs/comments.html
200      GET      173l      951w    12762c http://127.0.0.16:18082/docs/apr.html
200      GET       61l      468w     7641c http://127.0.0.16:18082/docs/balancer-howto.html
200      GET       34l      158w     1145c http://127.0.0.16:18082/docs/jspapi/index.html
200      GET     1056l     5305w    53611c http://127.0.0.16:18082/docs/jndi-resources-howto.html
200      GET       97l      688w     9113c http://127.0.0.16:18082/docs/aio.html
200      GET      929l     6166w    66772c http://127.0.0.16:18082/docs/jdbc-pool.html
200      GET       87l      468w     6204c http://127.0.0.16:18082/docs/appdev/index.html
200      GET       34l      158w     1144c http://127.0.0.16:18082/docs/elapi/index.html
200      GET      155l     1127w    13219c http://127.0.0.16:18082/docs/proxy-howto.html
200      GET      302l     1430w    18306c http://127.0.0.16:18082/docs/default-servlet.html
200      GET      340l     2030w    22437c http://127.0.0.16:18082/docs/windows-auth-howto.html
200      GET       89l      556w     8645c http://127.0.0.16:18082/docs/developers.html
200      GET      128l      775w    10450c http://127.0.0.16:18082/docs/extras.html
200      GET      232l     1279w    16866c http://127.0.0.16:18082/docs/
200      GET       32l      149w     1268c http://127.0.0.16:18082/examples/websocket/index.xhtml
200      GET       30l      141w     1126c http://127.0.0.16:18082/examples/
403      GET       73l      389w     3022c http://127.0.0.16:18082/host-manager/text/css
403      GET       73l      389w     3022c http://127.0.0.16:18082/host-manager/host-manager/html
403      GET       73l      389w     3022c http://127.0.0.16:18082/host-manager/
200      GET      202l      498w    11230c http://127.0.0.16:18082/index.jsp
403      GET       83l      431w     3420c http://127.0.0.16:18082/manager/docs/manager-howto.html
403      GET       83l      431w     3420c http://127.0.0.16:18082/manager/text/css
403      GET       83l      431w     3420c http://127.0.0.16:18082/manager/manager/html
403      GET       83l      431w     3420c http://127.0.0.16:18082/manager/
200      GET      177l      935w     7064c http://127.0.0.16:18082/RELEASE-NOTES.txt

```
