param(
    [string]$OutputDir = "output/generated_songs",
    [int]$Bars = 32,
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"

if (-not $Python) {
    $VenvPython = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
    if (Test-Path $VenvPython) {
        $Python = $VenvPython
    }
    else {
        $Python = "python"
    }
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

& $Python -m generation.batch `
    --output-dir $OutputDir `
    --bars $Bars

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Generated MIDI songs in $OutputDir"
