import pytest

from app import app
from storage import inventory, initial_inventory

from unittest.mock import patch


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


@patch("app.get_product_by_barcode")
def test_barcode_route(mock_get_product, client):
    mock_get_product.return_value = {
        "barcode": "123456789",
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "category": "Plant-based milk",
        "ingredients": "Water, almonds, sugar",
    }

    response = client.get("/products/barcode/123456789")

    assert response.status_code == 200

    data = response.get_json()

    assert data["barcode"] == "123456789"
    assert data["product_name"] == "Organic Almond Milk"
    assert data["brand"] == "Silk"

    mock_get_product.assert_called_once_with("123456789")


@patch("app.get_product_by_barcode")
def test_barcode_route_not_found(mock_get_product, client):
    mock_get_product.return_value = None

    response = client.get("/products/barcode/000000000")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Product not found"


@patch("app.search_products_by_name")
def test_search_products_route(mock_search, client):
    mock_search.return_value = [
        {
            "barcode": "111111111",
            "product_name": "Whole Milk",
            "brand": "Example Brand",
            "category": "Dairy",
            "ingredients": "Milk",
        },
        {
            "barcode": "222222222",
            "product_name": "Chocolate Milk",
            "brand": "Another Brand",
            "category": "Dairy",
            "ingredients": "Milk, cocoa, sugar",
        },
    ]

    response = client.get("/products/search?name=milk")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["products"]) == 2
    assert data["products"][0]["product_name"] == "Whole Milk"
    assert data["products"][1]["product_name"] == "Chocolate Milk"

    mock_search.assert_called_once_with("milk")


def test_search_products_route_missing_name(client):
    response = client.get("/products/search")

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Product name is required"


@patch("app.get_product_by_barcode")
def test_add_product_from_api(mock_get_product, client):
    mock_get_product.return_value = {
        "barcode": "123456789",
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "category": "Plant-based milk",
        "ingredients": "Water, almonds, sugar",
    }

    response = client.post(
        "/inventory/from-api/123456789",
        json={
            "price": 350,
            "stock": 20
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == 3
    assert data["barcode"] == "123456789"
    assert data["product_name"] == "Organic Almond Milk"
    assert data["brand"] == "Silk"
    assert data["category"] == "Plant-based milk"
    assert data["price"] == 350
    assert data["stock"] == 20
    assert data["ingredients"] == "Water, almonds, sugar"

    assert len(inventory) == 3

    mock_get_product.assert_called_once_with("123456789")


@patch("app.get_product_by_barcode")
def test_add_product_from_api_not_found(mock_get_product, client):
    mock_get_product.return_value = None

    response = client.post(
        "/inventory/from-api/000000000",
        json={
            "price": 350,
            "stock": 20
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Product not found in OpenFoodFacts"

    assert len(inventory) == 2


@patch("app.get_product_by_barcode")
def test_add_product_from_api_missing_body(mock_get_product, client):
    mock_get_product.return_value = {
        "barcode": "123456789",
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "category": "Plant-based milk",
        "ingredients": "Water, almonds, sugar",
    }

    response = client.post(
        "/inventory/from-api/123456789"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Request body is required"

    assert len(inventory) == 2


@patch("app.get_product_by_barcode")
def test_add_product_from_api_missing_price(mock_get_product, client):
    mock_get_product.return_value = {
        "barcode": "123456789",
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "category": "Plant-based milk",
        "ingredients": "Water, almonds, sugar",
    }

    response = client.post(
        "/inventory/from-api/123456789",
        json={
            "stock": 20
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Price and stock are required"

    assert len(inventory) == 2


@patch("app.get_product_by_barcode")
def test_add_product_from_api_missing_stock(mock_get_product, client):
    mock_get_product.return_value = {
        "barcode": "123456789",
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "category": "Plant-based milk",
        "ingredients": "Water, almonds, sugar",
    }

    response = client.post(
        "/inventory/from-api/123456789",
        json={
            "price": 350
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Price and stock are required"

    assert len(inventory) == 2