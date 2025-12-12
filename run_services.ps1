# --- Simple Multi-Service Flask Runner (PowerShell - Dedicated Terminals) ---

# Get the script's directory for reliable path resolution
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# All service Commands
$FrontendStart = "python `"$ScriptDir\Frontend\app.py`""
$BackendStart = "python `"$ScriptDir\Backend\app.py`""
$InferenceStart = "python `"$ScriptDir\Inference\app.py`""
$ShapeOpStart = "python `"$ScriptDir\ShapeOperations\app.py`""
$ImageOpStart = "python `"$ScriptDir\ImageOperations\app.py`""


# --- Start each Service in a New Console Window and capture PID ---
Write-Host "Starting Services..."

Write-Host "Starting Frontend..."
$FrontendProcess = Start-Process cmd.exe -ArgumentList "/c $FrontendStart" -PassThru
$Frontend_PID = $FrontendProcess.Id

Write-Host "Starting Backend..."
$BackendProcess = Start-Process cmd.exe -ArgumentList "/c $BackendStart" -PassThru
$Backend_PID = $BackendProcess.Id

Write-Host "Starting Inference..."
$InferenceProcess = Start-Process cmd.exe -ArgumentList "/c $InferenceStart" -PassThru
$Inference_PID = $InferenceProcess.Id

Write-Host "Starting Shape Operations..."
$ShapeOpProcess = Start-Process cmd.exe -ArgumentList "/c $ShapeOpStart" -PassThru
$ShapeOp_PID = $ShapeOpProcess.Id

Write-Host "Starting Image Operations..."
$ImageOpProcess = Start-Process cmd.exe -ArgumentList "/c $ImageOpStart" -PassThru
$ImageOp_PID = $ImageOpProcess.Id


Write-Host "---"
Write-Host "Application Services are running in two new CMD windows."
Write-Host "Frontend Process ID: $Frontend_PID"
Write-Host "Backend Process ID: $Backend_PID"
Write-Host "Inference Process ID: $Inference_PID"
Write-Host "Shape Operation Process ID: $ShapeOp_PID"
Write-Host "Image Operation Process ID: $ImageOp_PID"

Write-Host "Access UI at: http://127.0.0.1:5000"
Write-Host "---"
Write-Host "NOTE: To stop the application, press ENTER in this PowerShell window."

# Wait for user input
Read-Host "Press ENTER to stop both services and close the windows."

# --- Clean up the processes using the captured PIDs ---
Write-Host "Stopping services (PIDs: $Frontend_PID, $Backend_PID, $Inference_PID, $ShapeOp_PID, $ImageOp_PID)..."
# Stop-Process -Id $API_PID -Force -ErrorAction SilentlyContinue
# Stop-Process -Id $UI_PID -Force -ErrorAction SilentlyContinue

Write-Host "Killing API Process Tree (PID $Frontend_PID)..."
taskkill /F /T /PID $Frontend_PID

Write-Host "Killing API Process Tree (PID $Backend_PID)..."
taskkill /F /T /PID $Backend_PID

Write-Host "Killing UI Process Tree (PID $Inference_PID)..."
taskkill /F /T /PID $Inference_PID

Write-Host "Killing UI Process Tree (PID $ShapeOp_PID)..."
taskkill /F /T /PID $ShapeOp_PID

Write-Host "Killing UI Process Tree (PID $ImageOp_PID)..."
taskkill /F /T /PID $ImageOp_PID

Write-Host "Services stopped. Exiting runner script."