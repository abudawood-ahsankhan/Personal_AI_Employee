param(
    [string]$Model = "qwen2.5"
)

$ProgressPreference = 'Continue'

function Show-DownloadStatus {
    Clear-Host
    Write-Host ""
    Write-Host " ╔══════════════════════════════════════════════════════════════════════════╗ " -ForegroundColor Cyan
    Write-Host " ║              QWEN 2.5 DOWNLOAD - LIVE MONITOR                            ║ " -ForegroundColor Cyan
    Write-Host " ╚══════════════════════════════════════════════════════════════════════════╝ " -ForegroundColor Cyan
    Write-Host ""
    
    # Get models list
    Write-Host " 📦 DOWNLOADED MODELS:" -ForegroundColor Green
    Write-Host " ────────────────────────────────────────────────────────────────────────────"
    $models = ollama list 2>&1 | Out-String
    Write-Host "  $models"
    
    # Get active processes
    Write-Host " 🔄 ACTIVE PROCESSES:" -ForegroundColor Yellow
    Write-Host " ────────────────────────────────────────────────────────────────────────────"
    $processes = ollama ps 2>&1 | Out-String
    Write-Host "  $processes"
    
    # Get server status
    Write-Host " 🖥️  OLLAMA SERVER:" -ForegroundColor Blue
    Write-Host " ────────────────────────────────────────────────────────────────────────────"
    $version = curl.exe -s http://localhost:11434/api/version 2>$null
    Write-Host "  $version"
    Write-Host ""
    
    # Progress info
    Write-Host " ════════════════════════════════════════════════════════════════════════════ " -ForegroundColor Cyan
    Write-Host "  Updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
    Write-Host "  Auto-refresh every 3 seconds. Press Ctrl+C to exit." -ForegroundColor Gray
    Write-Host " ════════════════════════════════════════════════════════════════════════════ " -ForegroundColor Cyan
}

# Main loop
while ($true) {
    try {
        Show-DownloadStatus
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
    }
    Start-Sleep -Seconds 3
}
