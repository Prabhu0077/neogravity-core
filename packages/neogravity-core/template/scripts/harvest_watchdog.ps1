# Harvest Watchdog — Runs every 15 minutes via Task Scheduler
# Checks if Parquet data collection is alive, writes status to JSON
# NeoGravity reads this file at boot instead of running its own PowerShell check

$harvestDir = "d:\P-Projects\neo_swarm_nexus\data\raw_harvest\"
$outputFile = "d:\P-Projects\profile-neo\.knowledge\harvest_health.json"

try {
    if (-not (Test-Path $harvestDir)) {
        $status = "NOT_RUNNING"
        $latestFile = "N/A"
        $ageMinutes = -1
    }
    else {
        $latest = Get-ChildItem $harvestDir -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($null -eq $latest) {
            $status = "NOT_RUNNING"
            $latestFile = "N/A"
            $ageMinutes = -1
        }
        else {
            $age = (Get-Date) - $latest.LastWriteTime
            $ageMinutes = [math]::Round($age.TotalMinutes)
            $latestFile = $latest.Name

            if ($age.TotalMinutes -lt 15) {
                $status = "ACTIVE"
            }
            elseif ($age.TotalMinutes -lt 60) {
                $status = "STALE"
            }
            else {
                $status = "DEAD"
            }
        }
    }

    $report = @{
        status     = $status
        latest     = $latestFile
        age_min    = $ageMinutes
        checked_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    }

    $report | ConvertTo-Json | Set-Content $outputFile -Encoding UTF8
}
catch {
    @{ status = "ERROR"; error = $_.Exception.Message; checked_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss") } |
    ConvertTo-Json | Set-Content $outputFile -Encoding UTF8
}
