param(
  [string]$DatasetRoot = ".",
  [string]$WorkspaceRoot = "C:\Users\uSeR\Documents\Codex\2026-08-04\docker-cve-wp2shell-2",
  [string]$VulhubRoot = "C:\Users\uSeR\Documents\Codex\2026-08-04\docker-cve-wp2shell-2\work\vulhub",
  [string]$OutRoot = "",
  [int]$StartHostPort = 28000,
  [switch]$KeepRunning
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($OutRoot)) {
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $OutRoot = Join-Path $DatasetRoot "live-reports\vulhub-expansion-$stamp"
}

$manifestPath = Join-Path $DatasetRoot "records\staged-vulhub-expansion-labs.json"
if (!(Test-Path -LiteralPath $manifestPath)) {
  throw "Manifest not found: $manifestPath"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force -Path $OutRoot | Out-Null

function Write-Utf8File {
  param([string]$Path, [string]$Value)
  $dir = Split-Path -Parent $Path
  if (!(Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  [System.IO.File]::WriteAllText($Path, $Value, [System.Text.UTF8Encoding]::new($false))
}

function Run-Cmd {
  param([string]$FilePath, [string[]]$Args, [string]$WorkingDirectory)
  $psi = [System.Diagnostics.ProcessStartInfo]::new()
  $psi.FileName = $FilePath
  foreach ($arg in $Args) { [void]$psi.ArgumentList.Add($arg) }
  $psi.WorkingDirectory = $WorkingDirectory
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.UseShellExecute = $false
  $p = [System.Diagnostics.Process]::Start($psi)
  $stdout = $p.StandardOutput.ReadToEnd()
  $stderr = $p.StandardError.ReadToEnd()
  $p.WaitForExit()
  [pscustomobject]@{
    ExitCode = $p.ExitCode
    Stdout = $stdout
    Stderr = $stderr
    Command = "$FilePath $($Args -join ' ')"
  }
}

$dockerInfo = Run-Cmd -FilePath "docker" -Args @("info", "--format", "{{.ServerVersion}}") -WorkingDirectory $WorkspaceRoot
if ($dockerInfo.ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($dockerInfo.Stdout)) {
  Write-Utf8File -Path (Join-Path $OutRoot "docker-not-ready.txt") -Value $dockerInfo.Stderr
  throw "Docker daemon is not ready. See $OutRoot\docker-not-ready.txt"
}

$summary = @()
$hostPort = $StartHostPort

foreach ($lab in $manifest.labs) {
  $labSource = Join-Path $VulhubRoot $lab.vulhub_path
  $labOut = Join-Path $OutRoot $lab.id
  New-Item -ItemType Directory -Force -Path $labOut | Out-Null

  if (!(Test-Path -LiteralPath $labSource)) {
    Write-Utf8File -Path (Join-Path $labOut "missing.txt") -Value "Missing Vulhub path: $labSource"
    continue
  }

  $composePath = Join-Path $labSource "docker-compose.yml"
  if (!(Test-Path -LiteralPath $composePath)) {
    Write-Utf8File -Path (Join-Path $labOut "missing-compose.txt") -Value "Missing docker-compose.yml: $composePath"
    continue
  }

  $project = "chimera-exp-$($lab.id -replace '[^a-zA-Z0-9]', '-')"
  $up = Run-Cmd -FilePath "docker" -Args @("compose", "-p", $project, "up", "-d") -WorkingDirectory $labSource
  Write-Utf8File -Path (Join-Path $labOut "docker-compose-up.log") -Value ($up.Stdout + "`n" + $up.Stderr)

  Start-Sleep -Seconds 25

  $ps = Run-Cmd -FilePath "docker" -Args @("compose", "-p", $project, "ps", "--format", "json") -WorkingDirectory $labSource
  Write-Utf8File -Path (Join-Path $labOut "docker-compose-ps.jsonl") -Value $ps.Stdout

  $ports = Run-Cmd -FilePath "docker" -Args @("compose", "-p", $project, "port", "--protocol", "tcp", "web", "80") -WorkingDirectory $labSource
  Write-Utf8File -Path (Join-Path $labOut "port-detection.log") -Value ($ports.Stdout + "`n" + $ports.Stderr)

  # Generic local fingerprint path: store scanner commands, and use live_rank_target if a URL is known manually.
  $labMeta = [pscustomobject]@{
    id = $lab.id
    product = $lab.product
    known_cves = $lab.known_cves
    expected_family = $lab.expected_family
    vulhub_path = $lab.vulhub_path
    project = $project
    note = "Review docker-compose-ps.jsonl/port-detection.log to pick local URL, then run live_rank_target.py."
  }
  $labMeta | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $labOut "lab.json") -Encoding utf8

  $summary += $labMeta

  if (!$KeepRunning) {
    $down = Run-Cmd -FilePath "docker" -Args @("compose", "-p", $project, "down", "-v") -WorkingDirectory $labSource
    Write-Utf8File -Path (Join-Path $labOut "docker-compose-down.log") -Value ($down.Stdout + "`n" + $down.Stderr)
  }
}

$summary | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $OutRoot "summary.json") -Encoding utf8
Write-Host "Done. Output: $OutRoot"
