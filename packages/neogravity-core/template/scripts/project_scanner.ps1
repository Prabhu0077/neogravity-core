# Project Scanner — Runs every hour via Task Scheduler
# Scans the projects root directory for new project directories
# Detects projects by presence of markers (.git, package.json, pyproject.toml, Cargo.toml, etc.)
# When a new project is found, writes a discovery flag for NeoGravity to process at boot

$registryFile = "d:\P-Projects\profile-neo\projects.json"
$discoveryFlag = "d:\P-Projects\profile-neo\.knowledge\new_project_detected.json"

# If discovery flag already exists, don't overwrite — wait for NeoGravity to process it
if (Test-Path $discoveryFlag) { exit 0 }

# Read current registry
$registry = Get-Content $registryFile -Raw | ConvertFrom-Json
$scanRoot = $registry.scan_root
$knownPaths = @()
foreach ($proj in $registry.projects.PSObject.Properties) {
    $knownPaths += $proj.Value.path
}

# Scan for project directories (depth 1-2)
$markers = @(".git", "package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "*.sln")
$discovered = @()

Get-ChildItem $scanRoot -Directory -Depth 1 | ForEach-Object {
    $dir = $_.FullName
    # Skip if already registered
    if ($knownPaths -contains $dir) { return }
    # Skip profile-neo subfolders (they're sub-projects, not root projects)
    if ($dir -like "*profile-neo*") { return }

    # Check for project markers
    foreach ($marker in $markers) {
        if (Test-Path (Join-Path $dir $marker)) {
            $discovered += @{
                name        = $_.Name.ToLower() -replace '[^a-z0-9-]', '-'
                path        = $dir
                marker      = $marker
                detected_at = (Get-Date -Format "yyyy-MM-dd HH:mm")
            }
            break
        }
    }
}

# Write discovery flag if new projects found
if ($discovered.Count -gt 0) {
    @{
        new_projects = $discovered
        scanned_at   = (Get-Date -Format "yyyy-MM-dd HH:mm")
    } | ConvertTo-Json -Depth 3 | Set-Content $discoveryFlag -Encoding UTF8
}
