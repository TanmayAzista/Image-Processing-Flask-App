# Requires -Version 7   # Problematic
# --- Simple Multi-Service Flask Runner with -nw Toggle ---

# Define the script parameters
param(
    # Use -nw (No Window) to run all services in the current console (no new CMD windows)
    [switch]$nw
)

# Get the script's directory for reliable path resolution
# $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Define service names and their relative paths
$Services = @{
    "Frontend"        = "Frontend.app"
    "Backend"         = "Backend.app"
    "Inference"       = "Inference.app"
    "Shape Operations"= "ShapeOperations.app"
    "Image Operations"= "ImageOperations.app"
}

# Array to store live state of the service. Stores Process ID, Name and Status
$ServiceStates = @()

# Refined Cleanup Code Runs on shell exit
$script:CleanupCalled = $false
Register-EngineEvent PowerShell.Exiting -Action {
    if (-not $script:CleanupCalled) {
        $script:CleanupCalled = $true
        Stop-Services -Reason "PowerShell Exiting (Ctrl+C / Window Close)"
    }
}

# --- Cleanup Function ---
function Stop-Services {
    param([string]$Reason = "Cleanup")

    
    if ($script:CleanupCalled) { return }
    $script:CleanupCalled = $true
    
    if ($ServiceStates.Count -eq 0) {
        Write-Host "No services to stop." -ForegroundColor Gray
        return
    }

    Write-Host "---"
    Write-Host "$Reason --Stopping services..." -ForegroundColor Red

    # Loop through the stored PIDs and kill the process tree for each
    foreach ($Service in $ServiceStates) {
        Write-Host "Killing Process Tree for $($Service.Name) (PID $($Service.PID))..."
        
        # Using 2>$null to suppress errors if the process is already gone
        taskkill /F /T /PID $Service.PID 2>$null
    }

    Write-Host "Services stopped. Exiting runner script." -ForegroundColor Green
}

# --- Process Status Helper ---
function Get-ServiceStatus {
    param(
        [int]$ProcessId
    )

    $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($null -ne $proc -and -not $proc.HasExited) {
        return $true
    }
    return $false
}

# --- Draw Serice Status Dashboard.
function Draw-ServiceDashboard {
    param(
        [array]$States
    )

    Clear-Host
    Write-Host "Service Status Monitor"
    Write-Host "-----------------------"
    Write-Host ("{0,-20} {1,-10} {2,-10}" -f "Service", "PID", "Status")
    Write-Host ("{0,-20} {1,-10} {2,-10}" -f "-------", "---", "------")


    foreach ($svc in $States) {
        $pidText = if ($null -ne $svc.PID) { $svc.PID } else { "-" }          # Use pidText instead of ?? if PWSH version < 7

        Write-Host ("{0,-20} {1,-10} {2,-10}" -f `
            $svc.Name,
            $pidText,
            $svc.Status
        )
    }

    Write-Host ""
    Write-Host "Press ENTER or Ctrl+C to stop all services"

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
        $FullCommand = "title $Name & python -m Services.$Path"

        Write-Host "Starting $Name service..."
        
    # Start the process, splatting the arguments
        $Process = Start-Process @StartArgs -ArgumentList "/c", $FullCommand
        
        # Store the PID
        $ServiceStates += [PSCustomObject]@{
            Name    = $Name
            PID     = $Process.Id
            Status  = "Starting"
        }
    }

    $startTime = Get-Date
    $startupWindow = 5   # seconds

    while ((Get-Date) - $startTime -lt [TimeSpan]::FromSeconds($startupWindow)) {

        foreach ($svc in $ServiceStates) {
            $proc = Get-Process -Id $svc.PID -ErrorAction SilentlyContinue

            switch ($true) {
                { $null -eq $proc -and $svc.Status -eq "Starting" } { $svc.Status = "Failed"; break }
                { $null -eq $proc }                                 { $svc.Status = "Stopped"; break }
                default                                             { $svc.Status = "Running" }
            }

        }

        Draw-ServiceDashboard -States $ServiceStates
        Start-Sleep -Milliseconds 100
    }

    try {
        while ($true) {
            if ($Host.UI.RawUI.KeyAvailable) {
                $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
                if ($key.VirtualKeyCode -eq 13) {
                    Stop-Services -Reason "User Input (ENTER)"
                    break
                }
            }
            Start-Sleep -Milliseconds 100
        }
    }
    catch [System.Management.Automation.PipelineStoppedException] {
        Stop-Services -Reason "Ctrl+C Interrupt"
        throw
    }
}
# --- Guaranteed Cleanup Block ---
finally {
    Stop-Services -Reason "Script Exit"
}

Write-Host "Exiting runner script."