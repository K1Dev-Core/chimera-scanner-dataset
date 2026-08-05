param(
  [string]$DatasetRoot = ".",
  [int]$ZapMinutes = 1
)

$ErrorActionPreference = "Continue"
$DatasetRoot = (Resolve-Path $DatasetRoot).Path
$date = "2026-08-05"
$toolsRoot = Join-Path $DatasetRoot "datasets\tools-name-date"
$targets = @(
  @{ Id = "acme-support"; Url = "http://host.docker.internal:27000/"; HostPort = "27000"; Product = "Acme Support Portal" },
  @{ Id = "nova-devops"; Url = "http://host.docker.internal:27100/"; HostPort = "27100"; Product = "Nova DevOps Console" }
)

function Ensure-Dir([string]$Path) {
  New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Run-Logged([string]$Tool, [hashtable]$Target, [scriptblock]$Body) {
  $lab = $Target.Id
  $raw = Join-Path $toolsRoot "$Tool-$date\$lab\raw"
  Ensure-Dir $raw
  $started = (Get-Date).ToUniversalTime().ToString("o")
  $status = "ok"
  $errorText = ""
  try {
    & $Body $raw
    if ($LASTEXITCODE -ne 0) {
      $status = "nonzero_exit_$LASTEXITCODE"
    }
  } catch {
    $status = "exception"
    $errorText = $_.Exception.Message
  }
  $ended = (Get-Date).ToUniversalTime().ToString("o")
  $meta = [ordered]@{
    tool = $Tool
    lab_id = $lab
    target_url = $Target.Url
    host_port = $Target.HostPort
    product = $Target.Product
    started_at = $started
    ended_at = $ended
    status = $status
    error = $errorText
  }
  $meta | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $raw "run-metadata.json") -Encoding utf8
}

foreach ($target in $targets) {
  Run-Logged "nmap" $target {
    param($raw)
    docker run --rm -v "${raw}:/out" instrumentisto/nmap -sV -Pn -p $target.HostPort -oX /out/nmap.xml -oN /out/nmap.txt host.docker.internal
  }

  Run-Logged "httpx" $target {
    param($raw)
    Set-Content -LiteralPath (Join-Path $raw "targets.txt") -Value $target.Url -Encoding ascii
    docker run --rm -v "${raw}:/out" projectdiscovery/httpx -l /out/targets.txt -json -title -tech-detect -status-code -content-length -o /out/httpx.jsonl -silent
  }

  Run-Logged "nuclei" $target {
    param($raw)
    Set-Content -LiteralPath (Join-Path $raw "targets.txt") -Value $target.Url -Encoding ascii
    docker run --rm -v "${raw}:/out" projectdiscovery/nuclei -l /out/targets.txt -jsonl -o /out/nuclei.jsonl -severity info,low,medium,high,critical -rl 5 -c 5 -timeout 5 -retries 0 -silent
  }

  Run-Logged "nikto" $target {
    param($raw)
    docker run --rm -v "${raw}:/out" ghcr.io/sullo/nikto -h $target.Url -Format json -output /out/nikto.json -nointeractive
  }

  Run-Logged "wapiti" $target {
    param($raw)
    docker run --rm -v "${raw}:/out" cyberwatch/wapiti wapiti -u $target.Url -f json -o /out/wapiti.json --scope page --max-depth 1 --max-links-per-page 20 --max-scan-time 180 --flush-session
  }

  Run-Logged "zap" $target {
    param($raw)
    docker run --rm -v "${raw}:/zap/wrk" ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t $target.Url -J zap.json -r zap.html -m $ZapMinutes -I
  }
}
