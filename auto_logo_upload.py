#!/usr/bin/env python3
"""
Automatisierter Upload des HACS-Integration-Logos zum Home Assistant Brands Repository.
Kopiert icon.png und icon2x.png direkt ohne Bearbeitung ins Brands Repository.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Konfiguration
DOMAIN = "ostrom_advanced"
LOGO_SRC_ICON = "icon.png"
LOGO_SRC_ICON2X = "icon2x.png"
BRANDS_REPO_URL = "https://github.com/home-assistant/brands"
BRANDS_PATH = "./brands"
BRANCH_NAME = f"add-{DOMAIN}-logo"
TARGET_DIR = f"{BRANDS_PATH}/custom_integrations/{DOMAIN}"


def print_step(step, message):
    """Gibt einen Schritt mit Formatierung aus."""
    print(f"\n{'='*60}")
    print(f"STEP {step}: {message}")
    print(f"{'='*60}")


def check_dependencies():
    """Prüft und installiert benötigte Dependencies."""
    print_step(1, "Dependencies prüfen")
    
    try:
        import PIL
        print("[OK] Pillow ist installiert")
    except ImportError:
        print("[WARN] Pillow nicht gefunden. Installiere...")
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow", "-q"], check=True)
        print("[OK] Pillow installiert")
    
    # Git sollte standardmäßig verfügbar sein
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("[OK] Git ist verfügbar")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] FEHLER: Git ist nicht installiert oder nicht im PATH")
        sys.exit(1)


def setup_repository():
    """Setzt das Brands Repository auf (Clone oder nutzt bestehendes)."""
    print_step(2, "Repository Setup")
    
    # Prüfe ob brands/ bereits existiert
    if os.path.exists(BRANDS_PATH) and os.path.isdir(BRANDS_PATH):
        print(f"[OK] Brands Repository bereits vorhanden: {BRANDS_PATH}")
        
        # Prüfe ob es ein Git-Repository ist
        if os.path.exists(f"{BRANDS_PATH}/.git"):
            print("[OK] Ist ein Git-Repository")
            os.chdir(BRANDS_PATH)
            
            # Remote prüfen
            try:
                result = subprocess.run(
                    ["git", "remote", "-v"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"[OK] Remote konfiguriert:\n{result.stdout}")
            except subprocess.CalledProcessError:
                print("[WARN] Kein Remote konfiguriert")
            
            # Aktuellen Branch prüfen
            try:
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                current_branch = result.stdout.strip()
                print(f"[OK] Aktueller Branch: {current_branch}")
                
                # Zu main/master wechseln
                try:
                    subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
                    print("[OK] Zu 'main' gewechselt")
                except subprocess.CalledProcessError:
                    try:
                        subprocess.run(["git", "checkout", "master"], check=True, capture_output=True)
                        print("[OK] Zu 'master' gewechselt")
                    except subprocess.CalledProcessError:
                        print("[WARN] Konnte nicht zu main/master wechseln")
                
                # Pull latest changes
                try:
                    subprocess.run(["git", "pull"], check=True, capture_output=True)
                    print("[OK] Repository aktualisiert")
                except subprocess.CalledProcessError:
                    print("[WARN] Konnte nicht pullen (möglicherweise kein Remote)")
                
            except subprocess.CalledProcessError:
                print("[WARN] Konnte Branch nicht ermitteln")
            
            os.chdir("..")
        else:
            print("[WARN] Verzeichnis existiert, aber ist kein Git-Repository")
            print("  → Lösche und klone neu...")
            shutil.rmtree(BRANDS_PATH)
            clone_repository()
    else:
        clone_repository()
    
    # Branch erstellen
    create_branch()


def get_github_username():
    """Extrahiert den GitHub-Username aus dem Remote-URL oder manifest.json."""
    # Versuche aus Git Remote zu extrahieren
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True
        )
        # Extrahiere Username aus URL (z.B. https://github.com/USERNAME/repo.git)
        import re
        match = re.search(r'github\.com[/:]([^/]+)', result.stdout)
        if match:
            return match.group(1)
    except:
        pass
    
    # Fallback: Versuche aus manifest.json zu extrahieren
    try:
        import json
        with open("custom_components/ostrom_advanced/manifest.json", "r", encoding="utf-8") as f:
            manifest = json.load(f)
            if "documentation" in manifest:
                url = manifest["documentation"]
                import re
                match = re.search(r'github\.com/([^/]+)', url)
                if match:
                    return match.group(1)
    except:
        pass
    
    # Letzter Fallback: Git config user.name (kann Leerzeichen enthalten)
    try:
        username = subprocess.check_output(
            ["git", "config", "user.name"],
            text=True
        ).strip()
        # Ersetze Leerzeichen durch Bindestrich für URL
        return username.replace(" ", "-")
    except:
        return None


def clone_repository():
    """Klont das Brands Repository."""
    print(f"[INFO] Klone Brands Repository...")
    
    # Prüfe ob Fork existiert
    try:
        username = get_github_username()
        
        if username:
            fork_url = f"https://github.com/{username}/brands"
            print(f"[INFO] Prüfe Fork: {fork_url}")
            
            # Prüfe ob Fork existiert (einfache HTTP-Check)
            import urllib.request
            try:
                urllib.request.urlopen(f"https://github.com/{username}/brands", timeout=5)
                print(f"[OK] Fork gefunden: {fork_url}")
                repo_url = fork_url
            except:
                print(f"[WARN] Fork nicht gefunden, nutze Original: {BRANDS_REPO_URL}")
                repo_url = BRANDS_REPO_URL
        else:
            print(f"[WARN] Konnte GitHub-Username nicht ermitteln")
            print(f"  -> Nutze Original: {BRANDS_REPO_URL}")
            repo_url = BRANDS_REPO_URL
    except Exception as e:
        print(f"[WARN] Konnte Fork nicht prüfen: {e}")
        print(f"  -> Nutze Original: {BRANDS_REPO_URL}")
        repo_url = BRANDS_REPO_URL
    
    # Clone durchführen
    try:
        subprocess.run(
            ["git", "clone", repo_url, BRANDS_PATH],
            check=True,
            capture_output=True
        )
        print(f"[OK] Repository geklont: {BRANDS_PATH}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FEHLER beim Klonen: {e}")
        print(f"   Stelle sicher, dass du Zugriff auf {repo_url} hast")
        sys.exit(1)


def create_branch():
    """Erstellt einen neuen Branch für das Logo."""
    global BRANCH_NAME
    
    print(f"[INFO] Erstelle Branch: {BRANCH_NAME}")
    
    os.chdir(BRANDS_PATH)
    
    # Prüfe ob Branch bereits existiert
    try:
        result = subprocess.run(
            ["git", "branch", "-a"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if BRANCH_NAME in result.stdout or f"origin/{BRANCH_NAME}" in result.stdout:
            # Branch existiert bereits, erstelle neuen mit Timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            new_branch = f"{BRANCH_NAME}-{timestamp}"
            print(f"[WARN] Branch {BRANCH_NAME} existiert bereits")
            print(f"   -> Erstelle neuen Branch: {new_branch}")
            subprocess.run(["git", "checkout", "-b", new_branch], check=True)
            BRANCH_NAME = new_branch
        else:
            # Neuer Branch
            subprocess.run(["git", "checkout", "-b", BRANCH_NAME], check=True)
            print(f"[OK] Branch erstellt: {BRANCH_NAME}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FEHLER beim Branch-Erstellen: {e}")
        os.chdir("..")
        sys.exit(1)
    
    os.chdir("..")


def copy_logos():
    """Kopiert die Logo-Dateien ins Brands Repository."""
    print_step(3, "Logo-Dateien kopieren")
    
    # Prüfe ob Logo-Dateien existieren
    if not os.path.exists(LOGO_SRC_ICON):
        print(f"[ERROR] FEHLER: {LOGO_SRC_ICON} nicht gefunden!")
        sys.exit(1)
    
    if not os.path.exists(LOGO_SRC_ICON2X):
        print(f"[ERROR] FEHLER: {LOGO_SRC_ICON2X} nicht gefunden!")
        sys.exit(1)
    
    print(f"[OK] {LOGO_SRC_ICON} gefunden")
    print(f"[OK] {LOGO_SRC_ICON2X} gefunden")
    
    # Erstelle Zielordner
    os.makedirs(TARGET_DIR, exist_ok=True)
    print(f"[OK] Ordner erstellt: {TARGET_DIR}")
    
    # Kopiere Dateien
    target_icon = f"{TARGET_DIR}/icon.png"
    target_icon2x = f"{TARGET_DIR}/icon@2x.png"
    
    shutil.copy2(LOGO_SRC_ICON, target_icon)
    print(f"[OK] Kopiert: {LOGO_SRC_ICON} -> {target_icon}")
    
    shutil.copy2(LOGO_SRC_ICON2X, target_icon2x)
    print(f"[OK] Kopiert: {LOGO_SRC_ICON2X} -> {target_icon2x}")
    
    # Optional: Validiere Dateigröße
    try:
        from PIL import Image
        
        # Prüfe icon.png
        img = Image.open(target_icon)
        size_icon = os.path.getsize(target_icon) / 1024  # KB
        print(f"  -> icon.png: {img.size[0]}x{img.size[1]}px, {size_icon:.1f}KB")
        if size_icon > 50:
            print(f"  [WARN] Warnung: icon.png ist groesser als 50KB ({size_icon:.1f}KB)")
        
        # Prüfe icon@2x.png
        img2x = Image.open(target_icon2x)
        size_icon2x = os.path.getsize(target_icon2x) / 1024  # KB
        print(f"  -> icon@2x.png: {img2x.size[0]}x{img2x.size[1]}px, {size_icon2x:.1f}KB")
        if size_icon2x > 50:
            print(f"  [WARN] Warnung: icon@2x.png ist groesser als 50KB ({size_icon2x:.1f}KB)")
        
    except ImportError:
        print("  [WARN] Pillow nicht verfuegbar, ueberspringe Validierung")
    except Exception as e:
        print(f"  [WARN] Validierung fehlgeschlagen: {e}")


def git_operations():
    """Führt Git-Operationen durch (add, commit, push)."""
    print_step(4, "Git-Operationen")
    
    os.chdir(BRANDS_PATH)
    
    # Git add
    try:
        subprocess.run(
            ["git", "add", f"custom_integrations/{DOMAIN}/"],
            check=True,
            capture_output=True
        )
        print(f"[OK] Git add: custom_integrations/{DOMAIN}/")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FEHLER bei git add: {e}")
        os.chdir("..")
        sys.exit(1)
    
    # Git commit
    commit_message = f"Add logo for {DOMAIN} custom integration"
    try:
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            check=True,
            capture_output=True
        )
        print(f"[OK] Git commit: {commit_message}")
    except subprocess.CalledProcessError as e:
        # Möglicherweise keine Änderungen
        if "nothing to commit" in str(e):
            print("[WARN] Keine Aenderungen zu committen (Dateien moeglicherweise bereits committed)")
        else:
            print(f"[ERROR] FEHLER bei git commit: {e}")
            os.chdir("..")
            sys.exit(1)
    
    # Git push
    try:
        subprocess.run(
            ["git", "push", "origin", BRANCH_NAME],
            check=True,
            capture_output=True
        )
        print(f"[OK] Git push: origin {BRANCH_NAME}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FEHLER bei git push: {e}")
        print(f"   Stelle sicher, dass:")
        print(f"   1. Du einen Fork des Brands Repository hast")
        print(f"   2. Der Remote 'origin' auf deinen Fork zeigt")
        print(f"   3. Du die noetigen Berechtigungen hast")
        os.chdir("..")
        sys.exit(1)
    
    os.chdir("..")


def generate_pr_url():
    """Generiert die PR-URL und gibt sie aus."""
    print_step(5, "Pull Request URL generieren")
    
    try:
        # GitHub Username extrahieren
        username = get_github_username()
        
        if not username:
            raise Exception("GitHub-Username konnte nicht ermittelt werden")
        
        pr_url = f"https://github.com/home-assistant/brands/compare/main...{username}:brands:{BRANCH_NAME}?expand=1"
        
        print(f"\n{'='*60}")
        print(f"[SUCCESS] FERTIG! Pull Request erstellen:")
        print(f"\n{pr_url}")
        print(f"\n{'='*60}")
        print(f"\n[INFO] PR-Titel: Add logo for {DOMAIN} custom integration")
        print(f"[INFO] PR-Beschreibung siehe: PR_BODY.txt")
        print(f"\n[INFO] Klicke auf die URL oben und erstelle den Pull Request!")
        
        return pr_url
    except Exception as e:
        print(f"[WARN] Konnte PR-URL nicht generieren: {e}")
        print(f"   Erstelle manuell einen PR von {username}:{BRANCH_NAME} zu home-assistant/brands:main")


def main():
    """Hauptfunktion."""
    print("\n" + "="*60)
    print("HACS LOGO AUTO-UPLOAD")
    print("="*60)
    print(f"Domain: {DOMAIN}")
    print(f"Logo-Quellen: {LOGO_SRC_ICON}, {LOGO_SRC_ICON2X}")
    print("="*60)
    
    # Führe alle Schritte aus
    check_dependencies()
    setup_repository()
    copy_logos()
    git_operations()
    generate_pr_url()
    
    print("\n[SUCCESS] Alle Schritte erfolgreich abgeschlossen!")


if __name__ == "__main__":
    main()
