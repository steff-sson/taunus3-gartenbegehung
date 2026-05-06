# Entwicklung

## Setup

```bash
# Virtuelle Umgebung erstellen (einmalig)
python -m venv .venv

# Aktivieren
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Tests ausführen
pytest

# App starten (Entwicklung)
flask run --host=0.0.0.0

# App starten (Produktion via gunicorn)
gunicorn -b 0.0.0.0:5000 app:app
```

## Server-Setup (einmalig)

### System-Dependencies für WeasyPrint

**Debian/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

**Arch Linux:**
```bash
sudo pacman -S cairo pango gdk-pixbuf2 libffi shared-mime-info
```

### systemd Service

Die Vorlage `gartenbegehung.service.template` enthält `<USER>`, `<GROUP>` und `<APP_DIR>` als Platzhalter. Auf den Server kopieren, Platzhalter ersetzen und ablegen als:
```
/etc/systemd/system/taunus3-gartenbegehung.service
```

```bash
# Nach Anpassung der Platzhalter
sudo cp gartenbegehung.service.template /etc/systemd/system/taunus3-gartenbegehung.service
sudo systemctl daemon-reload
sudo systemctl enable --now taunus3-gartenbegehung
```

Nach Code-Updates:
```bash
git pull
sudo systemctl restart taunus3-gartenbegehung
```

## Code-Struktur

### app.py

| Funktion | Beschreibung |
|----------|---------------|
| `load_items()` | Lädt items.csv mit Auto-Reload (mtime-basiert) |
| `get_item_by_id()` | Sucht Item nach ID in allen Kategorien |
| `get_output_text()` | Ersetzt `{value}` in output_text |
| `make_tree()` | Erstellt rekursive Verzeichnisstruktur für /pdfs |
| Routes: `/`, `/name`, `/form`, `/preview`, `/done`, `/pdfs` | App-Routen |

### Templates

- `layout.html` / `layout-certificate.html` - Basis-Layouts (W3.CSS)
- `form.html` - Dynamisches Formular (Loop über CSV)
- `preview.html` - Vorschau vor Speichern
- `certificate.html` - PDF-Vorlage
- `done.html` - Erfolgsseite
- `pdfs.html` - PDF-Liste mit korrekten Links

### Statische Dateien

- `static/items.csv` - Formular-Konfiguration (wird automatisch neu geladen)
- `static/pdf/{jahr}/` - Generierte PDFs
- `static/gartenbegehung-{jahr}.csv` - Jahresdaten

## items.csv

Die CSV-Datei steuert alle Formularfelder. Änderungen werden bei jedem Request automatisch wirksam (kein Neustart).

### CSV-Felder (vollständig)

| Feld | Typ | Beschreibung | Beispiel |
|------|-----|--------------|----------|
| id | string | Eindeutiger Identifier (für HTML name="" ) | parzelle, dachbauten_keine |
| category | string | Gruppierung (Basis, Dachbauten, Drittelung, Unkraut, Sonstiges) | Basis |
| type | string | Input-Typ | number, text, select, checkbox |
| required | string | Pflichtfeld (true/false) | true |
| label | string | Anzeigetext im Formular | Parzellennummer |
| placeholder | string | Placeholder-Text | z.B. 42 |
| output_text | string | Text für PDF/CSV ( `{value}` wird ersetzt) | Parzelle: {value} |
| severity | string | Schweregrad für Farbcodierung | info, warning, error |
| options | string | Nur für select: kommaseparierte Werte | (leer) |

### Neue Items hinzufügen

1. `static/items.csv` bearbeiten
2. Neue Zeile mit allen Feldern hinzufügen
3. Kein Neustart nötig – wird automatisch erkannt

### Hinweise

- `{value}` in output_text wird durch den eingegebenen Wert ersetzt
- category muss klein geschrieben werden (basis, dachbauten, drittelung, unkraut, sonstiges)
- type muss gültig sein: number, text, select, checkbox

## Tests

```bash
# Alle Tests ausführen
pytest

# Mit Coverage
pytest --cov=app --cov-report=term-missing
```

## Styling

- **CSS-Framework:** W3.CSS (CDN)
- **Custom CSS:** `static/custom.css`
- **JS:** `static/slider-value.js`
- **Farbschema:** Türkis (#009688) als Primärfarbe (BKleingG-konform)

Bei Änderungen an Templates soll das bestehende W3.CSS-Styling beibehalten werden.

## Umgebungsvariablen

| Variable | Beschreibung | Standard |
|----------|--------------|----------|
| SECRET_KEY | Flask Secret Key | dev-fallback-key |
| FLASK_ENV | development / production | development |

## Ordnerstruktur

```
taunus3-gartenbegehung/
├── .venv/                    # Virtuelle Umgebung
├── requirements.txt          # Python-Abhängigkeiten
├── .env                      # Umgebungsvariablen (nicht in Git)
├── static/
│   ├── items.csv             # Formular-Konfiguration
│   ├── pdf/                  # Generierte PDFs
│   │   └── {jahr}/
│   ├── gartenbegehung-{jahr}.csv  # Jahresdaten
│   └── custom.css            # Eigenes CSS
├── templates/
│   ├── layout.html           # Basis-Layout
│   ├── form.html             # Formular
│   └── ...
├── app.py                    # Haupt-App
├── agents.md                 # Diese Datei
└── tests/                    # Tests
    └── test_items.py
```