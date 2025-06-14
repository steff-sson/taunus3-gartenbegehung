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
# Setup the secret key and the environment
app.config.update(SECRET_KEY='osd(99092=36&462134kjKDhuIS_d23',
                  ENV='development')

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
    # Variable wird erstellt, bleibt aber leer.
    # Variablen mit Details zur Gartenbewertung
    session['details'] = []
    # Elemente der Variable werden erstellt
    session['details0'] = 'Der Garten ist insgesamt in einem guten Zustand. Weiter so!'
    session['details1'] = 'Kein Stromzählerstand erfasst. Bitte den Stromzählerstand bis zum 27.07.2025 mit Foto an vorstand@taunus3.de übermitteln.'
    session['details2'] = 'Kein Kompost vorhanden. Bitte bis zum 27.07.2025 einen Kompost anlegen.'  
    session['details3'] = 'In dem Garten lagert Unrat/Müll. Bitte bis zum 27.07.2025 entfernen.'
    session['details4'] = 'Sichtschutz, der nicht aus Pflanzen besteht, ist verboten. Bitte bis zum 27.07.2025 entfernen.'
    session['details5'] = 'Hecke im Garten ist zu hoch (zulässige Höhe: 120cm). Bitte bis zum 27.07.2025 kürzen.'
    session['details6'] = 'Hecke an der Außengrenze ist zu hoch (zulässige Höhe: 180cm). Bitte bis zum 27.07.2025 kürzen.'
    session['details7'] = 'Sichtschutz, der nicht aus Pflanzen besteht, ist verboten.'
    session['details8'] = 'Äste, Zweige von Büschen und Bäumen ragen in die Gartenwege bzw. in Nachbargärten. Bitte bis zum 27.07.2025 entfernen.'
    session['details9'] = 'Der Garten enthält kranke Gehölze/Bäume. Bitte bis zum 27.07.2025 entfernen.'
    session['details10'] = 'Bitte die Parzellennummer sichtbar anbringen.' 
    #
    # Variablen werden nun in die Session geschrieben
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
        # Der Wert 'Dachbauten' wird in die Session geschrieben
        session['dachbauten'] = request.form['dachbauten']
        #
        if request.form['dachbauten'] == 'keine':
            session['dachbauten'] = 'Keine Anmerkungen. Bitte beachte, dass neue An- und Ausbauten, auch Vordachanbringung bzw. Vergrößerung, einer Zustimmung durch den Vorstand bedürfen.'
        elif request.form['dachbauten'] == 'ueberschreitet':
            session['dachbauten'] = 'Die Laube/überdachte Fläche überschreitet die erlaubten 24 m². Das bedeutet: Keine neuen An- und Ausbauten, auch nicht Vordachanbringung bzw. Vergrößerung erlaubt! Bei Gartenrückgabe muss ggf. mit Rückbau auf das erlaubte Maß von 24m² gerechnet werden. Bei Fragen kannst Du Dich an den Vorstand wenden.'   
        elif request.form['dachbauten'] == 'ueberschreitet_zustimmung':
            session['dachbauten'] = 'Die Laube/überdachte Fläche wurde ohne Zustimmung des Vorstandes vergrößert und überschreitet die erlaubten 24 m². Bitte bis zum 27.07.2025 auf das erlaubte Maß von 24 m² zurückbauen/die neue überdachte Fläche mit einer abnehmbaren Bedeckung bedecken und mit Fotos dem Vorstand (vorstand@taunus3.de) nachweisen. Bei Nichteinhaltung dieser Frist ist eine Abmahnung durch den Vorstand vorgesehen. Bei Fragen kannst Du Dich an den Vorstand wenden.'   
        else:
            session['dachbauten'] = 'Die Laube/überdachte Fläche wurde ohne Zustimmung des Vorstandes vergrößert und überschreitet die erlaubten 24 m². Wir mahnen Sie ab und setzen Ihnen eine Frist bis zum 27.07.2025, um den die Laube/überdachte Fläche auf das erlaubte Maß von 24 m² zurückzubauen.'
        #
        # Der Wert 'Drittelung' wird in die Session geschrieben
        session['drittelung'] = request.form['drittelung']
        #
        if request.form['drittelung'] == 'keine':
            session['drittelung'] = 'Keine Anmerkungen. Bitte achte auch weiterhin auf die Einhaltung der Drittelung (ein Drittel der Gartenfläche muss für den Anbau genutzt werden).'
        elif request.form['drittelung'] == 'drittelung':
            session['drittelung'] = 'Der Garten weist keine Drittelung auf (ein Drittel der Gartenfläche muss für den Anbau genutzt werden). Um einer Abmahnung vorzubeugen bitte bis zum 27.07.2025 die Anbaufläche auf ein Drittel vergrößern (z.B. durch die Umwandlung von Rasenfläche in Beete) und mit Fotos dem Vorstand (vorstand@taunus3.de) nachweisen.'   
        else:
            session['drittelung'] = 'Der Garten weist keine kleingärtnerische Nutzung auf. Es ist insbesondere keine Drittelung erkennbar (ein Drittel der Gartenfläche muss für den Anbau genutzt werden) / Der Garten wirkt verwildert oder verwahrlost. Wir mahnen Sie ab und setzen Ihnen eine Frist bis zum 27.07.2025, um den negativen Zustand zu beheben.'
        #
        # Der Wert 'Unkraut' wird in die Session geschrieben
        session['unkraut'] = request.form['unkraut']
        #
        if request.form['unkraut'] == 'keine':
            session['unkraut'] = 'Keine Anmerkungen. Bitte achte auch weiterhin darauf, Unkraut mit Samenflug sowie invasive Pflanzen, die sich negativ auf Nachbargarten ausbreiten, regelmäßig zu entfernen.'
        elif request.form['unkraut'] == 'unkraut':
            session['unkraut'] = 'Der Garten weist Unkraut mit Samenflug bzw. invasive Pflanzen, die sich negativ auf Nachbargarten ausbreiten, auf. Um einer Abmahnung vorzubeugen bitte bis 27.07.2025 Unkraut mit Samenflug bzw. invasive Pflanzen entfernen und dies mit Fotos dem Vorstand (vorstand@taunus3.de) nachweisen.'   
        else:
            session['unkraut'] = 'Der Garten weist Unkraut mit Samenflug bzw. invasive Pflanzen, die sich negativ auf Nachbargarten ausbreiten, auf. Wir mahnen Sie ab und setzen Ihnen eine Frist bis zum 27.07.2025, um den negativen Zustand zu beheben.'
        #    
        # Schulnoten-Slider wurde 2025 entfernt, da Schulnoten zu subjektiv und ggf. irrefuehrend sind!
        #
        # Der Wert des Schulnoten-Sliders werden direkt in die Session gespeichert.
        """
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
        """
        # ENDE des Schulnoten-Sliders
        #
        # Die Werte der Details und Verstoesse werden zunächst in eine Variablenliste geschrieben.
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
        return redirect(url_for('preview'))
    return render_template('form.html')

@app.route('/preview', methods=['GET', 'POST'])
def preview():
    if request.method == 'POST':
        # Kopfzeile für Jahresdatenbank
        header = ['Datum', 'Parzelle', 'Dach', 'Strom', 'Dachbauten', 'Drittelung', 'Unkraut','Details']
        if os.path.isfile(file) == False:
            with open(file, 'w', encoding='UTF8') as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(header)
        daten = [session['datum'], session['parzelle'], session['dach'], session['strom'], session['dachbauten'], session['drittelung'], session['unkraut']]
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
    session.pop('verstoss', default=None)
    session.pop('datum')
    session.pop('dach')
    session.pop('parzelle')
    session.pop('strom')
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
