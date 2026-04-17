# Jednorázový setup dev prostředí (Windows, bez Dockeru).
# Použití: .\scripts\setup-dev.ps1

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot

Write-Host "=== Realitní Asistent — lokální dev setup ===" -ForegroundColor Cyan
Write-Host ""

# --- 1. Python 3.12 check ---
$py312 = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-Not (Test-Path $py312)) {
    Write-Host "Python 3.12 nenalezen. Instaluji přes winget…" -ForegroundColor Yellow
    winget install Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements --silent
    if (-Not (Test-Path $py312)) {
        Write-Host "❌ Python 3.12 se nepodařilo nainstalovat. Nainstaluj ručně z python.org" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✓ Python 3.12 ($py312)" -ForegroundColor Green

# --- 2. Node.js check ---
try {
    $nodeVersion = (node --version) -replace "v", ""
    $nodeMajor = [int]($nodeVersion.Split(".")[0])
    if ($nodeMajor -lt 18) {
        Write-Host "⚠ Node $nodeVersion je starší než doporučené v20. Funguje i tak, ale upgrade by pomohl." -ForegroundColor Yellow
    } else {
        Write-Host "✓ Node v$nodeVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Node.js nenalezen. Nainstaluj z https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# --- 3. .env ---
if (-Not (Test-Path "$repo\.env")) {
    Copy-Item "$repo\.env.example" "$repo\.env"
    Write-Host "✓ .env vytvořeno (kopie .env.example). Uprav pokud potřeba." -ForegroundColor Green
} else {
    Write-Host "✓ .env už existuje" -ForegroundColor Green
}

# --- 4. Backend venv ---
$venvPy = "$repo\backend\.venv\Scripts\python.exe"
if (-Not (Test-Path $venvPy)) {
    Write-Host ""
    Write-Host "Vytvářím backend venv…" -ForegroundColor Yellow
    & $py312 -m venv "$repo\backend\.venv"
}
Write-Host "✓ Backend venv" -ForegroundColor Green

# --- 5. Backend dependencies ---
Write-Host ""
Write-Host "Instaluji backend závislosti (může trvat 3-5 min)…" -ForegroundColor Yellow
Set-Location "$repo\backend"
& $venvPy -m pip install --upgrade pip --quiet
& $venvPy -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ pip install selhal" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Backend závislosti nainstalované" -ForegroundColor Green

# --- 6. Frontend dependencies ---
Write-Host ""
Write-Host "Instaluji frontend závislosti…" -ForegroundColor Yellow
Set-Location "$repo\frontend"
if (-Not (Test-Path "node_modules")) {
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ npm install selhal" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✓ Frontend závislosti nainstalované" -ForegroundColor Green

# --- 7. Data adresáře ---
$dataDirs = @(
    "$repo\backend\data",
    "$repo\backend\data\chroma",
    "$repo\backend\data\reference_articles",
    "$repo\backend\data\articles\drafts",
    "$repo\backend\data\articles\published",
    "$repo\backend\data\transcripts",
    "$repo\backend\data\video_scripts",
    "$repo\backend\data\uploads"
)
foreach ($d in $dataDirs) {
    if (-Not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
    }
}
Write-Host "✓ Data adresáře" -ForegroundColor Green

Set-Location $repo

Write-Host ""
Write-Host "=== Setup hotov ✓ ===" -ForegroundColor Green
Write-Host ""
Write-Host "Spuštění (ve dvou terminálech):" -ForegroundColor Cyan
Write-Host "  .\scripts\dev-backend.ps1    # terminal 1" -ForegroundColor White
Write-Host "  .\scripts\dev-frontend.ps1   # terminal 2" -ForegroundColor White
Write-Host ""
Write-Host "Pak otevři http://localhost:3000" -ForegroundColor Cyan
