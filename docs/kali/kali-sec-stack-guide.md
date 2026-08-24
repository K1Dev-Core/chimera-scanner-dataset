# Kali Security Stack Guide

Verified against upstream docs and project pages on 2026-08-03.

## What this includes

- Platform / vulnerability management:
  - Faraday
  - DefectDojo
  - Reconmap
- Vulnerability scanners:
  - Greenbone Community Edition / GVM
  - OWASP ZAP
  - Nuclei
  - Wapiti
- Recon / attack surface:
  - Subfinder
  - httpx-toolkit
  - Naabu
  - AutoRecon
  - Amass
- Exploitation / web testing:
  - Metasploit Framework
  - sqlmap
  - Nikto
- Lab environment:
  - Docker Engine
  - Vulhub

## Recommended flow on Kali

1. Install Docker first.
2. Install CLI tools from Kali repos.
3. Install GVM and run `gvm-setup`.
4. Clone Faraday, DefectDojo, Reconmap, and Vulhub.
5. Start only the stack you need, because running all of them together can be heavy on RAM and may create port conflicts.

## One-shot installer

The script was created in the Codex workspace here:

[kali-sec-stack-install.sh](C:\Users\rapii\Documents\Codex\2026-08-03\faraday-https-github-com-infobyte-faraday\outputs\kali-sec-stack-install.sh)

Copy it to Kali first, then run it.

Example if you already moved it into your Kali home directory:

```bash
chmod +x ~/kali-sec-stack-install.sh
sudo ~/kali-sec-stack-install.sh
```

## Important Kali note for Docker

Docker's official docs say Kali should follow the Debian install path and substitute the matching Debian codename. The script currently uses `trixie`, which is the safe default from Docker's current Debian guidance for Kali-like setups. If your Kali image is pinned differently, adjust the `Suites:` line in `/etc/apt/sources.list.d/docker.sources`.

## Quick run commands

```bash
# Faraday
cd ~/sec-platforms/faraday
docker compose up -d

# DefectDojo
cd ~/sec-platforms/django-DefectDojo
docker compose up -d
docker compose logs initializer | grep "Admin password:"

# Reconmap
cd ~/sec-platforms/reconmap
docker compose up -d

# Greenbone / GVM
sudo gvm-start

# Vulhub
cd ~/labs/vulhub
find . -maxdepth 2 -name docker-compose.yml -o -name compose.yml | head
cd <scenario-dir>
docker compose up -d
```

## What I checked on this machine

On this Windows workspace, as of 2026-08-03:

- `git` is installed
- `docker` and `docker compose` binaries are present
- Docker daemon is not running
- WSL is not installed

That means I can prepare the installation assets and commands cleanly, but I cannot fully stand up a Kali lab inside this machine without first enabling WSL or using a separate Kali VM.

## Source links

- [Faraday](https://github.com/infobyte/faraday)
- [DefectDojo install docs](https://docs.defectdojo.com/get_started/open_source/installation/)
- [DefectDojo repo](https://github.com/DefectDojo/django-DefectDojo)
- [Reconmap deployment docs](https://reconmap.com/admin-manual/deployment-options/)
- [Reconmap repo](https://github.com/reconmap/reconmap)
- [Docker Engine on Debian](https://docs.docker.com/engine/install/debian/)
- [Greenbone Community docs](https://greenbone.github.io/docs/latest/index.html)
- [Kali gvm package](https://www.kali.org/tools/gvm/)
- [Kali zaproxy package](https://www.kali.org/tools/zaproxy/)
- [Kali nuclei package](https://www.kali.org/tools/nuclei/)
- [Kali wapiti package](https://www.kali.org/tools/wapiti/)
- [Kali subfinder package](https://www.kali.org/tools/subfinder/)
- [Kali httpx-toolkit package](https://www.kali.org/tools/httpx-toolkit/)
- [Kali naabu package](https://www.kali.org/tools/naabu/)
- [Kali autorecon package](https://www.kali.org/tools/autorecon/)
- [OWASP Amass install guide](https://github.com/owasp-amass/amass/wiki/Installation-Guide)
- [Kali metasploit-framework package](https://www.kali.org/tools/metasploit-framework/)
- [Kali Metasploit database init guide](https://www.kali.org/docs/tools/starting-metasploit-framework-in-kali/)
- [sqlmap project wiki](https://github.com/sqlmapproject/sqlmap/wiki/usage)
- [Kali all tools index](https://www.kali.org/tools/all-tools/)
- [Nikto repo](https://github.com/sullo/nikto)
- [Kali nikto package](https://www.kali.org/tools/nikto/)
- [Vulhub](https://github.com/vulhub/vulhub)
