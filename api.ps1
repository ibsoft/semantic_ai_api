# Define Variables
$APP_NAME = "run:app"
$SERVER_HOST = "0.0.0.0"  # Renamed variable to avoid conflict with 'Host'
$PORT = "8001"
$PID_FILE = "waitress.pid"

# Usage menu function
function Show-Help {
    Write-Host "Usage: api.ps1 {start|stop|usage}"
    Write-Host "    start       Start Waitress server"
    Write-Host "    stop        Stop Waitress server"
    Write-Host "    usage       Show if Waitress is running"
}

# Function to start Waitress
function Start-Waitress {
    Write-Host "Starting Waitress..."

    # Check if Waitress is already running
    if (Test-Path $PID_FILE) {
        $pid = Get-Content $PID_FILE
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "Waitress is already running with PID $pid."
            return
        }
    }

    # Start Waitress in the background and capture its PID
    Start-Process "python" -ArgumentList "-m", "waitress", "--host=$SERVER_HOST", "--port=$PORT", $APP_NAME -PassThru | Select-Object -ExpandProperty Id | Out-File $PID_FILE

    Write-Host "Waitress started with PID $(Get-Content $PID_FILE)."
}

# Function to stop Waitress
function Stop-Waitress {
    Write-Host "Stopping Waitress..."

    # Check if PID file exists
    if (Test-Path $PID_FILE) {
        $pid = Get-Content $PID_FILE
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            # Force stop the process
            Stop-Process -Id $pid -Force
            Remove-Item $PID_FILE
            Write-Host "Waitress stopped (PID: $pid)."
        } else {
            Write-Host "Waitress with PID $pid is not running."
            Remove-Item $PID_FILE
        }
    } else {
        Write-Host "No PID file found. Waitress may not be running."
    }
}

# Function to show usage/status
function Show-Usage {
    if (Test-Path $PID_FILE) {
        $pid = Get-Content $PID_FILE
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "Waitress is running with PID $pid."
        } else {
            Write-Host "Waitress with PID $pid is not running."
        }
    } else {
        Write-Host "Waitress is not running."
    }
}

# Main logic
if ($args.Count -eq 0) {
    Show-Help
} elseif ($args[0] -eq "start") {
    Start-Waitress
} elseif ($args[0] -eq "stop") {
    Stop-Waitress
} elseif ($args[0] -eq "usage") {
    Show-Usage
} else {
    Show-Help
}