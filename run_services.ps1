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

# Array to store the process IDs for cleanup
$ServicePIDs = @()

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
Write-Host "NOTE: To stop the application, press ENTER in this PowerShell window."

# Wait for user input
Read-Host "Press ENTER to stop all services."

# --- Clean up the processes using the captured PIDs ---
Write-Host "Stopping services..."

# Loop through the stored PIDs and kill the process tree for each
foreach ($Service in $ServicePIDs) {
    Write-Host "Killing Process Tree for $($Service.Name) (PID $($Service.PID))..."
    # Using taskkill /F /T to forcefully terminate the process and its children
    taskkill /F /T /PID $Service.PID
}

Write-Host "Services stopped. Exiting runner script."