import requests


BASE_URL = "https://world.openfoodfacts.org"

HEADERS = {
    "User-Agent": "InventoryManagementSystem/1.0 (Moringa School Student Project)"
}


def get_product_by_barcode(barcode):
    url = f"{BASE_URL}/api/v2/product/{barcode}.json"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

    except (requests.RequestException, ValueError):
        return None

    if data.get("status") != 1:
        return None

    product = data.get("product", {})

    return {
        "barcode": barcode,
        "product_name": product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "category": product.get("categories", ""),
        "ingredients": product.get("ingredients_text", ""),
    }


def search_products_by_name(name):
    url = f"{BASE_URL}/cgi/search.pl"

    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10,
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

    except (requests.RequestException, ValueError):
        return []

    products = []

    for product in data.get("products", []):
        products.append({
            "barcode": product.get("code", ""),
            "product_name": product.get("product_name", ""),
            "brand": product.get("brands", ""),
            "category": product.get("categories", ""),
            "ingredients": product.get("ingredients_text", ""),
        })

    return products