# PowerShell Script zum Erstellen eines GitHub Releases
# Verwendung: .\create_release.ps1 -Tag "v0.4.0" -Token "dein-token"

param(
    [Parameter(Mandatory=$true)]
    [string]$Tag,
    
    [Parameter(Mandatory=$false)]
    [string]$Token
)

$repo = "Al3xand3r1987/ha-ostrom-advanced"
$apiUrl = "https://api.github.com/repos/$repo/releases"

# Prüfe ob Token vorhanden
if (-not $Token) {
    if ($env:GITHUB_TOKEN) {
        $Token = $env:GITHUB_TOKEN
        Write-Host "✅ GitHub Token aus Umgebungsvariable gefunden" -ForegroundColor Green
    } else {
        Write-Host "❌ Kein GitHub Token gefunden!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Bitte erstelle einen GitHub Personal Access Token:" -ForegroundColor Yellow
        Write-Host "1. Gehe zu: https://github.com/settings/tokens" -ForegroundColor Cyan
        Write-Host "2. Klicke 'Generate new token (classic)'" -ForegroundColor Cyan
        Write-Host "3. Wähle Scope: 'repo' (volle Kontrolle über private Repositories)" -ForegroundColor Cyan
        Write-Host "4. Kopiere den Token" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Dann führe aus:" -ForegroundColor Yellow
        Write-Host "  `$env:GITHUB_TOKEN = 'dein-token-hier'" -ForegroundColor Cyan
        Write-Host "  .\create_release.ps1 -Tag $Tag -Token `$env:GITHUB_TOKEN" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "ODER erstelle das Release manuell über:" -ForegroundColor Yellow
        Write-Host "  https://github.com/$repo/releases/new" -ForegroundColor Cyan
        exit 1
    }
}

# Erstelle Release
$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}

$body = @{
    tag_name = $Tag
    name = "Ostrom Advanced $Tag"
    draft = $false
    prerelease = $false
    body = ""  # Leer lassen, Workflow generiert automatisch
} | ConvertTo-Json

Write-Host "Erstelle GitHub Release für Tag: $Tag" -ForegroundColor Green

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "✅ Release erfolgreich erstellt!" -ForegroundColor Green
    Write-Host "   URL: $($response.html_url)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Der GitHub Actions Workflow wird automatisch getriggert und generiert Release Notes." -ForegroundColor Yellow
    Write-Host "HACS wird das Update innerhalb weniger Stunden erkennen." -ForegroundColor Yellow
} catch {
    Write-Host "❌ Fehler beim Erstellen des Releases:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
    exit 1
}

