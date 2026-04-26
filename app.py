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
        session["drittelung"] = get_output_text(
            items, request.form.get("drittelung"), ""
        )
        session["unkraut"] = get_output_text(items, request.form.get("unkraut"), "")

        for item in items["sonstiges"]:
            item_id = item["id"]
            if request.form.get(item_id):
                output = get_output_text(items, item_id, "")
                if output:
                    session["details"].append(output)

        weiteres = request.form.get("weiteres", "").strip()
        if weiteres:
            output = get_output_text(items, "weiteres", weiteres)
            session["details"].append(output)

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
            "Datum",
            "Parzelle",
            "Dach",
            "Strom",
            "Dachbauten",
            "Drittelung",
            "Unkraut",
            "Details",
        ]
        if not os.path.isfile(csv_file):
            with open(csv_file, "w", encoding="UTF8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(header)

        daten = [
            session.get("datum", ""),
            session.get("parzelle", ""),
            session.get("dach", ""),
            session.get("strom", ""),
            session.get("dachbauten", ""),
            session.get("drittelung", ""),
            session.get("unkraut", ""),
            session.get("details", []),
        ]

        with open(csv_file, "a", encoding="UTF8") as f:
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

        return redirect(url_for("done"))

    return render_template("preview.html")


@app.route("/done", methods=["GET"])
def done():
    for key in [
        "details",
        "datum",
        "dach",
        "dachbauten",
        "unkraut",
        "drittelung",
        "parzelle",
        "strom",
        "jahr",
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


if __name__ == "__main__":
    app.run(host="0.0.0.0")
