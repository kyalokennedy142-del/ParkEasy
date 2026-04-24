$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $projectRoot "venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Python virtual environment not found at $python"
    exit 1
}

Set-Location $projectRoot
& $python app.py
