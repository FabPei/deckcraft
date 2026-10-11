param([ValidateRange(0, 1000000)][int]$Issue = 0)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$secretFile = Join-Path $root ".local\secrets\mimo.dpapi"
$settingsFile = Join-Path $root ".local\settings.json"
if (-not (Test-Path $secretFile) -or -not (Test-Path $settingsFile)) {
    throw "Missing local setup. Run scripts/setup-local.ps1 first."
}
$settings = Get-Content $settingsFile -Raw | ConvertFrom-Json
$secure = Get-Content $secretFile -Raw | ConvertTo-SecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$previousKey = $env:MIMO_API_KEY
$previousUrl = $env:MIMO_BASE_URL
$previousModel = $env:MIMO_MODEL
try {
    $env:MIMO_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    $env:MIMO_BASE_URL = [string]$settings.base_url
    $env:MIMO_MODEL = [string]$settings.model
    & python (Join-Path $PSScriptRoot "local_agent.py") run --issue $Issue
    $code = $LASTEXITCODE
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    if ($null -eq $previousKey) { Remove-Item Env:MIMO_API_KEY -ErrorAction SilentlyContinue }
    else { $env:MIMO_API_KEY = $previousKey }
    if ($null -eq $previousUrl) { Remove-Item Env:MIMO_BASE_URL -ErrorAction SilentlyContinue }
    else { $env:MIMO_BASE_URL = $previousUrl }
    if ($null -eq $previousModel) { Remove-Item Env:MIMO_MODEL -ErrorAction SilentlyContinue }
    else { $env:MIMO_MODEL = $previousModel }
}
if ($code -ne 0) { exit $code }
