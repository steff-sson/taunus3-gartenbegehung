# Formular für die Gartenbegehung des Kleingartenvereins Taunusgärten Anlage 3 e.V.

# import needed libraries
from flask import *
from datetime import date
import time
import csv
import os
import base64
import pdfkit
from pdfkit.api import configuration

# Name der Jahresdatenbank
file = 'static/gartenbegehung.csv'

# Optionen zur PDF-Erstellung
wkhtml_path = pdfkit.configuration(wkhtmltopdf = '/usr/bin/wkhtmltopdf')
options = {
    'enable-local-file-access': True,
    'encoding': 'UTF-8'
}

# Routine zum Anzeigen der PDFs
def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                tree['children'].append(dict(name=name))
    return tree



# Beginne Webapp
app = Flask(__name__)
# Setup the secret key and the environment - NOW FROM ENVIRONMENT VARIABLE
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production'),
    ENV=os.environ.get('FLASK_ENV', 'production')
)

@app.route('/name', methods=['GET', 'POST'])
def name():
    if request.method == 'POST':
        if request.form.get('name1'):
            session['name1'] = request.form['name1']
        if request.form.get('name2'):
            session['name2'] = request.form['name2']
        return redirect(url_for('form'))
    return render_template('name.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    # Variablen werden erstellt, bleiben aber leer.
    session['details'] = []
        # Variablen mit Details zur Gartenbewertung
    session['details0'] = 'Der Garten ist insgesamt in einem guten Zustand. Weiter so!'
    session['details1'] = 'Kein Stromzählerstand erfasst. Bitte den Stromzählerstand mit Foto an vorstand@taunus3.de übermitteln.'
    session['details2'] = 'Die Dachfläche ist zu groß. Die Dachfläche muss bei Abgabe des Gartens verkleinert werden.'
    session['details3'] = 'Gärtnerische Nutzung ist nicht erkennbar.'
    session['details4'] = 'In dem Garten lagert Unrat/Müll.'
    session['details5'] = 'Der Garten liegt – in Teilen – brach.'
    session['details6'] = 'Hecke im Garten ist zu hoch (zulässige Höhe: 120cm)'
    session['details7'] = 'Hecke an der Außengrenze ist zu hoch (zulässige Höhe: 180cm)'
    session['details8'] = 'Sichtschutz, der nicht aus Pflanzen besteht, ist verboten.'
    session['details9'] = 'Der Unkrautwuchs hat nachteilige Auswirkungen (z.B. Samenflug) auf die Nachbargärten.'
    session['details10'] = 'Die Gartenwege sind zu stark mit Unkraut bewachsen.'
    session['details11'] = 'Äste, Zweige von Büschen und Bäumen ragen in die Gartenwege bzw. in Nachbargärten.'
    session['details12'] = 'Der Garten enthält kranke Gehölze/Bäume. Diese sind zu entfernen!'
    session['details13'] = 'Die Menge der gelagerten planzlichen Abfälle übersteigt das erlaubte Maß.'
    session['details14'] = 'Kein Kompost vorhanden.'    
    session['details15'] = 'Bitte die Parzellennummer sichtbar anbringen.'    
    if request.method == 'POST':
        # Datum des Eintrages festlegen
        today = date.today()
        datum = today.strftime("%d.%m.%Y")
        # Das aktuelle Datum wird in die Session geschrieben
        session['datum'] = datum
        # Der Wert der Parzellennummer wird direkt in die Session gespeichert.
        session['parzelle'] = request.form['parzelle']
        # Der Wert der Dachfläche wird direkt in die Session geschrieben
        session['dach'] = request.form['dach']
        # Der Wert der Dachfläche wird direkt in die Session geschrieben
        session['strom'] = request.form['strom']
        # Der Wert des Schulnoten-Sliders werden direkt in die Session gespeichert.
        if request.form['zustand'] == '0':
            session['zustand'] = 'ungenügend (0 Punkte)'
        elif request.form['zustand'] == '1':
            session['zustand'] = 'mangelhaft - (1 Punkt)'
        elif request.form['zustand'] == '2':
            session['zustand'] = 'mangelhaft (2 Punkte)'
        elif request.form['zustand'] == '3':
            session['zustand'] = 'mangelhaft + (3 Punkte)'
        elif request.form['zustand'] == '4':
            session['zustand'] = 'ausreichend - (4 Punkte)'
        elif request.form['zustand'] == '5':
            session['zustand'] = 'ausreichend (5 Punkte)'
        elif request.form['zustand'] == '6':
            session['zustand'] = 'ausreichend + (6 Punkte)'
        elif request.form['zustand'] == '7':
            session['zustand'] = 'befriedigend - (7 Punkte)'
        elif request.form['zustand'] == '8':
            session['zustand'] = 'befriedigend (8 Punkte)'
        elif request.form['zustand'] == '9':
            session['zustand'] = 'befriedigend + (9 Punkte)'
        elif request.form['zustand'] == '10':
            session['zustand'] = 'gut - (10 Punkte) – Weiter so!'
        elif request.form['zustand'] == '11':
            session['zustand'] = 'gut (11 Punkte) – Weiter so!'
        elif request.form['zustand'] == '12':
            session['zustand'] = 'gut + (12 Punkte) – Weiter so!'
        elif request.form['zustand'] == '13':
            session['zustand'] = 'sehr gut - (13 Punkte) – Weiter so!'
        elif request.form['zustand'] == '14':
            session['zustand'] = 'sehr gut (14 Punkte) – Weiter so!'                
        else:
            session['zustand'] = 'sehr gut + (15 Punkte) – Weiter so!'

        # Die Werte der Details werden zunächst in eine Variablenliste geschrieben.
        if request.form.get('details0'):
            session['details'].append(session['details0'])
        if request.form.get('details1'):
            session['details'].append(session['details1'])
        if request.form.get('details2'):
            session['details'].append(session['details2'])
        if request.form.get('details3'):
            session['details'].append(session['details3'])
        if request.form.get('details4'):
            session['details'].append(session['details4'])
        if request.form.get('details5'):
            session['details'].append(session['details5'])
        if request.form.get('details6'):
            session['details'].append(session['details6'])
        if request.form.get('details7'):
            session['details'].append(session['details7'])
        if request.form.get('details8'):
            session['details'].append(session['details8'])
        if request.form.get('details9'):
            session['details'].append(session['details9'])
        if request.form.get('details10'):
            session['details'].append(session['details10'])
        if request.form.get('details11'):
            session['details'].append(session['details11'])
        if request.form.get('details12'):
            session['details'].append(session['details12'])
        if request.form.get('details13'):
            session['details'].append(session['details13'])
        if request.form.get('details14'):
            session['details'].append(session['details14'])
        if request.form.get('details15'):
            session['details'].append(session['details15'])                      
        if request.form.get('sonstiges'):
            session['details'].append(request.form.get('sonstiges'))

        return redirect(url_for('preview'))
    return render_template('form.html')

@app.route('/preview', methods=['GET', 'POST'])
def preview():
    if request.method == 'POST':
        # Kopfzeile für Jahresdatenbank
        header = ['Parzelle', 'Dachfläche', 'Strom', 'Zustand (Note)', 'Datum', 'Bewertungsdetails']
        if os.path.isfile(file) == False:
            with open(file, 'w', encoding='UTF8') as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(header)
        daten = [session['parzelle'], session['dach'], session['strom'], session['zustand'], session['datum']]
        detailliste = session['details']
        daten.append(detailliste)
        with open(file, 'a', encoding='UTF8') as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(daten)
        hours = str(time.localtime(time.time()).tm_hour)
        minutes = str(time.localtime(time.time()).tm_min)
        seconds = str(time.localtime(time.time()).tm_sec)
        html = render_template("certificate.html")
        pdfkit.from_string(html, 'static/pdf/Parzelle-' + session['parzelle'] + '---' + hours  + '-' + minutes  + '-' + seconds + '.pdf', options=options, configuration = wkhtml_path)
        return redirect(url_for('done'))
    return render_template('preview.html')

@app.route("/done", methods=['GET'])
def done():
    session.pop('details', default=None)
    session.pop('datum')
    session.pop('dach')
    session.pop('parzelle')
    session.pop('strom')
    return render_template('done.html')

@app.route('/pdfs')
def dirtree():
    path = '/app/static/pdf'  # CHANGED: Docker path instead of local path
    return render_template('pdfs.html', tree=make_tree(path))

@app.route('/')
def index():
    #print(img_logo)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
