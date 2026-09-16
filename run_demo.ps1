# CYCLOPS One-Click Windows Demo Launcher
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "   CYCLOPS: Meteorological AI Decision Workstation   " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

$WorkspaceRoot = $PSScriptRoot
Set-Location $WorkspaceRoot

# 1. Check Python virtual environment
$PythonExe = Join-Path $WorkspaceRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Virtual environment not found at .venv" -ForegroundColor Red
    Write-Host "Please ensure .venv is installed." -ForegroundColor Yellow
    exit 1
}

# 2. Check ports
$Port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$Port5180 = Get-NetTCPConnection -LocalPort 5180 -ErrorAction SilentlyContinue

if ($Port8000) {
    Write-Host "[WARN] Port 8000 is already in use by process PID $($Port8000.OwningProcess)" -ForegroundColor Yellow
}
if ($Port5180) {
    Write-Host "[WARN] Port 5180 is already in use by process PID $($Port5180.OwningProcess)" -ForegroundColor Yellow
}

# 3. Launch Backend API in a dedicated background window
Write-Host "`n1. Launching Backend API (FastAPI on http://127.0.0.1:8000)..." -ForegroundColor Green
$BackendCmd = "cd '$WorkspaceRoot'; `$env:PYTHONPATH='src'; & '$PythonExe' -m uvicorn api.main:app --host 127.0.0.1 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendCmd -WindowStyle Normal

# Wait for backend to be healthy
Write-Host "   Waiting for API to initialize..." -ForegroundColor Gray
$Healthy = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    try {
        $res = Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($res.status -eq "ok") {
            $Healthy = $true
            break
        }
    } catch {}
}

if ($Healthy) {
    Write-Host " [SUCCESS] API Server is healthy and responding!" -ForegroundColor Green
} else {
    Write-Host " [INFO] API starting up, continuing to frontend..." -ForegroundColor Yellow
}

# 4. Launch Frontend Console
Write-Host "`n2. Launching Frontend Console (Vite on http://localhost:5180)..." -ForegroundColor Green
$ConsolePath = Join-Path $WorkspaceRoot "console"
$FrontendCmd = "cd '$ConsolePath'; npm.cmd run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendCmd -WindowStyle Normal

Start-Sleep -Seconds 3

# 5. Open Browser
Write-Host "`n3. Opening Web Workstation in your default browser..." -ForegroundColor Cyan
Start-Process "http://localhost:5180"

Write-Host "`n=====================================================" -ForegroundColor Green
Write-Host ">>> CYCLOPS IS NOW RUNNING! <<<" -ForegroundColor Green
Write-Host "  Console:  http://localhost:5180" -ForegroundColor White
Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "  To stop:  Close the two terminal windows or run .\stop_demo.ps1" -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Green
