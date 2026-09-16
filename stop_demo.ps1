# CYCLOPS Graceful Stop Script for Windows
Write-Host "Stopping CYCLOPS services..." -ForegroundColor Cyan

# Find and stop uvicorn process on port 8000
$Port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($Port8000) {
    $Pid8000 = $Port8000.OwningProcess | Select-Object -Unique
    Write-Host "Stopping API server (PID $Pid8000)..." -ForegroundColor Yellow
    Stop-Process -Id $Pid8000 -Force -ErrorAction SilentlyContinue
}

# Find and stop node/vite on port 5180
$Port5180 = Get-NetTCPConnection -LocalPort 5180 -ErrorAction SilentlyContinue
if ($Port5180) {
    $Pid5180 = $Port5180.OwningProcess | Select-Object -Unique
    Write-Host "Stopping Console server (PID $Pid5180)..." -ForegroundColor Yellow
    Stop-Process -Id $Pid5180 -Force -ErrorAction SilentlyContinue
}

# Fallback: terminate uvicorn
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn api.main:app*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "All CYCLOPS services stopped cleanly." -ForegroundColor Green
