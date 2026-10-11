# Run once on your Windows PC, in PowerShell, with your own user account.
$ErrorActionPreference = "Stop"
if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
    throw "Windows is required for DPAPI and Task Scheduler setup."
}
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$state = Join-Path $root ".local"
New-Item -ItemType Directory -Force -Path $state | Out-Null
foreach ($program in @("git", "gh", "cargo", "npm", "python")) {
    if (-not (Get-Command $program -ErrorAction SilentlyContinue)) {
        throw "Missing $program. Install it before starting setup."
    }
}
if (-not (Get-Command "opencode" -ErrorAction SilentlyContinue)) {
    Write-Host "Installing OpenCode locally with npm..."
    & npm install -g opencode-ai
    if ($LASTEXITCODE -ne 0) { throw "Could not install OpenCode." }
}
& gh auth status
if ($LASTEXITCODE -ne 0) { throw "Run gh auth login first and repeat setup." }
& gh auth setup-git
if ($LASTEXITCODE -ne 0) { throw "Could not configure Git credential helper." }
$secret = Read-Host "MiMo API key (encrypted for this Windows user, not uploaded to GitHub)" -AsSecureString
if (-not $secret -or $secret.Length -lt 10) { throw "Missing API key." }
$secrets = Join-Path $state "secrets"
New-Item -ItemType Directory -Force -Path $secrets | Out-Null
$secret | ConvertFrom-SecureString | Set-Content -Path (Join-Path $secrets "mimo.dpapi") -NoNewline
Write-Host "Pay-as-you-go sk- keys: press Enter. Token Plan tp-/ttp- keys: enter the Token Plan base URL."
$defaultUrl = "https://api.xiaomimimo.com/v1"
$url = Read-Host "Official MiMo base URL [$defaultUrl]"
if ([string]::IsNullOrWhiteSpace($url)) { $url = $defaultUrl }
$uri = $null
if (-not [Uri]::TryCreate($url, [UriKind]::Absolute, [ref]$uri)) {
    throw "Invalid base URL"
}
if ($uri.Scheme -ne "https" -or -not ($uri.Host -eq "xiaomimimo.com" -or $uri.Host.EndsWith(".xiaomimimo.com"))) {
    throw "Only HTTPS Xiaomi MiMo API URLs are allowed"
}
@{base_url=$url; model="mimo-v2.6-flash"} | ConvertTo-Json | Set-Content -Path (Join-Path $state "settings.json") -Encoding UTF8
Write-Host "Running local automation tests..."
& python -m unittest discover -s (Join-Path $root "tests") -v
if ($LASTEXITCODE -ne 0) { throw "Local tests failed. Schedule not activated." }
& (Join-Path $PSScriptRoot "enable-schedule.ps1")
Write-Host "Configured local MiMo automation. Run scripts/run-local.ps1 for an immediate first pass."
Write-Host "All code/test execution is on this PC. PR publication requires explicit manual approval."
