import os
import sys
import csv
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_items():
    items = {'basis': [], 'dachbauten': [], 'drittelung': [], 'unkraut': [], 'sonstiges': []}
    items_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'items.csv')
    with open(items_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = row['category'].lower()
            if cat in items:
                items[cat].append(row)
    return items


def get_item_by_id(items, item_id):
    for category in items.values():
        for item in category:
            if item['id'] == item_id:
                return item
    return None


def format_output(text, value):
    if '{value}' in text and value:
        return text.replace('{value}', str(value))
    return text


def test_items_csv_exists():
    items_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'items.csv')
    assert os.path.isfile(items_path), "items.csv must exist"


def test_load_items():
    items = load_items()
    assert 'basis' in items
    assert 'dachbauten' in items
    assert 'drittelung' in items
    assert 'unkraut' in items
    assert 'sonstiges' in items


def test_items_have_required_fields():
    items = load_items()
    for category in items.values():
        for item in category:
            assert 'id' in item
            assert 'category' in item
            assert 'type' in item
            assert 'label' in item
            assert 'output_text' in item


def test_get_item_by_id():
    items = load_items()
    item = get_item_by_id(items, 'parzelle')
    assert item is not None
    assert item['id'] == 'parzelle'
    assert item['type'] == 'number'


def test_format_output():
    assert format_output("Parzelle: {value}", "42") == "Parzelle: 42"
    assert format_output("Keine Anmerkungen.", "") == "Keine Anmerkungen."
    assert format_output("Strom: {value} kWh", "1234") == "Strom: 1234 kWh"


def test_basis_fields_exist():
    items = load_items()
    basis_ids = [item['id'] for item in items['basis']]
    assert 'parzelle' in basis_ids
    assert 'dach' in basis_ids
    assert 'strom' in basis_ids


def test_dachbauten_options():
    items = load_items()
    dachbauten_ids = [item['id'] for item in items['dachbauten']]
    assert 'dachbauten_keine' in dachbauten_ids
    assert 'dachbauten_ueberschreitet' in dachbauten_ids


def test_sonstiges_checkboxes():
    items = load_items()
    checkbox_items = [item for item in items['sonstiges'] if item['type'] == 'checkbox']
    assert len(checkbox_items) > 0
