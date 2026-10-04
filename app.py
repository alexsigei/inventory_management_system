from flask import Flask, jsonify, request

from models import get_next_id
from storage import inventory
from services.openfoodfacts import (
    get_product_by_barcode,
    search_products_by_name
)

app = Flask(__name__)


@app.route("/")
def home():
    return {"message": "Inventory Management API is running"}


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory)


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    item = next(
        (item for item in inventory if item["id"] == item_id),
        None
    )

    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404

    return jsonify(item)

@app.route("/inventory", methods=["POST"])
def create_inventory_item():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    required_fields = [
        "barcode",
        "product_name",
        "brand",
        "category",
        "price",
        "stock"
    ]

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    new_item = {
        "id": get_next_id(inventory),
        "barcode": data["barcode"],
        "product_name": data["product_name"],
        "brand": data["brand"],
        "category": data["category"],
        "price": data["price"],
        "stock": data["stock"],
        "ingredients": data.get("ingredients", "")
    }

    inventory.append(new_item)

    return jsonify(new_item), 201

@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    item = next(
        (item for item in inventory if item["id"] == item_id),
        None
    )

    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    allowed_fields = [
        "barcode",
        "product_name",
        "brand",
        "category",
        "price",
        "stock",
        "ingredients"
    ]

    for field in allowed_fields:
        if field in data:
            item[field] = data[field]

    return jsonify(item)

@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    item = next(
        (item for item in inventory if item["id"] == item_id),
        None
    )

    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404

    inventory.remove(item)

    return jsonify({
        "message": "Inventory item deleted successfully"
    })


@app.route("/products/barcode/<barcode>", methods=["GET"])
def find_product_by_barcode(barcode):
    product = get_product_by_barcode(barcode)

    if product is None:
        return jsonify({
            "error": "Product not found"
        }), 404

    return jsonify(product)

@app.route("/products/search", methods=["GET"])
def search_products():
    name = request.args.get("name")

    if not name:
        return jsonify({
            "error": "Product name is required"
        }), 400

    products = search_products_by_name(name)

    return jsonify({
        "products": products
    })

@app.route("/inventory/from-api/<barcode>", methods=["POST"])
def add_product_from_api(barcode):
    product = get_product_by_barcode(barcode)

    if product is None:
        return jsonify({"error": "Product not found in OpenFoodFacts"}), 404

    if not request.is_json:
        return jsonify({"error": "Request body is required"}), 400

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    if "price" not in data or "stock" not in data:
        return jsonify({
            "error": "Price and stock are required"
        }), 400

    new_item = {
        "id": get_next_id(inventory),
        "barcode": product["barcode"],
        "product_name": product["product_name"],
        "brand": product["brand"],
        "category": product["category"],
        "price": data["price"],
        "stock": data["stock"],
        "ingredients": product["ingredients"]
    }

    inventory.append(new_item)

    return jsonify(new_item), 201

if __name__ == "__main__":
    app.run(debug=True)