# --- Simple Multi-Service Flask Runner with -nw Toggle ---

# Define the script parameters
param(
    # Use -nw (No Window) to run all services in the current console (no new CMD windows)
    [switch]$nw
)

# Get the script's directory for reliable path resolution
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Define service names and their relative paths
$Services = @{
    "Frontend"        = "Frontend\app.py"
    "Backend"         = "Backend\app.py"
    "Inference"       = "Inference\app.py"
    "Shape Operations"= "ShapeOperations\app.py"
    "Image Operations"= "ImageOperations\app.py"
}

# Array to store the process IDs for cleanup (Defined globally so finally can access it)
$ServicePIDs = @()

# --- Cleanup Function ---
function Stop-Services {
    param(
        [string]$Reason = "Cleanup"
    )

    if ($ServicePIDs.Count -eq 0) {
        Write-Host "No services to stop." -ForegroundColor Gray
        return
    }

    Write-Host "---"
    Write-Host "$Reason --Stopping services..." -ForegroundColor Red

    # Loop through the stored PIDs and kill the process tree for each
    foreach ($Service in $ServicePIDs) {
        Write-Host "Killing Process Tree for $($Service.Name) (PID $($Service.PID))..."
        
        # Using 2>$null to suppress errors if the process is already gone
        taskkill /F /T /PID $Service.PID 2>$null
    }
    
    Write-Host "Services stopped. Exiting runner script." -ForegroundColor Green
}


# --- Service Start Logic (Wrapped in Try/Finally) ---
try {
    # --- Dynamic Start-Process Arguments ---
    # Use a Hashtable for splatting to conditionally add -NoNewWindow
    $StartArgs = @{
        FilePath    = "cmd.exe"
        PassThru    = $true
    }

    if ($nw) {
    # If the -nw flag is provided, add the NoNewWindow switch to the arguments
        $StartArgs.NoNewWindow = $true
        Write-Host "Running services in the current PowerShell session..." -ForegroundColor Yellow
    } else {
        Write-Host "Running services in dedicated CMD windows..." -ForegroundColor Cyan
    }

    # --- Start each Service and capture PID ---
    Write-Host "Starting Services..."

    # Loop through the services, start them, and capture their PIDs
    foreach ($Name in $Services.Keys) {
        $Path = $Services[$Name]
    
    # The full command to pass to cmd.exe /c
    # We use double quotes for the python script path to handle spaces
        $FullCommand = "python `"$ScriptDir\$Path`""

        Write-Host "Starting $Name service..."

    # Start the process, splatting the arguments
        $Process = Start-Process @StartArgs -ArgumentList "/c", $FullCommand

        # Store the PID
        $ServicePIDs += [PSCustomObject]@{
            Name = $Name
            PID  = $Process.Id
        }
    }

    Write-Host "---"
    Write-Host "Service Start Complete."

    # Display the PIDs
    foreach ($Service in $ServicePIDs) {
        Write-Host "$($Service.Name) Process ID: $($Service.PID)"
    }

    Write-Host "Access UI at: http://127.0.0.1:5000"
    Write-Host "---"
    Write-Host "NOTE: Press ENTER or Ctrl+C in this PowerShell window to stop all services."

    # Wait for user input (The script will pause here)
    Read-Host "Press ENTER to stop all services."
    
    # If we get here, the user pressed ENTER, so call cleanup
    Stop-Services -Reason "User Input (ENTER)"

} 
# --- Guaranteed Cleanup Block ---
finally {
    # The 'finally' block is executed when the 'try' block exits, 
    # whether by normal completion (already handled above) or by an interrupt (Ctrl+C).
    # We only call Stop-Services here if it wasn't already called by ENTER (which calls exit).
    
    # Check if the script is terminating due to an error/interrupt
    if ($LASTEXITCODE -ne 0 -or $? -eq $false) {
        # This catch-all ensures cleanup runs if the user presses Ctrl+C
        Stop-Services -Reason "Interruption (Ctrl+C/Termination)"
    }
}

Write-Host "Exiting runner script."