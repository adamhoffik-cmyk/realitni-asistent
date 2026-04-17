# Spustí frontend v Next.js dev módu.
# Použití: .\scripts\dev-frontend.ps1

$ErrorActionPreference = "Stop"
Set-Location -Path "$PSScriptRoot\..\frontend"

if (-Not (Test-Path "node_modules")) {
    Write-Host "⚠ node_modules neexistuje, instaluji…" -ForegroundColor Yellow
    npm install
}

Write-Host "🟢 Frontend startuje na http://localhost:3000" -ForegroundColor Green
Write-Host "   Ctrl+C pro ukončení" -ForegroundColor Gray
Write-Host ""

npm run dev
