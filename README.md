# taunus3-gartenbegehung

Formular zur Dateneingabe einer Gartenbegehung für den Kleingartenverein Taunusgärten Anlage 3 e.V.

## Appstack

- **Flask** - Web-Framework
- **WeasyPrint** - PDF-Generierung
- **CSV** - Datenhaltung (jahrweise)
- **Jinja2** - Templates

## Hinweise

- Die notwendigen Python-Module werden in einer virtuellen Umgebung gepflegt (VENV).
- Zur einfacheren Verwaltung der virtuellen Umgebung und der darin installierten Module wird pipenv verwendet.

## Installation

```bash
pipenv install
```

### System-Dependencies (WeasyPrint)

```bash
sudo apt-get install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

## Entwicklung

```bash
pipenv run flask run
```

## Produktion

Der Service läuft via systemd:

```bash
systemctl restart gartenbegehung
```

Nach einem `git pull` muss der Service neu gestartet werden.

## Konfiguration

Die Konfiguration erfolgt über die `.env`-Datei:

- `SECRET_KEY` - Flask Secret Key
- `FLASK_ENV` - development / production

## Items anpassen

Alle Formularfelder werden aus `static/items.csv` geladen. Siehe `agents.md` für Details.

## Tests

```bash
pytest
```
