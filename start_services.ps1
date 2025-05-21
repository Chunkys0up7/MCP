# Function to write colored log messages
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

# Function to check if a service is running
function Test-ServiceRunning {
    param(
        [string]$Url,
        [int]$MaxRetries = 30,
        [int]$RetryInterval = 2
    )
    
    $retries = 0
    while ($retries -lt $MaxRetries) {
        try {
            $response = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                return $true
            }
        }
        catch {
            Write-Log "Waiting for service at $Url to start... (Attempt $($retries + 1)/$MaxRetries)" "WARN"
            Start-Sleep -Seconds $RetryInterval
            $retries++
        }
    }
    return $false
}

# Function to start a service and capture its output
function Start-ServiceWithLogging {
    param(
        [string]$Command,
        [string]$ServiceName,
        [string]$WorkingDirectory = $null
    )
    
    try {
        Write-Log "Starting $ServiceName..."
        $startInfo = New-Object System.Diagnostics.ProcessStartInfo
        $startInfo.FileName = "powershell.exe"
        $startInfo.Arguments = "-NoProfile -Command `"$Command`""
        $startInfo.UseShellExecute = $false
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
        $startInfo.CreateNoWindow = $true
        
        if ($WorkingDirectory) {
            $startInfo.WorkingDirectory = $WorkingDirectory
        }
        
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $startInfo
        $process.Start() | Out-Null
        
        Write-Log "$ServiceName started with PID: $($process.Id)" "SUCCESS"
        return $process
    }
    catch {
        Write-Log ('Failed to start ' + $ServiceName + ': ' + $_) 'ERROR'
        return $null
    }
}

# Function to check if a directory exists
function Check-DirectoryExists {
    param([string]$Path)
    if (-not (Test-Path $Path -PathType Container)) {
        Write-Log "Directory not found: $Path" "ERROR"
        exit 1
    }
}

# Main execution
try {
    Write-Log "Starting MCP services..."

    # Check frontend directory exists
    Check-DirectoryExists "frontend"

    # Start FastAPI backend
    $backendProcess = Start-ServiceWithLogging "uvicorn mcp.api.main:app --reload --port 8000" "FastAPI Backend"
    if (-not $backendProcess) {
        throw "Failed to start FastAPI backend"
    }

    # Wait for backend to be ready
    Write-Log "Waiting for FastAPI backend to be ready..."
    if (-not (Test-ServiceRunning "http://localhost:8000/health")) {
        throw "FastAPI backend failed to start within timeout period"
    }
    Write-Log "FastAPI backend is ready" "SUCCESS"

    # Start Streamlit frontend
    $streamlitProcess = Start-ServiceWithLogging "streamlit run mcp/ui/app.py" "Streamlit Frontend"
    if (-not $streamlitProcess) {
        throw "Failed to start Streamlit frontend"
    }

    # Start React frontend
    $reactProcess = Start-ServiceWithLogging "npm run dev" "React Frontend" "frontend"
    if (-not $reactProcess) {
        throw "Failed to start React frontend"
    }

    Write-Log "All services started successfully!" "SUCCESS"
    Write-Log "Services are running at:" "INFO"
    Write-Log "- FastAPI Backend: http://localhost:8000" "INFO"
    Write-Log "- Streamlit UI: http://localhost:8501" "INFO"
    Write-Log "- React Frontend: http://localhost:5173" "INFO"

    # Keep the script running and monitor processes
    $restartAttempts = 0
    $maxRestarts = 2
    while ($true) {
        if (-not $backendProcess.HasExited -and -not $streamlitProcess.HasExited -and -not $reactProcess.HasExited) {
            Start-Sleep -Seconds 5
        }
        else {
            Write-Log "One or more services have stopped unexpectedly" "ERROR"
            if ($backendProcess.HasExited) { Write-Log "FastAPI Backend stopped" "ERROR" }
            if ($streamlitProcess.HasExited) { Write-Log "Streamlit Frontend stopped" "ERROR" }
            if ($reactProcess.HasExited) { Write-Log "React Frontend stopped" "ERROR" }
            if ($restartAttempts -lt $maxRestarts) {
                Write-Log ("Attempting to restart all services (attempt $($($restartAttempts + 1))/$($maxRestarts))...") "WARN"
                $restartAttempts++
                # Clean up
                if ($backendProcess -and -not $backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id -Force }
                if ($streamlitProcess -and -not $streamlitProcess.HasExited) { Stop-Process -Id $streamlitProcess.Id -Force }
                if ($reactProcess -and -not $reactProcess.HasExited) { Stop-Process -Id $reactProcess.Id -Force }
                Start-Sleep -Seconds 2
                # Restart
                $backendProcess = Start-ServiceWithLogging "uvicorn mcp.api.main:app --reload --port 8000" "FastAPI Backend"
                if (-not $backendProcess) { throw "Failed to restart FastAPI backend" }
                if (-not (Test-ServiceRunning "http://localhost:8000/health")) { throw "FastAPI backend failed to restart" }
                $streamlitProcess = Start-ServiceWithLogging "streamlit run mcp/ui/app.py" "Streamlit Frontend"
                if (-not $streamlitProcess) { throw "Failed to restart Streamlit frontend" }
                $reactProcess = Start-ServiceWithLogging "npm run dev" "React Frontend" "frontend"
                if (-not $reactProcess) { throw "Failed to restart React frontend" }
                Write-Log "All services restarted successfully!" "SUCCESS"
            } else {
                Write-Log "Max restart attempts reached. Exiting." "ERROR"
                break
            }
        }
    }
}
catch {
    Write-Log "Error during service startup: $_" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    # Attempt to clean up any running processes
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force
    }
    if ($streamlitProcess -and -not $streamlitProcess.HasExited) {
        Stop-Process -Id $streamlitProcess.Id -Force
    }
    if ($reactProcess -and -not $reactProcess.HasExited) {
        Stop-Process -Id $reactProcess.Id -Force
    }
    exit 1
} 