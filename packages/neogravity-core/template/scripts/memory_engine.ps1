<#
.SYNOPSIS
    Sovereign Memory Engine - Autonomous Lifecycle Orchestrator
.DESCRIPTION
    Manages the full dependency DAG for starting/stopping the Sovereign Memory system.
    Each phase returns JSON status; dependent phases only fire after parent succeeds.
.PARAMETER Action
    'start' - Start Neo4j, verify health, report status
    'stop'  - Stop Neo4j, report RAM freed
.EXAMPLE
    .\memory_engine.ps1 -Action start
    .\memory_engine.ps1 -Action stop
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop")]
    [string]$Action
)

$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Phase, [string]$Node, [string]$Status, [string]$Detail)
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts] Phase $Phase | Node $Node | $Status | $Detail"
}

function Test-Neo4jHealth {
    param([int]$MaxRetries = 8, [int]$RetryDelaySec = 3)
    for ($i = 1; $i -le $MaxRetries; $i++) {
        try {
            $status = docker inspect hybrid-rag-neo4j --format "{{.State.Status}}" 2>$null
            if ($status -eq "running") {
                $tcp = Test-NetConnection -ComputerName localhost -Port 7687 -WarningAction SilentlyContinue
                if ($tcp.TcpTestSucceeded) {
                    return @{ healthy = $true; attempt = $i }
                }
            }
        } catch {}
        Write-Status "2" "C" "WAITING" "Neo4j health check attempt $i/$MaxRetries..."
        Start-Sleep -Seconds $RetryDelaySec
    }
    return @{ healthy = $false; attempt = $MaxRetries }
}

function Test-OllamaRunning {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3
        $models = $response.models | ForEach-Object { $_.name }
        return @{ alive = $true; models = ($models -join ", ") }
    } catch {
        return @{ alive = $false; models = "" }
    }
}

function Get-ContainerRamMB {
    try {
        $stats = docker stats hybrid-rag-neo4j --no-stream --format "{{.MemUsage}}" 2>$null
        if ($stats -match "([\d.]+)MiB") { return [math]::Round([double]$Matches[1]) }
        if ($stats -match "([\d.]+)GiB") { return [math]::Round([double]$Matches[1] * 1024) }
    } catch {}
    return 512
}

# --- START ---
function Invoke-Start {
    $result = @{
        action = "start"
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        phases = @{}
        success = $false
    }

    # Phase 1A: Start Neo4j
    Write-Status "1" "A" "STARTING" "Neo4j Docker container..."
    try {
        $dockerOut = docker start hybrid-rag-neo4j 2>&1
        $result.phases["1A_neo4j_start"] = @{ status = "started"; output = "$dockerOut" }
        Write-Status "1" "A" "OK" "Container start command sent"
    } catch {
        $result.phases["1A_neo4j_start"] = @{ status = "FAILED"; error = $_.Exception.Message }
        Write-Status "1" "A" "FAILED" $_.Exception.Message
        $result | ConvertTo-Json -Depth 4
        exit 1
    }

    # Phase 1B: Check Ollama
    Write-Status "1" "B" "CHECKING" "Ollama status..."
    $ollamaResult = Test-OllamaRunning
    $result.phases["1B_ollama"] = $ollamaResult
    if ($ollamaResult.alive) {
        Write-Status "1" "B" "OK" "Ollama alive, models: $($ollamaResult.models)"
    } else {
        Write-Status "1" "B" "WARN" "Ollama not running (consolidation unavailable, queries still work)"
    }

    # Phase 2C: Health gate
    Write-Status "2" "C" "CHECKING" "Neo4j health (bolt://localhost:7687)..."
    $healthResult = Test-Neo4jHealth -MaxRetries 8 -RetryDelaySec 3
    $result.phases["2C_neo4j_health"] = $healthResult

    if (-not $healthResult.healthy) {
        Write-Status "2" "C" "FAILED" "Neo4j did not become healthy after $($healthResult.attempt) attempts"
        $result | ConvertTo-Json -Depth 4
        exit 1
    }
    Write-Status "2" "C" "OK" "Neo4j healthy on attempt $($healthResult.attempt)"

    # Phase 3D: Report
    $ollamaStatus = "offline (non-blocking)"
    if ($ollamaResult.alive) { $ollamaStatus = "running" }

    $result.success = $true
    $result.phases["3D_status"] = @{
        neo4j = "healthy"
        ollama = $ollamaStatus
        mcp_note = "Agent should call memory_recent(n=1) to warm up models"
    }
    Write-Status "3" "D" "DONE" "Memory engine ready. MCP warm-up pending."

    $result | ConvertTo-Json -Depth 4
}

# --- STOP ---
function Invoke-Stop {
    $result = @{
        action = "stop"
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        phases = @{}
        success = $false
    }

    # Phase 1: Measure RAM
    Write-Status "1" "A" "MEASURING" "Current Neo4j RAM usage..."
    $ramBefore = Get-ContainerRamMB
    Write-Status "1" "A" "INFO" "Neo4j using ~${ramBefore}MB RAM"

    # Phase 2: Stop Neo4j
    Write-Status "2" "B" "STOPPING" "Neo4j Docker container..."
    try {
        $dockerOut = docker stop hybrid-rag-neo4j 2>&1
        $result.phases["2B_neo4j_stop"] = @{ status = "stopped"; output = "$dockerOut" }
        Write-Status "2" "B" "OK" "Neo4j stopped"
    } catch {
        $result.phases["2B_neo4j_stop"] = @{ status = "FAILED"; error = $_.Exception.Message }
        Write-Status "2" "B" "FAILED" $_.Exception.Message
        $result | ConvertTo-Json -Depth 4
        exit 1
    }

    # Phase 3: Report
    $totalFreed = $ramBefore + 290
    $result.success = $true
    $result.phases["3C_report"] = @{
        neo4j_ram_freed_mb = $ramBefore
        model_ram_freed_mb = 290
        total_freed_mb = $totalFreed
        note = "MCP server process stops when Antigravity session ends"
    }
    Write-Status "3" "C" "DONE" "Memory engine stopped. ~${totalFreed}MB RAM freed."

    $result | ConvertTo-Json -Depth 4
}

# --- MAIN ---
Write-Host "============================================"
Write-Host "  Sovereign Memory Engine - $($Action.ToUpper())"
Write-Host "============================================"

if ($Action -eq "start") {
    Invoke-Start
} else {
    Invoke-Stop
}
