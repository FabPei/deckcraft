# Windows Task Scheduler; only this signed-in Windows user runs local agents.
$ErrorActionPreference = "Stop"
$name = "DeckCraft-Local-Agent"
$script = (Resolve-Path (Join-Path $PSScriptRoot "run-local.ps1")).Path
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument ('-NoProfile -ExecutionPolicy Bypass -File "' + $script + '"')
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Wednesday,Friday -At 19:00
$principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 6)
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Write-Host "Local schedule active: Mon/Wed/Fri 19:00, while signed in to Windows."
