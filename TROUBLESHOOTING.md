# Fehlerbehebung: "Verbindung zur Ostrom API nicht möglich"

## Mögliche Ursachen

### 1. Falsche API-Credentials

**Prüfe:**
- Client ID ist korrekt (aus dem Ostrom Developer Portal)
- Client Secret ist korrekt (aus dem Ostrom Developer Portal)
- Keine Leerzeichen vor/nach den Werten

**Lösung:**
- Gehe zu https://developer.ostrom-api.io/
- Logge dich ein
- Prüfe deine API Client Credentials
- Erstelle einen neuen Client, falls nötig

### 2. Falsche Environment

**Prüfe:**
- Hast du "Sandbox" oder "Production" gewählt?
- Deine Credentials müssen zur gewählten Environment passen

**Lösung:**
- Sandbox: Für Test-Credentials
- Production: Für echte Credentials
- Stelle sicher, dass die Credentials zur Environment passen

### 3. Falsche Contract ID

**Prüfe:**
- Contract ID ist die korrekte Vertragsnummer
- Keine Leerzeichen oder Sonderzeichen

**Lösung:**
- Prüfe deine Contract ID in der Ostrom App
- Oder im Developer Portal

### 4. Falsche Postleitzahl

**Prüfe:**
- Postleitzahl ist eine gültige deutsche PLZ (5-stellig)
- Format: z.B. "10115" (ohne Leerzeichen)

### 5. Netzwerk-/Firewall-Problem

**Prüfe:**
- Internetverbindung funktioniert
- Firewall blockiert nicht die Verbindung
- Home Assistant kann auf das Internet zugreifen

**Lösung:**
- Teste die Internetverbindung in Home Assistant
- Prüfe Firewall-Einstellungen

### 6. API-Server nicht erreichbar

**Prüfe:**
- Ostrom API-Server sind online
- Keine Wartungsarbeiten

**Lösung:**
- Prüfe https://status.ostrom.de/ (falls verfügbar)
- Versuche es später erneut

## Debugging: Logs prüfen

### Schritt 1: Log-Level erhöhen

1. Gehe zu **Settings** → **System** → **Logs**
2. Suche nach `ostrom_advanced`
3. Oder füge in `configuration.yaml` hinzu:

```yaml
logger:
  default: info
  logs:
    custom_components.ostrom_advanced: debug
```

4. Starte Home Assistant neu

### Schritt 2: Logs analysieren

Suche nach folgenden Einträgen:

```
ERROR custom_components.ostrom_advanced.api - Connection error: ...
ERROR custom_components.ostrom_advanced.api - Authentication error: ...
ERROR custom_components.ostrom_advanced.config_flow - ...
```

### Schritt 3: Häufige Fehlermeldungen

**"Authentication failed: Invalid credentials"**
- Client ID oder Client Secret ist falsch
- Prüfe im Developer Portal

**"Connection error: ..."**
- Netzwerkproblem
- API-Server nicht erreichbar

**"Bad request: ..."**
- Falsche Parameter (z.B. Contract ID, Postleitzahl)
- Prüfe die eingegebenen Werte

**"Rate limit exceeded"**
- Zu viele Anfragen
- Warte ein paar Minuten

## Manueller Test

Du kannst die API-Verbindung auch manuell testen:

### Mit cURL (Windows PowerShell):

```powershell
# Ersetze CLIENT_ID und CLIENT_SECRET
$clientId = "DEINE_CLIENT_ID"
$clientSecret = "DEIN_CLIENT_SECRET"
$credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${clientId}:${clientSecret}"))

# Sandbox
$authUrl = "https://auth.sandbox.ostrom-api.io/oauth2/token"

# Production
# $authUrl = "https://auth.production.ostrom-api.io/oauth2/token"

$body = @{
    grant_type = "client_credentials"
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Basic $credentials"
    "Content-Type" = "application/x-www-form-urlencoded"
    "Accept" = "application/json"
}

$response = Invoke-RestMethod -Uri $authUrl -Method Post -Headers $headers -Body "grant_type=client_credentials" -ContentType "application/x-www-form-urlencoded"

Write-Host "Access Token: $($response.access_token)"
```

Wenn das funktioniert, sind deine Credentials korrekt.

## Schritt-für-Schritt Prüfliste

- [ ] Client ID ist korrekt (aus Developer Portal)
- [ ] Client Secret ist korrekt (aus Developer Portal)
- [ ] Environment passt zu den Credentials (Sandbox/Production)
- [ ] Contract ID ist korrekt
- [ ] Postleitzahl ist eine gültige 5-stellige deutsche PLZ
- [ ] Internetverbindung funktioniert
- [ ] Keine Firewall blockiert die Verbindung
- [ ] Logs zeigen detaillierte Fehlermeldungen

## Noch Probleme?

1. **Prüfe die Logs** (siehe oben)
2. **Teste die API manuell** (siehe oben)
3. **Erstelle ein Issue auf GitHub** mit:
   - Fehlermeldung aus den Logs
   - Welche Werte du eingegeben hast (ohne Secrets!)
   - Environment (Sandbox/Production)

