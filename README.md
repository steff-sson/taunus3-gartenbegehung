# Taunusgärten Anlage 3 - Gartenbegehung

Formular zur Dateneingabe einer Gartenbegehung mit PDF-Export.

---

## ⚠️ WICHTIGER HINWEIS: wkhtmltopdf ist DEPRECATED!

**ACHTUNG:** Dieses Projekt nutzt aktuell `wkhtmltopdf` für die PDF-Generierung. 
Dieses Tool wurde **offiziell eingestellt** (Stand: Dezember 2024) und gilt als **Sicherheitsrisiko**.

### Status:
- ❌ Keine Updates mehr
- ❌ Als "discontinued upstream" markiert
- ❌ Sicherheitslücken werden nicht mehr gepatcht
- ⚠️ Funktioniert aktuell noch, aber...

### Migration geplant:
Eine Migration zu **WeasyPrint** ist in Planung. Siehe Branch `weasyprint-migration` (wird erstellt).

**Referenzen:**
- [CiviCRM Security Advisory](https://civicrm.org/advisory/civi-psa-2024-01-wkhtmltopdf-eol)
- [GitHub Issue: Homebrew disabled wkhtmltopdf](https://github.com/frappe/frappe/issues/29064)

---

## 🚀 Quick Start

### 1. Voraussetzungen
- Docker & Docker Compose installiert
- Ein `frontend` Docker-Netzwerk erstellt:
  ```bash
  docker network create frontend
  ```

### 2. Konfiguration

#### a) SECRET_KEY erstellen
```bash
# Secret Key generieren
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

#### b) `.env` Datei erstellen
```bash
cp .env.example .env
# Dann .env bearbeiten und SECRET_KEY eintragen!
```

**WICHTIG:** Der `SECRET_KEY` muss VOR dem Deployment geändert werden!

### 3. Image bauen
```bash
docker build -t DEIN-DOCKERHUB-USERNAME/gartenbegehung:latest .
```

### 4. docker-compose.yml anpassen
```yaml
# Zeile 3 ändern:
image: DEIN-DOCKERHUB-USERNAME/gartenbegehung:latest
```

### 5. Starten
```bash
docker-compose up -d
```

### 6. Zugriff
- **Lokal:** http://localhost:5001
- **Mit Reverse Proxy:** siehe NGINX-Konfiguration unten

---

## 📂 Persistente Daten

Alle Daten werden in `./data/` gespeichert:
- `./data/gartenbegehung.csv` - Bewertungsdaten
- `./data/pdf/` - Generierte PDFs

**Volume-Mapping:**
```yaml
volumes:
  - ./data:/app/static
```

---

## 🌐 Reverse Proxy Setup

### Option 1: SWAG (empfohlen)
```bash
# 1. Konfiguration kopieren
cp gartenbegehung.swag.conf.example /path/to/swag/config/nginx/proxy-confs/gartenbegehung.subdomain.conf

# 2. SWAG neu starten
docker restart swag
```

### Option 2: Standalone NGINX
```bash
# 1. Konfiguration kopieren
cp gartenbegehung.nginx.conf.example /etc/nginx/sites-available/gartenbegehung

# 2. Anpassen (server_name, SSL-Pfade)
nano /etc/nginx/sites-available/gartenbegehung

# 3. Aktivieren
ln -s /etc/nginx/sites-available/gartenbegehung /etc/nginx/sites-enabled/

# 4. Testen & neu laden
nginx -t && systemctl reload nginx
```

---

## 🛠️ Entwicklung

### Lokale Entwicklung (ohne Docker)
```bash
# 1. Virtual Environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# 2. Dependencies
pip install -r requirements.txt

# 3. wkhtmltopdf installieren (System-abhängig)
# Ubuntu/Debian:
sudo apt-get install wkhtmltopdf

# macOS:
brew install wkhtmltopdf

# 4. Starten
python app.py
```

### Mit pipenv (wie ursprünglich)
```bash
pipenv install
pipenv shell
python app.py
```

---

## 📋 Technische Details

### Stack
- **Framework:** Flask 3.0.0
- **WSGI Server:** Gunicorn
- **PDF-Engine:** wkhtmltopdf 0.12.6 (⚠️ deprecated!)
- **Python:** 3.11
- **Port:** 5001

### Umgebungsvariablen
| Variable | Beschreibung | Default | Erforderlich |
|----------|--------------|---------|--------------|
| `SECRET_KEY` | Flask Secret Key | - | ✅ JA |
| `FLASK_ENV` | Environment | `production` | ❌ |
| `TZ` | Timezone | `Europe/Berlin` | ❌ |
| `PUID` | User ID | `1000` | ❌ |
| `PGID` | Group ID | `1000` | ❌ |

---

## 🔒 Sicherheit

### SECRET_KEY
**NIEMALS** den Default-Key aus `app.py` in Produktion nutzen!

```bash
# Sicheren Key generieren:
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

### wkhtmltopdf Sicherheitsrisiken
- Keine aktive Wartung
- Bekannte Sicherheitslücken (CVEs)
- **Empfehlung:** Migration zu WeasyPrint planen

---

## 🐛 Troubleshooting

### PDFs werden nicht erstellt
```bash
# Container-Logs prüfen
docker logs gartenbegehung

# In Container schauen
docker exec -it gartenbegehung bash
ls -la /app/static/pdf/
```

### Fehler: "No module named 'pdfkit'"
```bash
# Image neu bauen
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Permissions-Fehler
```bash
# Host-Verzeichnis Rechte prüfen
chmod -R 755 ./data/
chown -R 1000:1000 ./data/
```

---

## 📦 Deployment

### Production Checklist
- [ ] `.env` Datei mit eigenem `SECRET_KEY` erstellt
- [ ] `docker-compose.yml`: Image-Name angepasst
- [ ] `frontend` Netzwerk erstellt
- [ ] Volume-Pfad `./data/` existiert
- [ ] Reverse Proxy konfiguriert
- [ ] SSL-Zertifikat eingerichtet
- [ ] Backup-Strategie für `./data/` definiert

### Updates
```bash
# Image aktualisieren
docker pull DEIN-DOCKERHUB-USERNAME/gartenbegehung:latest

# Container neu starten
docker-compose down
docker-compose up -d
```

---

## 📜 Lizenz

GNU General Public License v3.0 (siehe `LICENSE`)

---

## 🤝 Kontakt

Taunusgärten Anlage 3 e.V.  
vorstand@taunus3.de

---

## 🔄 Roadmap

- [ ] **Migration zu WeasyPrint** (höchste Priorität!)
- [ ] Authentifizierung/Login-System
- [ ] Export als Excel/CSV
- [ ] Responsive Design verbessern
- [ ] Tests schreiben

---

**Stand:** Dezember 2024  
**Version:** 1.0.0-wkhtmltopdf (deprecated)
