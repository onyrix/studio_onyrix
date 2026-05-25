param(
    [string]$InputMidi = "input.mid",
    [string]$OutputDir = "output/generated_variations",
    [int]$MaxNewTokens = 128,
    [string]$Checkpoint = "moonbeam_style_model.pt",
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
    --input $InputMidi `
    --output-dir $OutputDir `
    --max-new-tokens $MaxNewTokens `
    --checkpoint $Checkpoint

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Generated MIDI variations in $OutputDir"
