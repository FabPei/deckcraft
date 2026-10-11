param([ValidateRange(0, 1000000)][int]$Issue = 0)
$ErrorActionPreference = "Stop"
# Uses the existing local Hermes installation and its already-configured model.
# No GitHub Action, API-key copy, token transfer or OpenCode installation.
& python (Join-Path $PSScriptRoot "local_agent.py") run --issue $Issue
exit $LASTEXITCODE
