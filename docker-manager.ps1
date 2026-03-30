#!/usr/bin/env pwsh
# MQTT Docker Manager

# Colors
$GREEN = "Green"
$YELLOW = "Yellow"
$RED = "Red"
$CYAN = "Cyan"

function Start-MQTT {
    Write-Host "Starting MQTT broker..." -ForegroundColor $GREEN
    Push-Location broker
    docker compose up -d
    Write-Host "MQTT broker started!" -ForegroundColor $GREEN
    docker compose ps
    Pop-Location
}

function Stop-MQTT {
    Write-Host "Stopping MQTT broker..." -ForegroundColor $YELLOW
    Push-Location broker
    docker compose down
    Write-Host "MQTT broker stopped!" -ForegroundColor $GREEN
    Pop-Location
}

function Restart-MQTT {
    Write-Host "Restarting MQTT broker..." -ForegroundColor $YELLOW
    Push-Location broker
    docker compose restart
    Write-Host "MQTT broker restarted!" -ForegroundColor $GREEN
    docker compose ps
    Pop-Location
}

function Show-Logs {
    Write-Host "MQTT Broker Logs (Ctrl+C to exit):" -ForegroundColor $CYAN
    Push-Location broker
    docker compose logs --follow mqtt-broker
    Pop-Location
}

function Check-Health {
    Write-Host "Checking broker health..." -ForegroundColor $CYAN
    Push-Location broker
    $status = docker compose ps
    Write-Host $status
    Pop-Location
}

function Clean-All {
    Write-Host "WARNING: This will delete all broker data!" -ForegroundColor $RED
    $confirm = Read-Host "Are you sure? (y/n)"
    if ($confirm -eq 'y') {
        Push-Location broker
        docker compose down -v
        Write-Host "All data removed!" -ForegroundColor $GREEN
        Pop-Location
    }
}

function Open-Web-Client {
    Write-Host "Opening Web Client..." -ForegroundColor $CYAN
    $webClientPath = Join-Path $PSScriptRoot "web-client.html"
    if (Test-Path $webClientPath) {
        Start-Process $webClientPath
        Write-Host "Web Client opened in browser!" -ForegroundColor $GREEN
    } else {
        Write-Host "File web-client.html not found!" -ForegroundColor $RED
    }
}

function Show-Menu {
    $host.UI.RawUI.WindowTitle = "MQTT Docker Manager - pz-MQTT"
    Write-Host "`n=========================================" -ForegroundColor $CYAN
    Write-Host "  MQTT Docker Manager - pz-MQTT" -ForegroundColor $CYAN
    Write-Host "=========================================" -ForegroundColor $CYAN
    Write-Host ""
    Write-Host "Select operation:" -ForegroundColor $YELLOW
    Write-Host "1. Start MQTT broker" -ForegroundColor $GREEN
    Write-Host "2. Stop MQTT broker" -ForegroundColor $YELLOW
    Write-Host "3. Restart MQTT broker" -ForegroundColor $CYAN
    Write-Host "4. View logs" -ForegroundColor $CYAN
    Write-Host "5. Check health" -ForegroundColor $CYAN
    Write-Host "6. Clean all data" -ForegroundColor $RED
    Write-Host "7. Postman info" -ForegroundColor $GREEN
    Write-Host "8. 🌐 Open Web Client" -ForegroundColor $CYAN
    Write-Host "9. Exit" -ForegroundColor $RED
    Write-Host ""
    
    $choice = Read-Host "Your choice (1-9)"
    
    switch ($choice) {
        "1" { Start-MQTT }
        "2" { Stop-MQTT }
        "3" { Restart-MQTT }
        "4" { Show-Logs }
        "5" { Check-Health }
        "6" { Clean-All }
        "7" { 
            Write-Host ""
            Write-Host "Testing with Postman:" -ForegroundColor $GREEN
            Write-Host "1. Install Postman from https://www.postman.com/downloads/" -ForegroundColor $YELLOW
            Write-Host "2. Import Postman_MQTT_Collection.json" -ForegroundColor $YELLOW
            Write-Host "3. Connect to WebSocket: ws://localhost:9090" -ForegroundColor $CYAN
            Write-Host "4. Send MQTT messages" -ForegroundColor $YELLOW
            Write-Host ""
        }
        "8" { Open-Web-Client }
        "9" { 
            Write-Host "Goodbye!" -ForegroundColor $GREEN
            exit 0
        }
        default { Write-Host "Invalid choice!" -ForegroundColor $RED }
    }
    
    Read-Host "Press Enter to continue..."
    Clear-Host
    Show-Menu
}

# Main
if ($args.Count -gt 0) {
    $cmd = $args[0]
    switch ($cmd) {
        "start" { Start-MQTT }
        "stop" { Stop-MQTT }
        "restart" { Restart-MQTT }
        "logs" { Show-Logs }
        "health" { Check-Health }
        "clean" { Clean-All }
        default { Write-Host "Unknown command: $cmd" }
    }
} else {
    Show-Menu
}
