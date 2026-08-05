```bash
feroxbuster -u http://127.0.0.11:18080/ -t 10 -w /root/.local/share/AutoRecon/wordlists/dirbuster.txt -x "txt,html,php,asp,aspx,jsp" -v -k -n -q -e -r -o "/home/kali/dataset/raw/autorecon/2026-08-04/struts2_s2045/127.0.0.11/scans/tcp18080/tcp_18080_http_feroxbuster_dirbuster.txt"
```

[/home/kali/dataset/raw/autorecon/2026-08-04/struts2_s2045/127.0.0.11/scans/tcp18080/tcp_18080_http_feroxbuster_dirbuster.txt](file:///home/kali/dataset/raw/autorecon/2026-08-04/struts2_s2045/127.0.0.11/scans/tcp18080/tcp_18080_http_feroxbuster_dirbuster.txt):

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
    target_url: "http://127.0.0.11:18080/",
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
    output: "/home/kali/dataset/raw/autorecon/2026-08-04/struts2_s2045/127.0.0.11/scans/tcp18080/tcp_18080_http_feroxbuster_dirbuster.txt",
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
                    127.0.0.11,
                ),
            ),
            port: Some(
                18080,
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
500      GET       38l      106w     2709c http://127.0.0.11:18080/@
500      GET       38l      112w     2797c http://127.0.0.11:18080/Documents%20and%20Settings
500      GET       38l      109w     2759c http://127.0.0.11:18080/Program%20Files
500      GET       38l      106w     2745c http://127.0.0.11:18080/lost+found
500      GET       38l      109w     2755c http://127.0.0.11:18080/reports%20list
200      GET       28l       34w      495c http://127.0.0.11:18080/upload
500      GET       38l      106w     2721c http://127.0.0.11:18080/~adm
500      GET       38l      106w     2729c http://127.0.0.11:18080/~admin
500      GET       38l      106w     2733c http://127.0.0.11:18080/~amanda
500      GET       38l      106w     2733c http://127.0.0.11:18080/~apache
500      GET       38l      106w     2761c http://127.0.0.11:18080/~administrator
500      GET       38l      106w     2721c http://127.0.0.11:18080/~bin
500      GET       38l      106w     2729c http://127.0.0.11:18080/~guest
500      GET       38l      106w     2729c http://127.0.0.11:18080/~httpd
500      GET       38l      106w     2725c http://127.0.0.11:18080/~http
500      GET       38l      106w     2721c http://127.0.0.11:18080/~log
500      GET       38l      106w     2717c http://127.0.0.11:18080/~lp
500      GET       38l      106w     2741c http://127.0.0.11:18080/~operator
500      GET       38l      106w     2725c http://127.0.0.11:18080/~root
500      GET       38l      106w     2741c http://127.0.0.11:18080/~sysadmin
500      GET       38l      106w     2721c http://127.0.0.11:18080/~tmp
500      GET       38l      106w     2725c http://127.0.0.11:18080/~user
500      GET       38l      106w     2725c http://127.0.0.11:18080/~test
500      GET       38l      106w     2725c http://127.0.0.11:18080/~mail
500      GET       38l      106w     2733c http://127.0.0.11:18080/~nobody
500      GET       38l      106w     2721c http://127.0.0.11:18080/~sys
500      GET       38l      106w     2725c http://127.0.0.11:18080/~logs
500      GET       38l      106w     2745c http://127.0.0.11:18080/~webmaster
500      GET       38l      106w     2721c http://127.0.0.11:18080/~www
500      GET       38l      106w     2733c http://127.0.0.11:18080/~sysadm
500      GET       38l      106w     2709c http://127.0.0.11:18080/[
500      GET       38l      106w     2709c http://127.0.0.11:18080/]
500      GET       38l      106w     2752c http://127.0.0.11:18080/anv%C3%A4ndare
500      GET       38l      109w     2747c http://127.0.0.11:18080/contact%20us
500      GET       38l      109w     2751c http://127.0.0.11:18080/donate%20cash
500      GET       38l      109w     2763c http://127.0.0.11:18080/external%20files
500      GET       38l      109w     2743c http://127.0.0.11:18080/home%20page
500      GET       38l      106w     2747c http://127.0.0.11:18080/lost%2Bfound
500      GET       38l      109w     2747c http://127.0.0.11:18080/modern%20mom
500      GET       38l      109w     2747c http://127.0.0.11:18080/my%20project
500      GET       38l      112w     2769c http://127.0.0.11:18080/neuf%20giga%20photo
500      GET       38l      106w     2729c http://127.0.0.11:18080/plain]
500      GET       38l      109w     2763c http://127.0.0.11:18080/planned%20giving
500      GET       38l      109w     2763c http://127.0.0.11:18080/press%20releases
500      GET       38l      109w     2763c http://127.0.0.11:18080/privacy%20policy
500      GET       38l      106w     2729c http://127.0.0.11:18080/quote]
500      GET       38l      109w     2739c http://127.0.0.11:18080/site%20map
500      GET       38l      109w     2759c http://127.0.0.11:18080/style%20library
500      GET       38l      109w     2763c http://127.0.0.11:18080/web%20references
500      GET       38l      106w     2713c http://127.0.0.11:18080/~r
500      GET       38l      106w     2733c http://127.0.0.11:18080/~images
500      GET       38l      106w     2725c http://127.0.0.11:18080/~mike
500      GET       38l      106w     2729c http://127.0.0.11:18080/~chris
500      GET       38l      106w     2725c http://127.0.0.11:18080/~site
500      GET       38l      106w     2713c http://127.0.0.11:18080/~a
500      GET       38l      106w     2721c http://127.0.0.11:18080/~joe
500      GET       38l      106w     2725c http://127.0.0.11:18080/~sys~

```
