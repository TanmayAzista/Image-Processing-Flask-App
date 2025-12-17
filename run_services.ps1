# Requires -Version 7   
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
    param([array]$States)

    $rawUI = $Host.UI.RawUI
    $rawUI.CursorPosition = @{ X = 0; Y = 0 }

    Write-Host "Service Status Monitor"
    Write-Host "-----------------------"
    Write-Host ("{0,-20} {1,-10} {2,-10}" -f "Service", "PID", "Status")
    Write-Host ("{0,-20} {1,-10} {2,-10}" -f "-------", "---", "------")

    foreach ($svc in $States) {
        $pidText = if ($null -ne $svc.PID) { $svc.PID } else { "-" }

        $color = switch ($svc.Status) {
            "Starting" { "Yellow" }
            "Running " { "Green" }
            "Stopped " { "Red" }
            "Failed  " { "Red" }
            default    { "Gray" }
        }

        Write-Host ("{0,-20} {1,-10} " -f $svc.Name, $pidText) -NoNewline
        Write-Host $svc.Status -ForegroundColor $color
    }

    Write-Host ""
    Write-Host "Press ENTER or Ctrl+C to stop all services"
}

function Update-ServiceStatus {
    param($svc)

    $oldStatus = $svc.Status

    $cmdProc = Get-Process -Id $svc.PID -ErrorAction SilentlyContinue

    if ($null -eq $cmdProc) {
        $svc.Status = if ($svc.Status -eq "Starting") { "Failed  " } else { "Stopped " }
    }
    else {
        $children = Get-CimInstance Win32_Process |
            Where-Object { $_.ParentProcessId -eq $svc.PID -and $_.Name -like "python*" }

        if ($children.Count -eq 0) {
            $svc.Status = "Stopped "
        }
        else {
            $svc.Status = "Running "
        }
    }

    return ($oldStatus -ne $svc.Status)
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

    
    
    Clear-Host
    Draw-ServiceDashboard -States $ServiceStates
    $needsRedraw = $false
    $count = 0

    try { 
        while ($true) {
            $count = $count + 1
            
            foreach ($svc in $ServiceStates) {

                # Update UI only when there is change
                if (Update-ServiceStatus $svc) {
                    $needsRedraw = $true
                }
            }

            if ($needsRedraw) {
                Draw-ServiceDashboard -States $ServiceStates
                $needsRedraw = $false
            }
            Start-Sleep -Milliseconds 250

            if ([Console]::KeyAvailable) {
                $key = [Console]::ReadKey($true)

                if ($key.Key -eq [ConsoleKey]::Enter) {
                    Stop-Services -Reason "User Input (ENTER)"
                    break
                }
            }
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