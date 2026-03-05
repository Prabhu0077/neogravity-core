<#
.SYNOPSIS
    Sovereign Memory - Automated Installation Script
.DESCRIPTION
    Installs the Sovereign Memory MCP backend.
    Instead of a black-box executable, this script creates an isolated Python
    virtual environment (.venv), installs dependencies, and outputs the exact
    MCP configuration needed. Perfect transparency for elite engineers.
#>

$ErrorActionPreference = "Stop"

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host " Installing Sovereign Memory Engine (VibCoder)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

$InstallDir = $PSScriptRoot

# 1. Check Python
$PythonExe = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $PythonExe) {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.10+."
    exit 1
}

# 2. Recreate .venv
Write-Host "`n>> Provisioning isolated Python Virtual Environment..."
if (Test-Path "$InstallDir\.venv") {
    Remove-Item -Path "$InstallDir\.venv" -Recurse -Force
}
& $PythonExe -m venv "$InstallDir\.venv"

# 3. Install Dependencies
Write-Host ">> Installing ML models and dependencies (this may take a minute)..."
$VenvPython = "$InstallDir\.venv\Scripts\python.exe"
& $VenvPython -m pip install -q --upgrade pip
& $VenvPython -m pip install -q -r "$InstallDir\requirements.txt"

# 4. Generate MCP Config
$ConfigSnippet = @"
{
  "mcpServers": {
    "sovereign-memory": {
      "command": "$VenvPython",
      "args": ["$InstallDir\src\mcp\server.py"]
    }
  }
}
"@

Write-Host "`n======================================================" -ForegroundColor Green
Write-Host " Installation Complete! " -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host "`nTo use Sovereign Memory, ensure Neo4j is running:"
Write-Host "  docker-compose -f `"$InstallDir\docker-compose.yml`" up -d"
Write-Host "`nAdd this configuration to your MCP client (Cursor, Claude Desktop):"
Write-Host $ConfigSnippet -ForegroundColor Yellow
Write-Host "`nReady for Autonomous Operation."
