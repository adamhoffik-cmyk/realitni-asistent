# Spustí backend v dev módu s hot-reloadem.
# Použití: .\scripts\dev-backend.ps1

$ErrorActionPreference = "Stop"
Set-Location -Path "$PSScriptRoot\..\backend"

# Zajisti, že venv existuje
if (-Not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "❌ Venv neexistuje. Spusť: .\scripts\setup-dev.ps1" -ForegroundColor Red
    exit 1
}

# Zajisti data adresáře
$dataDirs = @("data", "data/chroma", "data/reference_articles",
              "data/articles/drafts", "data/articles/published",
              "data/transcripts", "data/video_scripts", "data/uploads")
foreach ($d in $dataDirs) {
    if (-Not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
    }
}

# Zajisti .env
if (-Not (Test-Path "..\.env")) {
    Write-Host "⚠ .env neexistuje — kopíruji z .env.example" -ForegroundColor Yellow
    Copy-Item "..\.env.example" "..\.env"
}

Write-Host "🟢 Backend startuje na http://localhost:8000" -ForegroundColor Green
Write-Host "   API docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "   Ctrl+C pro ukončení" -ForegroundColor Gray
Write-Host ""

# Hot-reload při změně .py souborů
& .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
