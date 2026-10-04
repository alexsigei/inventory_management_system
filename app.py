from flask import Flask, jsonify, request

from models import get_next_id
from storage import inventory

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


if __name__ == "__main__":
    app.run(debug=True)