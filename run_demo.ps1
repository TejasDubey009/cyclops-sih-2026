<#
.SYNOPSIS
    Starts the full CYCLOPS Operational Stack (FastAPI backend + Vite frontend console) on Windows PowerShell.
#>
param(
    [int]$ApiPort = 8000,
    [int]$ConsolePort = 5180
)

$ErrorActionPreference = "Stop"
$WorkspaceRoot = $PSScriptRoot

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "               CYCLOPS OPERATIONAL STACK                " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Check Python Virtual Environment
$PythonExe = Join-Path $WorkspaceRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Error "Virtual environment not found at $PythonExe. Run setup first."
}

# 2. Check Node & npm
$NpmCmd = "C:\Program Files\nodejs\npm.cmd"
if (-not (Test-Path $NpmCmd)) {
    $NpmCmd = (Get-Command npm.cmd -ErrorAction SilentlyContinue).Source
    if (-not $NpmCmd) {
        Write-Error "npm.cmd not found. Ensure Node.js is installed."
    }
}

# 3. Check for Port Conflicts
$ApiInUse = Get-NetTCPConnection -LocalPort $ApiPort -ErrorAction SilentlyContinue
if ($ApiInUse) {
    Write-Host "[INFO] Port $ApiPort is already active (Process ID: $($ApiInUse.OwningProcess)). Reusing existing backend." -ForegroundColor Yellow
} else {
    Write-Host "[1/2] Starting CYCLOPS FastAPI backend on port $ApiPort..." -ForegroundColor Green
    $env:PYTHONPATH = "src"
    $ApiProcess = Start-Process -FilePath $PythonExe `
        -ArgumentList "-m uvicorn api.main:app --host 127.0.0.1 --port $ApiPort" `
        -WorkingDirectory $WorkspaceRoot `
        -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# 4. Check Frontend Console
$ConsoleInUse = Get-NetTCPConnection -LocalPort $ConsolePort -ErrorAction SilentlyContinue
if ($ConsoleInUse) {
    Write-Host "[INFO] Port $ConsolePort is already active (Process ID: $($ConsoleInUse.OwningProcess)). Reusing existing console." -ForegroundColor Yellow
} else {
    Write-Host "[2/2] Starting CYCLOPS Vite console on port $ConsolePort..." -ForegroundColor Green
    $ConsoleProcess = Start-Process -FilePath $NpmCmd `
        -ArgumentList "run dev" `
        -WorkingDirectory (Join-Path $WorkspaceRoot "console") `
        -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# 5. Verify Health
Write-Host "`nVerifying stack health..." -ForegroundColor Cyan
try {
    $Health = Invoke-RestMethod -Uri "http://127.0.0.1:$ApiPort/v1/health" -TimeoutSec 5
    Write-Host "[SUCCESS] API Backend: Healthy (status = $($Health.status))" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] API did not reply immediately, but process was launched." -ForegroundColor Yellow
}

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host " CYCLOPS Console:  http://127.0.0.1:$ConsolePort" -ForegroundColor Green
Write-Host " API Docs:         http://127.0.0.1:$ApiPort/docs" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

# Open default browser
Start-Process "http://127.0.0.1:$ConsolePort"
