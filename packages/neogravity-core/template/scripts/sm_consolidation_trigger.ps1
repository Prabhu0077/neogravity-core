# SM Consolidation Trigger — Runs weekly (Sunday 11pm) via Task Scheduler
# Creates a flag file telling NeoGravity to run memory_consolidate() on next boot
# This avoids loading Qwen3:8b (~5.9GB) unless actually needed

$flagFile = "d:\P-Projects\profile-neo\.knowledge\consolidation_due.txt"

# If flag already exists, don't overwrite
if (Test-Path $flagFile) { exit 0 }

"WARM-to-COLD consolidation due. Run memory_consolidate() this session. Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm')" |
Set-Content $flagFile -Encoding UTF8
