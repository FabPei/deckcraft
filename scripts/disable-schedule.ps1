# Disable future local runs without deleting code, credentials, or drafts.
$ErrorActionPreference = "Stop"
Unregister-ScheduledTask -TaskName "DeckCraft-Local-Agent" -Confirm:$false
Write-Host "DeckCraft local agent schedule disabled."
