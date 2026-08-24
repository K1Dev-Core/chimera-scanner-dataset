#!/usr/bin/env bash

set -euo pipefail

echo "[+] Verified source set date: 2026-08-03"
echo "[+] Installing Docker, Kali security tools, and cloning app platforms"

if [[ "${EUID}" -ne 0 ]]; then
  echo "[!] Please run this script with sudo:"
  echo "    sudo bash $0"
  exit 1
fi

TARGET_USER="${SUDO_USER:-root}"
TARGET_HOME="$(getent passwd "${TARGET_USER}" | cut -d: -f6)"
PLATFORMS_DIR="${TARGET_HOME}/sec-platforms"
LABS_DIR="${TARGET_HOME}/labs"
DOCKER_ARCH="$(dpkg --print-architecture)"

echo "[+] Updating apt cache"
apt update

echo "[+] Installing base packages"
apt install -y \
  ca-certificates \
  curl \
  git \
  gnupg \
  jq \
  wget

echo "[+] Configuring Docker repository for Kali via Debian-compatible instructions"
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

cat >/etc/apt/sources.list.d/docker.sources <<'EOF'
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: trixie
Components: stable
Architectures: __ARCH__
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sed -i "s/__ARCH__/${DOCKER_ARCH}/" /etc/apt/sources.list.d/docker.sources

echo "[+] Refreshing apt metadata after adding Docker repo"
apt update

echo "[+] Installing Docker Engine and Compose plugin"
apt install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

systemctl enable --now docker
usermod -aG docker "${TARGET_USER}" || true

echo "[+] Verifying Docker"
docker --version
docker compose version

echo "[+] Installing security tools from Kali repositories"
apt install -y \
  gvm \
  zaproxy \
  nuclei \
  wapiti \
  subfinder \
  httpx-toolkit \
  naabu \
  autorecon \
  amass \
  metasploit-framework \
  sqlmap \
  nikto \
  nmap \
  seclists

echo "[+] Initializing Greenbone / GVM (this can take a while)"
gvm-setup || true
gvm-check-setup || true

echo "[+] Initializing Metasploit database"
msfdb init || true

echo "[+] Creating workspace directories"
mkdir -p "${PLATFORMS_DIR}" "${LABS_DIR}"
chown -R "${TARGET_USER}:${TARGET_USER}" "${PLATFORMS_DIR}" "${LABS_DIR}"

echo "[+] Cloning platform repositories"
runuser -u "${TARGET_USER}" -- bash -lc "
  set -euo pipefail
  mkdir -p '${PLATFORMS_DIR}'
  cd '${PLATFORMS_DIR}'
  [[ -d faraday ]] || git clone https://github.com/infobyte/faraday.git
  [[ -d django-DefectDojo ]] || git clone https://github.com/DefectDojo/django-DefectDojo.git
  [[ -d reconmap ]] || git clone https://github.com/reconmap/reconmap.git
"

echo "[+] Cloning Vulhub"
runuser -u "${TARGET_USER}" -- bash -lc "
  set -euo pipefail
  mkdir -p '${LABS_DIR}'
  cd '${LABS_DIR}'
  [[ -d vulhub ]] || git clone --depth 1 https://github.com/vulhub/vulhub.git
"

cat <<EOF

[+] Install phase complete.

Next steps:
  1. Log out and log back in so docker group membership applies to ${TARGET_USER}
  2. Start each platform when needed:

     Faraday:
       cd ${PLATFORMS_DIR}/faraday
       docker compose up -d

     DefectDojo:
       cd ${PLATFORMS_DIR}/django-DefectDojo
       docker compose up -d
       docker compose logs initializer | grep "Admin password:"

     Reconmap:
       cd ${PLATFORMS_DIR}/reconmap
       docker compose up -d

     Greenbone:
       gvm-start

     Vulhub example:
       cd ${LABS_DIR}/vulhub
       find . -maxdepth 2 -name docker-compose.yml -o -name compose.yml | head
       cd <chosen-scenario-directory>
       docker compose up -d

EOF
