param([Parameter(Mandatory = $true)][ValidateRange(1, 1000000)][int]$Issue)
$ErrorActionPreference = "Stop"
Write-Host "This command may CREATE A PUBLIC upstream PR after your explicit typed confirmation."
& python (Join-Path $PSScriptRoot "local_agent.py") publish --issue $Issue
exit $LASTEXITCODE
