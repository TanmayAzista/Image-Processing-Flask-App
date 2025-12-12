# --- Simple Multi-Service Flask Runner (PowerShell - Dedicated Terminals) ---

# Get the script's directory for reliable path resolution
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Define service names and their relative paths
# The key is the service name (for display), and the value is the path to its script.
$Services = @{
    "Frontend"        = "Frontend\app.py"
    "Backend"         = "Backend\app.py"
    "Inference"       = "Inference\app.py"
    "Shape Operations"= "ShapeOperations\app.py"
    "Image Operations"= "ImageOperations\app.py"
}

# Array to store the process IDs for cleanup
$ServicePIDs = @()

# --- Start each Service in a New Console Window and capture PID ---
Write-Host "Starting Services..."

# Loop through the services, start them, and capture their PIDs
foreach ($Name in $Services.Keys) {
    $Path = $Services[$Name]
    $FullCommand = "python `"$ScriptDir\$Path`""

    Write-Host "Starting $Name service..."

    # Start the process and capture the object
    $Process = Start-Process cmd.exe -ArgumentList "/c $FullCommand" -PassThru

    # Store the PID in our array
    $ServicePIDs += [PSCustomObject]@{
        Name = $Name
        PID  = $Process.Id
    }
}

Write-Host "---"
Write-Host "Application Services are running in dedicated CMD windows."

# Display the PIDs
foreach ($Service in $ServicePIDs) {
    Write-Host "$($Service.Name) Process ID: $($Service.PID)"
}

Write-Host "Access UI at: http://127.0.0.1:5000"
Write-Host "---"
Write-Host "NOTE: To stop the application, press ENTER in this PowerShell window."

# Wait for user input
Read-Host "Press ENTER to stop all services and close the windows."

# --- Clean up the processes using the captured PIDs ---
Write-Host "Stopping services..."

# Loop through the stored PIDs and kill the process tree for each
foreach ($Service in $ServicePIDs) {
    Write-Host "Killing Process Tree for $($Service.Name) (PID $($Service.PID))..."
    # Using taskkill /F /T to forcefully terminate the process and its children (the python process)
    taskkill /F /T /PID $Service.PID
}

Write-Host "Services stopped. Exiting runner script."