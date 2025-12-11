# Ostrom Advanced - Release Notes Generator (PowerShell)
# Generiert Release Notes aus Git-Commits seit dem letzten Tag

$ErrorActionPreference = "Stop"

Write-Host "🚀 Ostrom Advanced - Release Notes Generator" -ForegroundColor Green
Write-Host ""

# 1. Lese Version aus manifest.json
$manifestFile = "custom_components/ostrom_advanced/manifest.json"
if (-not (Test-Path $manifestFile)) {
    Write-Host "❌ Fehler: $manifestFile nicht gefunden!" -ForegroundColor Red
    exit 1
}

$manifestContent = Get-Content $manifestFile -Raw | ConvertFrom-Json
$version = $manifestContent.version
if (-not $version) {
    Write-Host "❌ Fehler: Version nicht in manifest.json gefunden!" -ForegroundColor Red
    exit 1
}

$tag = "v$version"
Write-Host "✓ Aktuelle Version: $version (Tag: $tag)" -ForegroundColor Green

# 2. Finde letzten Tag
try {
    $lastTag = git describe --tags --abbrev=0 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $lastTag) {
        Write-Host "⚠ Kein vorheriger Tag gefunden. Verwende ersten Commit als Basis." -ForegroundColor Yellow
        $lastTag = git rev-list --max-parents=0 HEAD 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $lastTag) {
            Write-Host "❌ Fehler: Keine Git-Historie gefunden!" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✓ Letzter Tag: $lastTag" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Fehler beim Abrufen des letzten Tags: $_" -ForegroundColor Red
    exit 1
}

# 3. Sammle Commits seit letztem Tag
Write-Host ""
Write-Host "📝 Sammle Commits seit $lastTag..." -ForegroundColor Green

# Prüfe ob es überhaupt Commits gibt
$totalCommits = git rev-list --count "${lastTag}..HEAD" 2>$null
if ($LASTEXITCODE -ne 0) {
    $totalCommits = 0
}

if ($totalCommits -eq 0) {
    Write-Host "⚠ Keine neuen Commits seit $lastTag gefunden!" -ForegroundColor Yellow
    exit 0
}

Write-Host "✓ Gefunden: $totalCommits Commit(s)" -ForegroundColor Green

# Sammle alle Commits
$allCommits = git log "${lastTag}..HEAD" --pretty=format:"- %s (%h)" --no-merges 2>$null
$allCommitMessages = git log "${lastTag}..HEAD" --pretty=format:"%s" --no-merges 2>$null

# Kategorisiere Commits nach Conventional Commits
$features = @()
$fixes = @()
$chores = @()
$docs = @()
$other = @()

foreach ($commit in $allCommits) {
    if ($commit -match "^\s*-\s*(feat|feature):\s*(.+)$") {
        $features += "- $($matches[2])"
    }
    elseif ($commit -match "^\s*-\s*(fix|bug):\s*(.+)$") {
        $fixes += "- $($matches[2])"
    }
    elseif ($commit -match "^\s*-\s*(chore|refactor):\s*(.+)$") {
        $chores += "- $($matches[2])"
    }
    elseif ($commit -match "^\s*-\s*docs:\s*(.+)$") {
        $docs += "- $($matches[1])"
    }
    else {
        $other += $commit
    }
}

# 4. Berechne Versionsempfehlung basierend auf Commits
$hasFeatures = $features.Count -gt 0
$hasFixes = $fixes.Count -gt 0
$hasBreaking = ($allCommitMessages | Where-Object { $_ -match "breaking" -or $_ -match "BREAKING" }).Count -gt 0

# Parse aktuelle Version (X.Y.Z)
$versionParts = $version -split '\.'
$major = [int]$versionParts[0]
$minor = [int]$versionParts[1]
$patch = [int]$versionParts[2]

# Berechne neue Version
if ($hasBreaking) {
    # Breaking Change → Major Version
    $newMajor = $major + 1
    $newMinor = 0
    $newPatch = 0
    $versionType = "MAJOR (Breaking Changes)"
} elseif ($hasFeatures) {
    # Neue Features → Minor Version
    $newMajor = $major
    $newMinor = $minor + 1
    $newPatch = 0
    $versionType = "MINOR (New Features)"
} elseif ($hasFixes) {
    # Nur Bugfixes → Patch Version
    $newMajor = $major
    $newMinor = $minor
    $newPatch = $patch + 1
    $versionType = "PATCH (Bug Fixes)"
} else {
    # Nur Docs/Chores → Patch Version
    $newMajor = $major
    $newMinor = $minor
    $newPatch = $patch + 1
    $versionType = "PATCH (Maintenance)"
}

$newVersion = "$newMajor.$newMinor.$newPatch"
$newTag = "v$newVersion"

Write-Host ""
Write-Host "📌 Versionsempfehlung:" -ForegroundColor Yellow
Write-Host "   Aktuelle Version: $version" -ForegroundColor Yellow
Write-Host "   Empfohlene Version: $newVersion ($versionType)" -ForegroundColor Green
Write-Host ""

# 5. Generiere Release Notes (Priorität: Features → Fixes → Maintenance → Docs)
$outputFile = "RELEASE_NOTES.md"
$releaseNotes = @"
# Ostrom Advanced $newTag

## 🚀 New Features
$(if ($features.Count -gt 0) { $features -join "`n" } else { "- Keine neuen Features" })

## 🐛 Bug Fixes
$(if ($fixes.Count -gt 0) { $fixes -join "`n" } else { "- Keine Bugfixes" })

## 🔧 Maintenance
$(if ($chores.Count -gt 0) { $chores -join "`n" } else { "- Keine Wartungsarbeiten" })

## 📝 Documentation
$(if ($docs.Count -gt 0) { $docs -join "`n" } else { "- Keine Dokumentationsänderungen" })
"@

if ($other.Count -gt 0) {
    $releaseNotes += "`n`n## 📦 Other Changes`n"
    $releaseNotes += $other -join "`n"
}

$releaseNotes | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host ""
Write-Host "✓ Release Notes generiert: $outputFile" -ForegroundColor Green
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host $releaseNotes
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "✅ Fertig! Release Notes wurden in $outputFile gespeichert." -ForegroundColor Green
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "📋 COPY-PASTE BEFEHLE:" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "# 1. Version in manifest.json aktualisieren:"
Write-Host "   (Die Version ist bereits in den Release Notes als $newVersion vorgeschlagen)"
Write-Host ""
Write-Host "# 2. Git-Befehle zum Taggen und Pushen:"
Write-Host "   git add custom_components/ostrom_advanced/manifest.json"
Write-Host "   git commit -m `"chore: release $newTag`""
Write-Host "   git tag $newTag"
Write-Host "   git push origin main"
Write-Host "   git push origin $newTag"
Write-Host ""
Write-Host "# 3. Release Notes kopieren:"
Write-Host "   (Die Release Notes sind in $outputFile gespeichert)"
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "Nächste Schritte:" -ForegroundColor Green
Write-Host "1. Version aktualisieren: Setze Version in manifest.json auf $newVersion" -ForegroundColor Yellow
Write-Host "2. Release Notes kopieren: Öffne $outputFile und kopiere den Inhalt" -ForegroundColor Yellow
Write-Host "3. Tag erstellen & pushen: Verwende die Git-Befehle oben" -ForegroundColor Yellow
Write-Host "4. Release auf GitHub: Gehe zu https://github.com/Al3xand3r1987/ha-ostrom-advanced/releases/new" -ForegroundColor Yellow
Write-Host "   - Wähle Tag: $newTag" -ForegroundColor Green
Write-Host "   - Füge die kopierten Release Notes ein"
Write-Host "   - Klicke auf 'Publish release'"
Write-Host ""

