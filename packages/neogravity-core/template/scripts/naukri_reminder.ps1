# Naukri Reminder — Runs every 3 days via Task Scheduler
# Creates a reminder flag file if Naukri profile hasn't been bumped recently
# NeoGravity reads this file at boot and surfaces reminder to user

$lastBumpFile = "d:\P-Projects\profile-neo\.knowledge\naukri_last_bump.txt"
$reminderFile = "d:\P-Projects\profile-neo\.knowledge\naukri_reminder.txt"

# If reminder already exists, don't overwrite
if (Test-Path $reminderFile) { exit 0 }

if (Test-Path $lastBumpFile) {
    $lastBump = Get-Date (Get-Content $lastBumpFile -Raw).Trim()
    $daysSince = ((Get-Date) - $lastBump).TotalDays

    if ($daysSince -ge 3) {
        "ACTION NEEDED: Naukri profile bump overdue. Last bump: $($lastBump.ToString('yyyy-MM-dd')). Days since: $([math]::Round($daysSince)). Edit resume summary and re-save to trigger 'Active Today' flag." |
        Set-Content $reminderFile -Encoding UTF8
    }
}
else {
    "ACTION NEEDED: Naukri profile bump — no record of last bump. Edit resume summary and re-save to trigger 'Active Today' flag." |
    Set-Content $reminderFile -Encoding UTF8
}
