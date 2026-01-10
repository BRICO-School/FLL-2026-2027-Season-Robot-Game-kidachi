# FLL Robot Game - Code Formatter (Windows PowerShell)
# Usage: .\tools\format.ps1

$ErrorActionPreference = "Stop"

$ROOT_DIR = Split-Path -Parent $PSScriptRoot
$TARGETS = @(
    "$ROOT_DIR\runs",
    "$ROOT_DIR\selector.py",
    "$ROOT_DIR\setup.py",
    "$ROOT_DIR\utils"
)

# Check if ruff is installed
try {
    Get-Command ruff -ErrorAction Stop | Out-Null
} catch {
    Write-Error "ruff not found. Please run 'pip install -r requirements.txt'"
    exit 1
}

# Check if black is installed
try {
    Get-Command black -ErrorAction Stop | Out-Null
} catch {
    Write-Error "black not found. Please run 'pip install -r requirements.txt'"
    exit 1
}

Write-Host "== Ruff (lint + auto-fix) ==" -ForegroundColor Cyan
ruff check $TARGETS --fix

Write-Host "`n== Ruff (format) ==" -ForegroundColor Cyan
ruff format $TARGETS

Write-Host "`n== Black (format) ==" -ForegroundColor Cyan
black $TARGETS

Write-Host "`nCompleted successfully!" -ForegroundColor Green

