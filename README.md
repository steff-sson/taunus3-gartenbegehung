# taunus3-gartenbegehung

Formular zur Dateneingabe einer Gartenbegehung für den Kleingartenverein Taunusgärten Anlage 3 e.V. – inklusive Abmahnung-PDF und automatischer Datenübernahme aus dem Vorjahr.

## Appstack

- **Flask** - Web-Framework
- **WeasyPrint** - PDF-Generierung
- **CSV** - Datenhaltung (jahrweise)
- **Jinja2** - Templates

## Lokale Entwicklung

```bash
# 1. Virtuelle Umgebung erstellen (einmalig)
python -m venv .venv

# 2. Virtuelle Umgebung aktivieren
source .venv/bin/activate

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. App starten
flask run --host=0.0.0.0
```

### Entwicklung

- **Aktivieren:** `source .venv/bin/activate`
- **Deaktivieren:** `deactivate`
- **Neue Pakete:** `pip install <paket>` (danach `pip freeze > requirements.txt`)
- **Tests:** `pytest`
- **LAN-Zugriff:** `flask run --host=0.0.0.0` (sonst nur localhost)

---

## Produktion (Server)

### 1. Server-Voraussetzungen

#### Debian/Ubuntu

```bash
# System-Dependencies für WeasyPrint (einmalig)
sudo apt-get update
sudo apt-get install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# Python 3 installieren (falls nicht vorhanden)
sudo apt-get install -y python3 python3-venv python3-pip
```

#### Arch Linux

```bash
# System-Dependencies für WeasyPrint (einmalig)
sudo pacman -S cairo pango gdk-pixbuf2 libffi shared-mime-info

# Python installieren (falls nicht vorhanden)
sudo pacman -S python python-pip python-venv
```

### 2. App deployen

```bash
# In das App-Verzeichnis wechseln
cd /home/stef/github/taunus3-gartenbegehung

# Code aktualisieren
git pull

# Virtuelle Umgebung erstellen (einmalig)
python -m venv .venv

# Abhängigkeiten installieren
source .venv/bin/activate
pip install -r requirements.txt

# Service neu starten
sudo systemctl restart gartenbegehung
```

### 3. systemd-Service einrichten

Die Service-Vorlage liegt im Repo: `gartenbegehung.service.template`. Platzhalter ersetzen und auf dem Server installieren:

```bash
sudo cp gartenbegehung.service.template /etc/systemd/system/taunus3-gartenbegehung.service
sudo systemctl daemon-reload
sudo systemctl enable --now taunus3-gartenbegehung
```

Prüfen mit:
```bash
sudo systemctl status taunus3-gartenbegehung
sudo journalctl -u taunus3-gartenbegehung -f
```

---

## Ordnerstruktur

```
taunus3-gartenbegehung/
├── .venv/                    # Virtuelle Umgebung
├── requirements.txt          # Python-Abhängigkeiten
├── static/
│   ├── items.csv             # Formular-Konfiguration
│   ├── pdf/                  # Generierte PDFs
│   │   └── 2026/
│   └── gartenbegehung-2026.csv  # Jahresdaten
├── templates/
├── app.py
└── agents.md                 # Entwickler-Doku
```

---

## .env-Datei (einmalig)

Für Produktion einen sicheren Secret-Key setzen:

```bash
# .env erstellen
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
echo "FLASK_ENV=production" >> .env
```

**Wichtig:** `.env` nicht ins Git-Repository committen!

---

## Konfiguration

Die Konfiguration erfolgt über die `.env`-Datei:

- `SECRET_KEY` - Flask Secret Key
- `FLASK_ENV` - development / production

---

## Items anpassen

Alle Formularfelder werden aus `static/items.csv` geladen. Die Datei wird bei jeder Anfrage automatisch neu eingelesen – Änderungen sind sofort wirksam (kein Neustart nötig).

### CSV-Felder (Kurzübersicht)

| Feld | Beschreibung |
|------|---------------|
| id | Eindeutiger Identifier (für HTML name) |
| category | Gruppierung (Basis, Dachbauten, Drittelung, Unkraut, Sonstiges, Abmahnung) |
| type | number, text, select, checkbox, date |
| label | Anzeige im Formular |
| output_text | Text für PDF/CSV (`{value}` wird ersetzt; leer lassen bei Freitextfeldern) |

Ausführliche Dokumentation: `agents.md`

## Tests

```bash
pytest
```

## Weitere Dokumentation

- `agents.md` - Entwickler-Dokumentation