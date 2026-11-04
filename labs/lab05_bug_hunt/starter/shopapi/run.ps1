# Start ShopAPI on http://localhost:8000 (Windows PowerShell).
# Resets the demo data every time you start it.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv run python seed.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "ShopAPI: http://localhost:8000/docs   (stop with Ctrl+C)"
    uv run python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
} else {
    python seed.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "ShopAPI: http://localhost:8000/docs   (stop with Ctrl+C)"
    python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
}
