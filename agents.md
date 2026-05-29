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
| `clear_items_cache()` | Cache manuell zurücksetzen |
| `get_item_by_id()` | Sucht Item nach ID in allen Kategorien |
| `format_output()` | Ersetzt `{value}` in output_text |
| `get_output_text()` | Kombiniert get_item_by_id + format_output |
| `make_tree()` | Erstellt rekursive Verzeichnisstruktur für /pdfs |
| Routes: `/`, `/name`, `/form`, `/preview`, `/done`, `/pdfs`, `/api/last-dach` | App-Routen |

### Templates

- `layout.html` / `layout-certificate.html` - Basis-Layouts (W3.CSS)
- `form.html` - Dynamisches Formular (Loop über CSV), inkl. Dach-Daten-Button; Selects als Radio-Buttons oder Button-Gruppe gerendert
- `preview.html` - Vorschau vor Speichern, inkl. Abmahnung-Warnung und Frist-Hinweis
- `certificate.html` - PDF-Vorlage, inkl. Frist-Hinweis nach Sonstiges-Liste
- `abmahnung.html` - Abmahnung-PDF (dynamischer Titel je Mahnungslevel)
- `done.html` - Erfolgsseite
- `pdfs.html` - PDF-Liste mit korrekten Links

### Statische Dateien

- `static/items.csv` - Formular-Konfiguration (wird automatisch neu geladen)
- `static/pdf/{jahr}/` - Generierte PDFs (inkl. Abmahnung-PDFs)
- `static/gartenbegehung-{jahr}.csv` - Jahresdaten (Semikolon-getrennt)
- `static/custom.css` - Eigenes CSS
- `static/slider-value.js` - JavaScript (Range-Slider, Dach-Daten-Button)
- `static/loading.gif` / `static/taunus3-small.png` / `static/taunus3.jpg` - Bilder

## items.csv

Die CSV-Datei steuert alle Formularfelder. Änderungen werden bei jedem Request automatisch wirksam (kein Neustart).

### CSV-Felder (vollständig)

| Feld | Typ | Beschreibung | Beispiel |
|------|-----|--------------|----------|
| id | string | Eindeutiger Identifier (für HTML name="" ) | parzelle, dachbauten_keine |
| category | string | Gruppierung (Basis, Dachbauten, Drittelung, Unkraut, Sonstiges, Abmahnung) | Basis |
| type | string | Input-Typ (select-Items werden als Radio-Buttons bzw. Button-Gruppe gerendert) | number, text, select, checkbox, date |
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
- category muss klein geschrieben werden (basis, dachbauten, drittelung, unkraut, sonstiges, abmahnung)
- type muss gültig sein: number, text, select, checkbox, date
- `Frist` (type=date) ist ein Pflichtfeld mit Platzhalter-Wert, der im Formular vorausgefüllt und bearbeitbar ist
- Items mit `id` in `details0, details1, Frist` werden von Abmahnungsgründen ausgeschlossen, ebenso alle Dachbauten-Items

## Tests

```bash
# Alle Tests ausführen
pytest

# Mit Coverage
pytest --cov=app --cov-report=term-missing
```

## Styling

- **CSS-Framework:** W3.CSS (CDN)
- **Custom CSS:** `static/custom.css` (enthält Styles für Radio-Buttons, Button-Gruppe, Checkboxen, Formular, Layout)
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
│   ├── pdf/                  # Generierte PDFs (inkl. Abmahnungen)
│   │   └── {jahr}/
│   ├── gartenbegehung-{jahr}.csv  # Jahresdaten
│   ├── custom.css            # Eigenes CSS
│   └── slider-value.js       # JavaScript (Slider + API-Button)
├── templates/
│   ├── layout.html           # Basis-Layout
│   ├── layout-certificate.html  # PDF-Layout
│   ├── form.html             # Formular
│   ├── preview.html          # Vorschau
│   ├── certificate.html      # Bescheinigung-PDF
│   ├── abmahnung.html        # Abmahnung-PDF
│   └── ...
├── app.py                    # Haupt-App
├── agents.md                 # Diese Datei
└── tests/                    # Tests (18 Tests)
    └── test_items.py
```