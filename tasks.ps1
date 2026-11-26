# Windows equivalent of the Makefile. Usage: .\tasks.ps1 <target>
param(
    [Parameter(Position = 0)]
    [ValidateSet("setup", "dev", "run", "migrate", "test", "test-infer", "lint", "fetch-models", "bench")]
    [string]$Target = "test"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$Py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

function Invoke-Step {
    param([string]$Exe, [string[]]$Arguments)
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

switch ($Target) {
    "setup" {
        Invoke-Step "py" @("-3.10", "-m", "venv", ".venv")
        Invoke-Step $Py @("-m", "pip", "install", "-U", "pip")
        Invoke-Step $Py @("-m", "pip", "install", "-e", ".[dev]")
    }
    "dev" { Invoke-Step $Py @("-m", "uvicorn", "app.main:create_app", "--factory", "--reload", "--host", "127.0.0.1", "--port", "8000") }
    "run" { Invoke-Step $Py @("-m", "app.main") }
    "migrate" { Invoke-Step $Py @("-m", "alembic", "upgrade", "head") }
    "test" { Invoke-Step $Py @("-m", "pytest") }
    "test-infer" { Invoke-Step $Py @("-m", "pytest", "-m", "inference") }
    "lint" {
        Invoke-Step $Py @("-m", "ruff", "check", ".")
        Invoke-Step $Py @("-m", "ruff", "format", "--check", ".")
        Invoke-Step $Py @("-m", "mypy")
    }
    "fetch-models" { Write-Host "fetch-models: implemented in M1" }
    "bench" { Invoke-Step $Py @("scripts/benchmark_models.py") }
}
