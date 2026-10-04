from unittest.mock import patch
from requests import RequestException

from services.openfoodfacts import (
    get_product_by_barcode,
    search_products_by_name,
)


@patch("services.openfoodfacts.requests.get")
def test_get_product_by_barcode(mock_get):
    mock_response = mock_get.return_value

    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "categories": "Plant-based milk",
            "ingredients_text": "Water, almonds, sugar",
        },
    }

    mock_response.raise_for_status.return_value = None

    result = get_product_by_barcode("123456789")

    assert result["barcode"] == "123456789"
    assert result["product_name"] == "Organic Almond Milk"
    assert result["brand"] == "Silk"
    assert result["category"] == "Plant-based milk"
    assert result["ingredients"] == "Water, almonds, sugar"


@patch("services.openfoodfacts.requests.get")
def test_get_product_by_barcode_not_found(mock_get):
    mock_response = mock_get.return_value

    mock_response.json.return_value = {
        "status": 0,
        "product": {},
    }

    mock_response.raise_for_status.return_value = None

    result = get_product_by_barcode("000000000")

    assert result is None


@patch("services.openfoodfacts.requests.get")
def test_get_product_by_barcode_api_failure(mock_get):
    mock_get.side_effect = RequestException("API unavailable")

    result = get_product_by_barcode("123456789")

    assert result is None


@patch("services.openfoodfacts.requests.get")
def test_search_products_by_name(mock_get):
    mock_response = mock_get.return_value

    mock_response.json.return_value = {
        "products": [
            {
                "code": "111111111",
                "product_name": "Whole Milk",
                "brands": "Example Brand",
                "categories": "Dairy",
                "ingredients_text": "Milk",
            },
            {
                "code": "222222222",
                "product_name": "Chocolate Milk",
                "brands": "Another Brand",
                "categories": "Dairy",
                "ingredients_text": "Milk, cocoa, sugar",
            },
        ]
    }

    mock_response.raise_for_status.return_value = None

    result = search_products_by_name("milk")

    assert len(result) == 2
    assert result[0]["barcode"] == "111111111"
    assert result[0]["product_name"] == "Whole Milk"
    assert result[1]["barcode"] == "222222222"
    assert result[1]["product_name"] == "Chocolate Milk"


@patch("services.openfoodfacts.requests.get")
def test_search_products_api_failure(mock_get):
    mock_get.side_effect = RequestException("API unavailable")

    result = search_products_by_name("milk")

    assert result == []