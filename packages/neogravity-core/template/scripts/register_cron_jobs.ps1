# NeoGravity Cron Registration Script
# Run this ONCE with admin privileges to register all scheduled tasks
# These tasks run PowerShell scripts that write flag/status files
# NeoGravity reads these files at boot — zero LLM inference for repetitive checks

$scriptsDir = "d:\P-Projects\profile-neo\scripts"

Write-Host "Registering NeoGravity scheduled tasks..." -ForegroundColor Cyan

# 1. Harvest Watchdog — every 15 minutes
schtasks /Create /SC MINUTE /MO 15 `
    /TN "NeoGravity\HarvestWatchdog" `
    /TR "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File $scriptsDir\harvest_watchdog.ps1" `
    /F
Write-Host "  [+] HarvestWatchdog — every 15 min" -ForegroundColor Green

# 2. Naukri Reminder — every 3 days
schtasks /Create /SC DAILY /MO 3 `
    /TN "NeoGravity\NaukriReminder" `
    /TR "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File $scriptsDir\naukri_reminder.ps1" `
    /F
Write-Host "  [+] NaukriReminder — every 3 days" -ForegroundColor Green

# 3. SM Consolidation Trigger — weekly Sunday 11pm
schtasks /Create /SC WEEKLY /D SUN /ST 23:00 `
    /TN "NeoGravity\SMConsolidation" `
    /TR "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File $scriptsDir\sm_consolidation_trigger.ps1" `
    /F
Write-Host "  [+] SMConsolidation — weekly Sunday 11pm" -ForegroundColor Green

# 4. Project Scanner — every hour
schtasks /Create /SC HOURLY /MO 1 `
    /TN "NeoGravity\ProjectScanner" `
    /TR "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File $scriptsDir\project_scanner.ps1" `
    /F
Write-Host "  [+] ProjectScanner — every hour" -ForegroundColor Green

Write-Host ""
Write-Host "All tasks registered under NeoGravity\ folder in Task Scheduler." -ForegroundColor Cyan
Write-Host "To verify: schtasks /Query /TN \NeoGravity\" -ForegroundColor DarkGray
Write-Host "To remove all: schtasks /Delete /TN \NeoGravity\ /F" -ForegroundColor DarkGray
