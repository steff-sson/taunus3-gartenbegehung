from flask import *
from datetime import date
import csv
import os
import time
from weasyprint import HTML
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-fallback-key")
app.config["FLASK_RUN_HOST"] = "0.0.0.0"

_items_cache = {"items": None, "mtime": None}


def load_items():
    items_path = os.path.join(os.path.dirname(__file__), "static", "items.csv")
    current_mtime = os.path.getmtime(items_path)

    if _items_cache["items"] is None or _items_cache["mtime"] < current_mtime:
        items = {
            "basis": [],
            "dachbauten": [],
            "drittelung": [],
            "unkraut": [],
            "abmahnung": [],
            "sonstiges": [],
        }
        with open(items_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cat = row["category"].lower()
                if cat in items:
                    items[cat].append(row)
        _items_cache["items"] = items
        _items_cache["mtime"] = current_mtime

    return _items_cache["items"]


def clear_items_cache():
    global _items_cache
    _items_cache = {"items": None, "mtime": None}


def get_item_by_id(items, item_id):
    for category in items.values():
        for item in category:
            if item["id"] == item_id:
                return item
    return None


def format_output(text, value):
    if "{value}" in text and value:
        return text.replace("{value}", str(value))
    return text


def get_output_text(items, item_id, value):
    item = get_item_by_id(items, item_id)
    if item:
        return format_output(item["output_text"], value)
    return ""


def make_tree(path, base_path=""):
    rel_path = os.path.basename(path)
    tree = dict(name=rel_path, path=base_path + "/" + rel_path, children=[])
    try:
        lst = os.listdir(path)
    except OSError:
        pass
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree["children"].append(make_tree(fn, tree["path"]))
            else:
                tree["children"].append(dict(name=name, path=tree["path"] + "/" + name))
    return tree


@app.route("/name", methods=["GET", "POST"])
def name():
    if request.method == "POST":
        if request.form.get("name1"):
            session["name1"] = request.form["name1"]
        if request.form.get("name2"):
            session["name2"] = request.form["name2"]
        return redirect(url_for("form"))
    return render_template("name.html")


@app.route("/form", methods=["GET", "POST"])
def form():
    items = load_items()

    if request.method == "POST":
        session["details"] = []
        today = date.today()
        jahr = today.strftime("%Y")
        datum = today.strftime("%d.%m.%Y")
        session["datum"] = datum
        session["jahr"] = jahr

        session["parzelle"] = request.form.get("parzelle")
        session["dach"] = request.form.get("dach")
        session["strom"] = request.form.get("strom", "")

        session["dachbauten"] = get_output_text(
            items, request.form.get("dachbauten"), ""
        )
        session["dachbauten_id"] = request.form.get("dachbauten", "")
        session["drittelung"] = get_output_text(
            items, request.form.get("drittelung"), ""
        )
        session["drittelung_id"] = request.form.get("drittelung", "")
        session["unkraut"] = get_output_text(items, request.form.get("unkraut"), "")
        session["unkraut_id"] = request.form.get("unkraut", "")

        session["frist"] = request.form.get("Frist", "") if "frist_aktiv" in request.form else ""

        abmahnung_select = request.form.get("abmahnung", "abmahnung_keine")
        session["abmahnung"] = abmahnung_select != "abmahnung_keine"
        if session["abmahnung"]:
            session["abmahnung_level"] = abmahnung_select

        session["abmahnung_items"] = []

        if session["abmahnung"]:
            for field in ["drittelung", "unkraut"]:
                item_id = request.form.get(field)
                item = get_item_by_id(items, item_id)
                if item and item.get("output_text"):
                    session["abmahnung_items"].append(item["output_text"])

        ABMAHNUNG_EXCLUDE = {"details0", "details1", "Frist"}

        for item in items["sonstiges"]:
            item_id = item["id"]
            if request.form.get(item_id):
                output = get_output_text(items, item_id, "")
                if output:
                    session["details"].append(output)
                    if session["abmahnung"] and item_id not in ABMAHNUNG_EXCLUDE:
                        session["abmahnung_items"].append(output)

        weiteres = request.form.get("weiteres", "").strip()
        if weiteres:
            session["details"].append(weiteres)
            if session["abmahnung"]:
                session["abmahnung_items"].append(weiteres)

        return redirect(url_for("preview"))

    return render_template("form.html", items=items)


@app.route("/preview", methods=["GET", "POST"])
def preview():
    if request.method == "POST":
        jahr = session.get("jahr", str(date.today().year))
        csv_file = os.path.join(
            os.path.dirname(__file__), "static", f"gartenbegehung-{jahr}.csv"
        )

        header = [
            "Datum", "Parzelle", "Dach", "Strom",
            "Dachbauten", "Dachbauten_Text",
            "Drittelung", "Drittelung_Text",
            "Unkraut", "Unkraut_Text",
            "Details",
            "Abmahnung", "Abmahnung_Level", "Frist",
        ]

        if os.path.isfile(csv_file):
            with open(csv_file, "r", encoding="utf-8") as f:
                existing_header = f.readline().strip()
            if existing_header != ";".join(header):
                with open(csv_file, "r", encoding="utf-8") as f:
                    reader = csv.reader(f, delimiter=";")
                    next(reader, None)
                    old_rows = list(reader)
                with open(csv_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f, delimiter=";")
                    writer.writerow(header)
                    MAPPING = {0:0, 1:1, 2:2, 3:3, 4:5, 5:7, 6:9, 7:10}
                    for old_row in old_rows:
                        new_row = [""] * len(header)
                        if len(old_row) <= 8:
                            for old_i, new_i in MAPPING.items():
                                if old_i < len(old_row):
                                    new_row[new_i] = old_row[old_i]
                        else:
                            for i in range(min(len(old_row), len(header))):
                                new_row[i] = old_row[i]
                        writer.writerow(new_row)
        else:
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(header)

        daten = [
            session.get("datum", ""),
            session.get("parzelle", ""),
            session.get("dach", ""),
            session.get("strom", ""),
            session.get("dachbauten_id", ""),
            session.get("dachbauten", ""),
            session.get("drittelung_id", ""),
            session.get("drittelung", ""),
            session.get("unkraut_id", ""),
            session.get("unkraut", ""),
            session.get("details", []),
            session.get("abmahnung", ""),
            session.get("abmahnung_level", ""),
            session.get("frist", ""),
        ]

        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(daten)

        hours = str(time.localtime(time.time()).tm_hour)
        minutes = str(time.localtime(time.time()).tm_min)
        seconds = str(time.localtime(time.time()).tm_sec)

        pdf_dir = os.path.join(os.path.dirname(__file__), "static", "pdf", jahr)
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_name = f"{jahr}-Parzelle-{session.get('parzelle', 'x')}---{hours}-{minutes}-{seconds}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_name)

        html = render_template("certificate.html")
        HTML(string=html).write_pdf(pdf_path)

        if session.get("abmahnung"):
            abmahnung_name = f"{jahr}-Parzelle-{session.get('parzelle', 'x')}---{hours}-{minutes}-{seconds}-Abmahnung.pdf"
            abmahnung_path = os.path.join(pdf_dir, abmahnung_name)
            abmahnung_html = render_template("abmahnung.html")
            HTML(string=abmahnung_html).write_pdf(abmahnung_path)

        return redirect(url_for("done"))

    return render_template("preview.html")


@app.route("/done", methods=["GET"])
def done():
    for key in [
        "details",
        "datum",
        "dach",
        "dachbauten",
        "dachbauten_id",
        "drittelung_id",
        "unkraut_id",
        "unkraut",
        "drittelung",
        "parzelle",
        "strom",
        "jahr",
        "abmahnung",
        "abmahnung_items",
        "abmahnung_level",
        "frist",
    ]:
        session.pop(key, None)
    return render_template("done.html")


@app.route("/pdfs")
def dirtree():
    path = os.path.join(os.path.dirname(__file__), "static", "pdf")
    return render_template("pdfs.html", tree=make_tree(path))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/last-dach")
def last_dach():
    parzelle = request.args.get("parzelle", "")
    if not parzelle:
        return {"error": "Keine Parzellennummer angegeben"}, 400

    today_year = str(date.today().year)
    years_to_try = [today_year, str(int(today_year) - 1)]

    for jahr in years_to_try:
        csv_file = os.path.join(
            os.path.dirname(__file__), "static", f"gartenbegehung-{jahr}.csv"
        )
        if not os.path.isfile(csv_file):
            continue
        last_dach = None
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=";")
            next(reader, None)
            for row in reader:
                if len(row) >= 3 and row[1] == parzelle:
                    last_dach = row[2]
        if last_dach is not None:
            return {"dach": last_dach, "jahr": jahr}

    return {"info": "Keine Daten vorhanden"}, 200


@app.route("/api/clean")
def clean_csv():
    jahr = request.args.get("jahr", str(date.today().year))
    csv_file = os.path.join(
        os.path.dirname(__file__), "static", f"gartenbegehung-{jahr}.csv"
    )
    if not os.path.isfile(csv_file):
        return {"error": f"Keine CSV für {jahr} vorhanden"}, 404

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        rows = list(reader)

    seen = {}
    for i, row in enumerate(rows):
        if len(row) >= 2:
            seen[row[1]] = i

    keep_indices = set(seen.values())
    deleted = len(rows) - len(keep_indices)

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        for i, row in enumerate(rows):
            if i in keep_indices:
                writer.writerow(row)

    return {"deleted": deleted, "kept": len(keep_indices)}


@app.route("/api/generate-all")
def generate_all():
    jahr = request.args.get("jahr", str(date.today().year))
    csv_file = os.path.join(
        os.path.dirname(__file__), "static", f"gartenbegehung-{jahr}.csv"
    )
    csv_only = request.args.get("csv-only", "").lower() in ("true", "1")

    if not os.path.isfile(csv_file):
        return {"error": f"Keine CSV für {jahr} vorhanden"}, 404

    items = load_items()
    text_to_id = {}
    for cat_items in items.values():
        for item in cat_items:
            ot = item.get("output_text", "")
            if ot:
                text_to_id[ot] = item["id"]

    pdf_dir = os.path.join(os.path.dirname(__file__), "static", "pdf", jahr)
    os.makedirs(pdf_dir, exist_ok=True)

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f, delimiter=";"))

    updated_rows = []
    count_cert = 0
    count_abm = 0

    import ast

    for i, row in enumerate(reader):
        row = dict(row)

        for id_col, text_col in [
            ("Dachbauten", "Dachbauten_Text"),
            ("Drittelung", "Drittelung_Text"),
            ("Unkraut", "Unkraut_Text"),
        ]:
            item_id = row.get(id_col, "")
            if not item_id:
                old_text = row.get(text_col, "")
                item_id = text_to_id.get(old_text, "")
                if not item_id and len(old_text) > 20:
                    for full_text, candidate_id in text_to_id.items():
                        if old_text in full_text or full_text in old_text:
                            item_id = candidate_id
                            break
                if item_id:
                    row[id_col] = item_id
            if item_id:
                new_text = get_output_text(items, item_id, "")
                if new_text:
                    row[text_col] = new_text

        updated_rows.append(row)

        if csv_only:
            continue

        session["datum"] = row.get("Datum", "")
        session["parzelle"] = row.get("Parzelle", "")
        session["dach"] = row.get("Dach", "")
        session["strom"] = row.get("Strom", "")
        session["dachbauten"] = row.get("Dachbauten_Text", "")
        session["drittelung"] = row.get("Drittelung_Text", "")
        session["unkraut"] = row.get("Unkraut_Text", "")

        try:
            session["details"] = ast.literal_eval(row.get("Details", "[]"))
        except (ValueError, SyntaxError):
            session["details"] = []

        session["frist"] = row.get("Frist", "")

        pdf_name = f"{jahr}-Parzelle-{row.get('Parzelle', 'x')}---{str(i).zfill(3)}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_name)
        html = render_template("certificate.html")
        HTML(string=html).write_pdf(pdf_path)
        count_cert += 1

        abm_str = row.get("Abmahnung", "")
        if abm_str.lower() in ("true", "ja", "1"):
            session["abmahnung"] = True
            session["abmahnung_level"] = row.get("Abmahnung_Level", "abmahnung_erste")

            abm_items = []
            for detail in session["details"]:
                abm_items.append(detail)
            for text in [
                row.get("Drittelung_Text", ""),
                row.get("Unkraut_Text", ""),
            ]:
                if text and "Keine Anmerkungen" not in text:
                    abm_items.append(text)
            session["abmahnung_items"] = abm_items

            abm_pdf_name = f"{jahr}-Parzelle-{row.get('Parzelle', 'x')}---{str(i).zfill(3)}-Abmahnung.pdf"
            abm_pdf_path = os.path.join(pdf_dir, abm_pdf_name)
            abm_html = render_template("abmahnung.html")
            HTML(string=abm_html).write_pdf(abm_pdf_path)
            count_abm += 1

        session.clear()
        session["name1"] = "Batch"

    if updated_rows:
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, delimiter=";", fieldnames=updated_rows[0].keys())
            writer.writeheader()
            writer.writerows(updated_rows)

    result = {"certificates": count_cert, "abmahnungen": count_abm}
    if csv_only:
        result["csv_updated"] = True
        result["rows"] = len(updated_rows)
    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0")
