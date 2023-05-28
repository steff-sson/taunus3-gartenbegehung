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
file = 'static/2023-gartenbegehung.csv'
# Kopfzeile für Jahresdatenbank
header = ['parzelle', 'Dachfläche', 'Zustand (Note)', 'Datum', 'Bewertungsdetails']
if os.path.isfile(file) == False:
    with open(file, 'w', encoding='UTF8') as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)

# Datum des Eintrages festlegen
today = date.today()
datum = today.strftime("%d.%m.%Y")

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
# Setup the secret key and the environment
app.config.update(SECRET_KEY='osd(99092=36&462134kjKDhuIS_d23',
                  ENV='development')

@app.route('/form', methods=['GET', 'POST'])
def form():
    # Variablen werden erstellt, bleiben aber leer.
    session['details'] = []
        # Variablen mit Details zur Gartenbewertung
    session['details0'] = 'Die Dachfläche ist zu groß.'
    session['details1'] = 'Gärtnerische Nutzung ist nicht erkennbar.'
    session['details2'] = 'In dem Garten lagert Unrat/Müll.'
    session['details3'] = 'Der Garten liegt – in Teilen – brach.'
    session['details4'] = 'Büsche im Bereich der Gartenwege sind zu hoch (Zulässige Höhe: 2,00 bis 2,20m)'
    session['details5'] = 'Der Unkrautwuchs hat nachteilige Auswirkungen (z.B. Samenflug) auf die Nachbargärten.'
    session['details6'] = 'Die Gartenwege sind zu stark mit Unkraut bewachsen.'
    session['details7'] = 'Äste, Zweige von Büschen und Bäumen ragen in die Gartenwege bzw. in Nachbargärten.'
    session['details8'] = 'Der Garten enthält kranke Gehölze/Bäume. Diese sind zu entfernen!'
    session['details9'] = 'Die Menge der gelagerten planzlichen Abfälle übersteigt das erlaubte Maß.'
    session['details10'] = 'Sichtschutz, der nicht aus Pflanzen besteht, ist verboten.'
    if request.method == 'POST':
        # Das aktuelle Datum wird in die Session geschrieben
        session['datum'] = datum
        # Der Wert der Parzellennummer wird direkt in die Session gespeichert.
        session['parzelle'] = request.form['parzelle']
        # Der Wert der Dachfläche wird direkt in die Session geschrieben
        session['dach'] = request.form['dach']
        # Der Wert des Schulnoten-Sliders werden direkt in die Session gespeichert.
        if request.form['zustand'] == '1':
            session['zustand'] =  'sehr gut (1)'
        elif request.form['zustand'] == '2':
            session['zustand'] =  'gut (2)'
        elif request.form['zustand'] == '3':
            session['zustand'] =  'befriedigend (3)'
        elif request.form['zustand'] == '4':
            session['zustand'] =  'ausreichend (4)'
        elif request.form['zustand'] == '5':
            session['zustand'] =  'mangelhaft (5)'
        else:
            session['zustand'] =  'ungenügend (6)'

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
        if request.form.get('sonstiges'):
            session['details'].append(request.form.get('sonstiges'))

        return redirect(url_for('preview'))
    return render_template('form.html')

@app.route('/preview', methods=['GET', 'POST'])
def preview():
    if request.method == 'POST':
        daten = [session['parzelle'], session['dach'], session['zustand'], datum]
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
    session.clear()
    return render_template('done.html')

@app.route('/pdfs')
def dirtree():
    path = '/home/stef/github/taunus3-gartenbegehung/static/pdf'
    return render_template('pdfs.html', tree=make_tree(path))

@app.route('/')
def index():
    #print(img_logo)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
