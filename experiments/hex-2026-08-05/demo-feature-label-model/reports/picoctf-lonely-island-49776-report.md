# Chimera A/B Test Model Report

- generated_at: `2026-08-05T04:33:39.202638+00:00`
- target: `http://lonely-island.picoctf.net:49776/`
- status_code: `200`
- title: `Login - picoCTF demo`
- server: `Apache/2.4.66 (Debian)`
- content_type: `text/html; charset=UTF-8`
- form_count: `1`
- input_names: `password, username, viewport`
- discovered_links: `http://lonely-island.picoctf.net:49776/assets/css/styles.css, http://lonely-island.picoctf.net:49776/register.php`

## Ranked vulnerability families

| rank | family | score | reason |
|---:|---|---:|---|
| 1 | `auth-bypass` | 0.78 | login/register flow is the primary exposed surface |
| 2 | `sqli` | 0.68 | username/password POST form may depend on backend query handling |
| 3 | `broken-access-control` | 0.62 | social-app style account/session flows often expose authorization checks |
| 4 | `xss` | 0.48 | social posting/profile surfaces are plausible but not yet observed from login page |
| 5 | `sensitive-data-exposure` | 0.35 | framework/version header is visible; more evidence needed |
| 6 | `csrf` | 0.28 | state-changing forms exist; token evidence not yet collected |

## Limitation

This report is a safe prioritization aid from passive fingerprint only. It should be used to decide what to inspect first, not as proof that an exploit will work.

