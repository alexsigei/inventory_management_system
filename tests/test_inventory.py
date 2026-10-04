import pytest

from app import app
from storage import inventory, initial_inventory


@pytest.fixture
def client():
    inventory.clear()
    inventory.extend(item.copy() for item in initial_inventory)

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_get_all_inventory(client):
    response = client.get("/inventory")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    assert data[0]["product_name"] == "Nutella"


def test_get_single_inventory_item(client):
    response = client.get("/inventory/1")

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == 1
    assert data["product_name"] == "Nutella"


def test_get_nonexistent_item(client):
    response = client.get("/inventory/999")

    assert response.status_code == 404

    assert response.get_json()["error"] == "Inventory item not found"


def test_create_inventory_item(client):
    new_item = {
        "barcode": "123456789",
        "product_name": "Brookside Milk",
        "brand": "Brookside",
        "category": "Dairy",
        "price": 120,
        "stock": 30,
        "ingredients": "Milk"
    }

    response = client.post("/inventory", json=new_item)

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == 3
    assert data["product_name"] == "Brookside Milk"
    assert data["price"] == 120


def test_create_inventory_item_missing_fields(client):
    new_item = {
        "product_name": "Brookside Milk"
    }

    response = client.post("/inventory", json=new_item)

    assert response.status_code == 400

    data = response.get_json()

    assert "Missing required fields" in data["error"]


def test_update_inventory_item(client):
    updated_data = {
        "price": 700,
        "stock": 15
    }

    response = client.patch(
        "/inventory/1",
        json=updated_data
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["price"] == 700
    assert data["stock"] == 15

    # Ensure other fields remain unchanged.
    assert data["product_name"] == "Nutella"


def test_update_nonexistent_item(client):
    response = client.patch(
        "/inventory/999",
        json={"price": 500}
    )

    assert response.status_code == 404


def test_delete_inventory_item(client):
    response = client.delete("/inventory/1")

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Inventory item deleted successfully"

    # Verify that the item was actually removed.
    assert not any(item["id"] == 1 for item in inventory)


def test_delete_nonexistent_item(client):
    response = client.delete("/inventory/999")

    assert response.status_code == 404