# One-time setup on YOUR Windows PC. Hermes is already your primary coding agent.
$ErrorActionPreference = "Stop"
if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
    throw "This setup supports Windows Task Scheduler. No cloud runner is required."
}
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
foreach ($program in @("git", "gh", "cargo", "python", "hermes", "rustup")) {
    if (-not (Get-Command $program -ErrorAction SilentlyContinue)) {
        throw "Missing $program. Install/configure it first on this PC."
    }
}
& gh auth status
if ($LASTEXITCODE -ne 0) {
    throw "GitHub CLI not authenticated. Run gh auth login, then retry."
}
& gh auth setup-git
if ($LASTEXITCODE -ne 0) {
    throw "Git credential helper setup failed."
}
& rustup component add rustfmt clippy
if ($LASTEXITCODE -ne 0) { throw "Rust component installation failed." }
& rustup target add wasm32-unknown-unknown
if ($LASTEXITCODE -ne 0) { throw "WASM target installation failed." }
& hermes --version
if ($LASTEXITCODE -ne 0) {
    throw "Hermes CLI is not usable. Fix Hermes before running automation."
}
Write-Host "Hermes uses your existing model/provider configuration."
Write-Host "To select Xiaomi MiMo, run 'hermes model' (provider: xiaomi)."
Write-Host "Its API key stays in Hermes's existing credentials, not in this repo."
& python -m unittest discover -s (Join-Path $root "tests") -v
if ($LASTEXITCODE -ne 0) {
    throw "Repository tests failed. Local schedule not enabled."
}
Write-Host "Setup checks passed. No scheduled job has been created yet."
Write-Host "Manually run: .\scripts\run-local.ps1"
Write-Host "To enable a recurring local schedule: .\scripts\enable-schedule.ps1"
Write-Host "No upstream PR is ever created automatically."
