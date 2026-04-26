# Entwicklung

## Setup

```bash
pipenv install
pipenv install --dev pytest
pipenv run flask run
```

## Server-Setup (einmalig)

### System-Dependencies für WeasyPrint

```bash
sudo apt-get install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

### systemd Service

Der Service läuft bereits unter `/etc/systemd/system/gartenbegehung.service`.

Nach Updates:
```bash
git pull
systemctl restart gartenbegehung
```

## Neue Items hinzufügen

1. `static/items.csv` bearbeiten
2. Neue Zeile hinzufügen (alle Felder)
3. App neu starten

### CSV-Felder

| Feld | Beschreibung |
|------|---------------|
| id | Eindeutiger Identifier (für HTML name) |
| category | Gruppierung (Basis, Dachbauten, Drittelung, Unkraut, Sonstiges) |
| type | number, text, select, checkbox |
| required | true/false |
| label | Anzeige im Formular |
| placeholder | Placeholder-Text |
| output_text | Text für PDF/CSV (`{value}` wird ersetzt) |
| severity | info/warning/error |
| options | Nur für select (kommasepariert) |

## Tests

```bash
pytest
```

## Ordnerstruktur

```
static/
├── items.csv           # Alle Formularfelder
├── pdf/
│   └── 2026/          # PDFs nach Jahr
└── gartenbegehung-2026.csv  # Daten nach Jahr
```

## Umgebungsvariablen

| Variable | Beschreibung |
|----------|---------------|
| SECRET_KEY | Flask Secret Key |
| FLASK_ENV | development / production |
