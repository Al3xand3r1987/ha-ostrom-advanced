#!/bin/bash

# Ostrom Advanced - Release Notes Generator
# Generiert Release Notes aus Git-Commits seit dem letzten Tag

set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Ostrom Advanced - Release Notes Generator${NC}"
echo ""

# 1. Lese Version aus manifest.json
MANIFEST_FILE="custom_components/ostrom_advanced/manifest.json"
if [ ! -f "$MANIFEST_FILE" ]; then
    echo -e "${RED}❌ Fehler: $MANIFEST_FILE nicht gefunden!${NC}"
    exit 1
fi

VERSION=$(grep -o '"version": "[^"]*"' "$MANIFEST_FILE" | cut -d'"' -f4)
if [ -z "$VERSION" ]; then
    echo -e "${RED}❌ Fehler: Version nicht in manifest.json gefunden!${NC}"
    exit 1
fi

TAG="v${VERSION}"
echo -e "${GREEN}✓${NC} Aktuelle Version: ${YELLOW}$VERSION${NC} (Tag: ${YELLOW}$TAG${NC})"

# 2. Finde letzten Tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -z "$LAST_TAG" ]; then
    echo -e "${YELLOW}⚠${NC}  Kein vorheriger Tag gefunden. Verwende ersten Commit als Basis."
    LAST_TAG=$(git rev-list --max-parents=0 HEAD 2>/dev/null || echo "")
    if [ -z "$LAST_TAG" ]; then
        echo -e "${RED}❌ Fehler: Keine Git-Historie gefunden!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Letzter Tag: ${YELLOW}$LAST_TAG${NC}"
fi

# 3. Sammle Commits seit letztem Tag
echo ""
echo -e "${GREEN}📝 Sammle Commits seit $LAST_TAG...${NC}"

# Kategorisiere Commits nach Conventional Commits
FEATURES=$(git log ${LAST_TAG}..HEAD --pretty=format:"- %s (%h)" --no-merges 2>/dev/null | grep -E "^-\s*(feat|feature):" | sed 's/^-\s*\(feat\|feature\):/-/' || echo "")
FIXES=$(git log ${LAST_TAG}..HEAD --pretty=format:"- %s (%h)" --no-merges 2>/dev/null | grep -E "^-\s*(fix|bug):" | sed 's/^-\s*\(fix\|bug\):/-/' || echo "")
CHORES=$(git log ${LAST_TAG}..HEAD --pretty=format:"- %s (%h)" --no-merges 2>/dev/null | grep -E "^-\s*(chore|refactor):" | sed 's/^-\s*\(chore\|refactor\):/-/' || echo "")
DOCS=$(git log ${LAST_TAG}..HEAD --pretty=format:"- %s (%h)" --no-merges 2>/dev/null | grep -E "^-\s*docs:" | sed 's/^-\s*docs:/-/' || echo "")
OTHER=$(git log ${LAST_TAG}..HEAD --pretty=format:"- %s (%h)" --no-merges 2>/dev/null | grep -vE "^-\s*(feat|feature|fix|bug|docs|chore|refactor):" || echo "")

# Prüfe ob es überhaupt Commits gibt
TOTAL_COMMITS=$(git rev-list --count ${LAST_TAG}..HEAD 2>/dev/null || echo "0")
if [ "$TOTAL_COMMITS" -eq "0" ]; then
    echo -e "${YELLOW}⚠${NC}  Keine neuen Commits seit $LAST_TAG gefunden!"
    exit 0
fi

echo -e "${GREEN}✓${NC} Gefunden: $TOTAL_COMMITS Commit(s)"

# 4. Berechne Versionsempfehlung basierend auf Commits
HAS_FEATURES=$(echo "$FEATURES" | grep -q "." && echo "yes" || echo "no")
HAS_FIXES=$(echo "$FIXES" | grep -q "." && echo "yes" || echo "no")
HAS_BREAKING=$(git log ${LAST_TAG}..HEAD --pretty=format:"%s" --no-merges 2>/dev/null | grep -qi "breaking" && echo "yes" || echo "no")

# Parse aktuelle Version (X.Y.Z)
IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"

# Berechne neue Version
if [ "$HAS_BREAKING" = "yes" ]; then
    # Breaking Change → Major Version
    NEW_MAJOR=$((MAJOR + 1))
    NEW_MINOR=0
    NEW_PATCH=0
    VERSION_TYPE="MAJOR (Breaking Changes)"
elif [ "$HAS_FEATURES" = "yes" ]; then
    # Neue Features → Minor Version
    NEW_MAJOR=$MAJOR
    NEW_MINOR=$((MINOR + 1))
    NEW_PATCH=0
    VERSION_TYPE="MINOR (New Features)"
elif [ "$HAS_FIXES" = "yes" ]; then
    # Nur Bugfixes → Patch Version
    NEW_MAJOR=$MAJOR
    NEW_MINOR=$MINOR
    NEW_PATCH=$((PATCH + 1))
    VERSION_TYPE="PATCH (Bug Fixes)"
else
    # Nur Docs/Chores → Patch Version
    NEW_MAJOR=$MAJOR
    NEW_MINOR=$MINOR
    NEW_PATCH=$((PATCH + 1))
    VERSION_TYPE="PATCH (Maintenance)"
fi

NEW_VERSION="${NEW_MAJOR}.${NEW_MINOR}.${NEW_PATCH}"
NEW_TAG="v${NEW_VERSION}"

echo ""
echo -e "${YELLOW}📌 Versionsempfehlung:${NC}"
echo -e "   Aktuelle Version: ${YELLOW}$VERSION${NC}"
echo -e "   Empfohlene Version: ${GREEN}$NEW_VERSION${NC} (${VERSION_TYPE})"
echo ""

# 5. Generiere Release Notes (Priorität: Features → Fixes → Maintenance → Docs)
OUTPUT_FILE="RELEASE_NOTES.md"

{
    echo "# Ostrom Advanced $NEW_TAG"
    echo ""
    echo "## 🚀 New Features"
    if [ -n "$FEATURES" ]; then
        echo "$FEATURES"
    else
        echo "- Keine neuen Features"
    fi
    echo ""
    echo "## 🐛 Bug Fixes"
    if [ -n "$FIXES" ]; then
        echo "$FIXES"
    else
        echo "- Keine Bugfixes"
    fi
    echo ""
    echo "## 🔧 Maintenance"
    if [ -n "$CHORES" ]; then
        echo "$CHORES"
    else
        echo "- Keine Wartungsarbeiten"
    fi
    echo ""
    echo "## 📝 Documentation"
    if [ -n "$DOCS" ]; then
        echo "$DOCS"
    else
        echo "- Keine Dokumentationsänderungen"
    fi
    if [ -n "$OTHER" ]; then
        echo ""
        echo "## 📦 Other Changes"
        echo "$OTHER"
    fi
} > "$OUTPUT_FILE"

echo ""
echo -e "${GREEN}✓${NC} Release Notes generiert: ${YELLOW}$OUTPUT_FILE${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
cat "$OUTPUT_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ Fertig!${NC} Release Notes wurden in ${YELLOW}$OUTPUT_FILE${NC} gespeichert."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}📋 COPY-PASTE BEFEHLE:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "# 1. Version in manifest.json aktualisieren:"
echo "   (Die Version ist bereits in den Release Notes als $NEW_VERSION vorgeschlagen)"
echo ""
echo "# 2. Git-Befehle zum Taggen und Pushen:"
echo "   git add custom_components/ostrom_advanced/manifest.json"
echo "   git commit -m \"chore: release $NEW_TAG\""
echo "   git tag $NEW_TAG"
echo "   git push origin main"
echo "   git push origin $NEW_TAG"
echo ""
echo "# 3. Release Notes kopieren:"
echo "   (Die Release Notes sind in $OUTPUT_FILE gespeichert)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}Nächste Schritte:${NC}"
echo "1. ${YELLOW}Version aktualisieren:${NC} Setze Version in manifest.json auf ${GREEN}$NEW_VERSION${NC}"
echo "2. ${YELLOW}Release Notes kopieren:${NC} Öffne $OUTPUT_FILE und kopiere den Inhalt"
echo "3. ${YELLOW}Tag erstellen & pushen:${NC} Verwende die Git-Befehle oben"
echo "4. ${YELLOW}Release auf GitHub:${NC} Gehe zu https://github.com/Al3xand3r1987/ha-ostrom-advanced/releases/new"
echo "   - Wähle Tag: ${GREEN}$NEW_TAG${NC}"
echo "   - Füge die kopierten Release Notes ein"
echo "   - Klicke auf 'Publish release'"
echo ""

