from unittest.mock import patch

from cli.main import (
    display_inventory,
    display_inventory_item,
    add_inventory_item,
    update_inventory_item,
    delete_inventory_item,
    search_openfoodfacts,
    add_product_from_openfoodfacts,
)


@patch("cli.main.requests.get")
def test_display_inventory(mock_get, capsys):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [
        {
            "id": 1,
            "barcode": "3017620422003",
            "product_name": "Nutella",
            "brand": "Ferrero",
            "category": "Spread",
            "price": 650,
            "stock": 25,
            "ingredients": "Sugar, palm oil",
        }
    ]

    display_inventory()

    output = capsys.readouterr().out

    assert "Nutella" in output
    assert "Ferrero" in output
    assert "650" in output
    assert "25" in output

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/inventory"
    )


@patch("cli.main.requests.get")
def test_display_inventory_failure(mock_get, capsys):
    mock_get.return_value.status_code = 500

    display_inventory()

    output = capsys.readouterr().out

    assert "Failed to retrieve inventory." in output


@patch("cli.main.requests.get")
def test_display_inventory_item(mock_get, capsys, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "id": 1,
        "barcode": "3017620422003",
        "product_name": "Nutella",
        "brand": "Ferrero",
        "category": "Spread",
        "price": 650,
        "stock": 25,
        "ingredients": "Sugar, palm oil",
    }

    display_inventory_item()

    output = capsys.readouterr().out

    assert "Nutella" in output
    assert "Ferrero" in output
    assert "650" in output


@patch("cli.main.requests.get")
def test_display_inventory_item_not_found(mock_get, capsys, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "999")

    mock_get.return_value.status_code = 404

    display_inventory_item()

    output = capsys.readouterr().out

    assert "Inventory item not found." in output


@patch("cli.main.requests.post")
def test_add_inventory_item(mock_post, capsys, monkeypatch):
    inputs = iter([
        "123456789",
        "Brookside Milk",
        "Brookside",
        "Dairy",
        "Milk",
        "120",
        "30",
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {
        "id": 3,
        "barcode": "123456789",
        "product_name": "Brookside Milk",
        "price": 120,
        "stock": 30,
    }

    add_inventory_item()

    output = capsys.readouterr().out

    assert "Inventory item added successfully." in output

    mock_post.assert_called_once_with(
        "http://127.0.0.1:5000/inventory",
        json={
            "barcode": "123456789",
            "product_name": "Brookside Milk",
            "brand": "Brookside",
            "category": "Dairy",
            "price": 120.0,
            "stock": 30,
            "ingredients": "Milk",
        },
    )


@patch("cli.main.requests.patch")
def test_update_inventory_item(mock_patch, capsys, monkeypatch):
    inputs = iter([
        "1",
        "1",
        "700",
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    mock_patch.return_value.status_code = 200
    mock_patch.return_value.json.return_value = {
        "id": 1,
        "price": 700,
    }

    update_inventory_item()

    output = capsys.readouterr().out

    assert "Inventory item updated successfully." in output

    mock_patch.assert_called_once_with(
        "http://127.0.0.1:5000/inventory/1",
        json={"price": 700.0},
    )


@patch("cli.main.requests.delete")
def test_delete_inventory_item(mock_delete, capsys, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")

    mock_delete.return_value.status_code = 200

    delete_inventory_item()

    output = capsys.readouterr().out

    assert "Inventory item deleted successfully." in output

    mock_delete.assert_called_once_with(
        "http://127.0.0.1:5000/inventory/1"
    )


@patch("cli.main.requests.get")
def test_search_openfoodfacts(mock_get, capsys, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "milk")

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "products": [
            {
                "barcode": "111111111",
                "product_name": "Whole Milk",
                "brand": "Example Brand",
                "category": "Dairy",
            }
        ]
    }

    search_openfoodfacts()

    output = capsys.readouterr().out

    assert "Whole Milk" in output
    assert "111111111" in output
    assert "Example Brand" in output

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/products/search",
        params={"name": "milk"},
    )


@patch("cli.main.requests.get")
@patch("cli.main.requests.post")
def test_add_product_from_openfoodfacts(
    mock_post,
    mock_get,
    capsys,
    monkeypatch
):
    inputs = iter([
        "3017620422003",
        "650",
        "20",
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "barcode": "3017620422003",
        "product_name": "Nutella",
        "brand": "Nutella, Ferrero",
        "category": "Spread",
        "ingredients": "Sugar, palm oil",
    }

    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {
        "id": 3,
        "barcode": "3017620422003",
        "product_name": "Nutella",
        "price": 650,
        "stock": 20,
    }

    add_product_from_openfoodfacts()

    output = capsys.readouterr().out

    assert "Product found:" in output
    assert "Nutella" in output
    assert "Product added to inventory successfully." in output

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/products/barcode/3017620422003"
    )

    mock_post.assert_called_once_with(
        "http://127.0.0.1:5000/inventory/from-api/3017620422003",
        json={
            "price": 650.0,
            "stock": 20,
        },
    )