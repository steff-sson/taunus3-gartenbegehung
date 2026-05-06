import os
import sys
import csv
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def app_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def load_items():
    items = {
        "basis": [],
        "dachbauten": [],
        "drittelung": [],
        "unkraut": [],
        "abmahnung": [],
        "sonstiges": [],
    }
    items_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "static",
        "items.csv",
    )
    with open(items_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = row["category"].lower()
            if cat in items:
                items[cat].append(row)
    return items


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


def test_items_csv_exists():
    items_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "static",
        "items.csv",
    )
    assert os.path.isfile(items_path), "items.csv must exist"


def test_load_items():
    items = load_items()
    assert "basis" in items
    assert "dachbauten" in items
    assert "drittelung" in items
    assert "unkraut" in items
    assert "abmahnung" in items
    assert "sonstiges" in items


def test_items_have_required_fields():
    items = load_items()
    for category in items.values():
        for item in category:
            assert "id" in item
            assert "category" in item
            assert "type" in item
            assert "label" in item
            assert "output_text" in item


def test_get_item_by_id():
    items = load_items()
    item = get_item_by_id(items, "parzelle")
    assert item is not None
    assert item["id"] == "parzelle"
    assert item["type"] == "number"


def test_format_output():
    assert format_output("Parzelle: {value}", "42") == "Parzelle: 42"
    assert format_output("Keine Anmerkungen.", "") == "Keine Anmerkungen."
    assert format_output("Strom: {value} kWh", "1234") == "Strom: 1234 kWh"


def test_basis_fields_exist():
    items = load_items()
    basis_ids = [item["id"] for item in items["basis"]]
    assert "parzelle" in basis_ids
    assert "dach" in basis_ids
    assert "strom" in basis_ids


def test_dachbauten_options():
    items = load_items()
    dachbauten_ids = [item["id"] for item in items["dachbauten"]]
    assert "dachbauten_keine" in dachbauten_ids
    assert "dachbauten_ueberschreitet" in dachbauten_ids


def test_sonstiges_checkboxes():
    items = load_items()
    checkbox_items = [item for item in items["sonstiges"] if item["type"] == "checkbox"]
    assert len(checkbox_items) > 0


def test_abmahnung_item_exists():
    items = load_items()
    assert len(items["abmahnung"]) >= 4
    abmahnung_ids = [item["id"] for item in items["abmahnung"]]
    assert "abmahnung_keine" in abmahnung_ids
    assert "abmahnung_erste" in abmahnung_ids
    assert "abmahnung_zweite" in abmahnung_ids
    assert "abmahnung_dritte" in abmahnung_ids


def test_abmahnung_item_has_frist():
    items = load_items()
    frist_item = get_item_by_id(items, "Frist")
    assert frist_item is not None
    assert frist_item["type"] == "date"
    assert frist_item["required"] == "true"
    assert frist_item["placeholder"]


def test_error_items_identifiable():
    items = load_items()
    error_ids = []
    for category in items.values():
        for item in category:
            if item.get("severity") == "error":
                error_ids.append(item["id"])
    assert "details3" in error_ids
    assert "details9" in error_ids
    assert "abmahnung_zweite" in error_ids
    assert "abmahnung_dritte" in error_ids


def test_abmahnung_form_post_sets_session(app_client):
    with app_client.session_transaction() as sess:
        sess.clear()
        sess["name1"] = "Tester"
    resp = app_client.post(
        "/form",
        data={
            "parzelle": "42",
            "dach": "24",
            "strom": "",
            "dachbauten": "dachbauten_keine",
            "drittelung": "drittelung_keine",
            "unkraut": "unkraut_keine",
            "abmahnung": "abmahnung_erste",
        },
    )
    assert resp.status_code == 302
    with app_client.session_transaction() as sess:
        assert sess["parzelle"] == "42"
        assert sess["dach"] == "24"
        assert sess["abmahnung"] is True
        assert isinstance(sess["abmahnung_items"], list)


def test_abmahnung_form_post_without_abmahnung(app_client):
    with app_client.session_transaction() as sess:
        sess.clear()
        sess["name1"] = "Tester"
    resp = app_client.post(
        "/form",
        data={
            "parzelle": "42",
            "dach": "24",
            "strom": "",
            "dachbauten": "dachbauten_keine",
            "drittelung": "drittelung_keine",
            "unkraut": "unkraut_keine",
        },
    )
    assert resp.status_code == 302
    with app_client.session_transaction() as sess:
        assert sess.get("abmahnung") is False
        assert sess.get("abmahnung_items") == []


def test_abmahnung_form_post_collects_selected_items(app_client):
    with app_client.session_transaction() as sess:
        sess.clear()
        sess["name1"] = "Tester"
    resp = app_client.post(
        "/form",
        data={
            "parzelle": "42",
            "dach": "24",
            "strom": "",
            "dachbauten": "dachbauten_ohne",
            "drittelung": "drittelung_fehlt",
            "unkraut": "unkraut_samen",
            "details3": "on",
            "details0": "on",
            "abmahnung": "abmahnung_erste",
        },
    )
    assert resp.status_code == 302
    with app_client.session_transaction() as sess:
        assert sess["abmahnung"] is True
        assert len(sess["abmahnung_items"]) == 3


def test_abmahnung_frist_parsed(app_client):
    with app_client.session_transaction() as sess:
        sess.clear()
        sess["name1"] = "Tester"
    resp = app_client.post(
        "/form",
        data={
            "parzelle": "42",
            "dach": "24",
            "strom": "",
            "dachbauten": "dachbauten_keine",
            "drittelung": "drittelung_keine",
            "unkraut": "unkraut_keine",
            "Frist": "30.05.26",
            "abmahnung": "abmahnung_erste",
        },
    )
    assert resp.status_code == 302
    with app_client.session_transaction() as sess:
        assert sess.get("frist") == "30.05.26"


def test_abmahnung_preview_generates_pdf(app_client):
    with app_client.session_transaction() as sess:
        sess.clear()
        sess["name1"] = "Tester"
        sess["parzelle"] = "99"
        sess["dach"] = "20"
        sess["strom"] = ""
        sess["dachbauten"] = "Keine Anmerkungen."
        sess["drittelung"] = "Keine Anmerkungen."
        sess["unkraut"] = "Keine Anmerkungen."
        sess["details"] = []
        sess["jahr"] = "2026"
        sess["datum"] = "06.05.2026"
        sess["abmahnung"] = True
        sess["abmahnung_items"] = ["Testverstoss"]
        sess["frist"] = "31.07.2026"
    resp = app_client.post("/preview")
    assert resp.status_code == 302
    import glob
    import time

    time.sleep(0.1)
    pdf_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "static",
        "pdf",
        "2026",
    )
    pdfs = glob.glob(os.path.join(pdf_dir, "*Abmahnung*.pdf"))
    assert len(pdfs) >= 1
    for p in pdfs:
        os.remove(p)


def test_api_last_dach_no_parzelle(app_client):
    resp = app_client.get("/api/last-dach")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_api_last_dach_missing(app_client):
    resp = app_client.get("/api/last-dach?parzelle=99999")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data
