# Inventory Management System

A simple **Inventory Management REST API** built with Flask. It supports CRUD operations, OpenFoodFacts integration, and a command-line interface (CLI).

## Features

* View all inventory items
* View a single inventory item
* Add inventory items
* Update inventory items
* Delete inventory items
* Search products using OpenFoodFacts
* Add products from OpenFoodFacts to inventory
* CLI for interacting with the API
* Automated tests with pytest

## Technologies

* Python 3
* Flask
* Requests
* Pytest
* OpenFoodFacts API

## Project Structure

```text
inventory-management-system/
├── app.py
├── models.py
├── storage.py
├── cli/
│   └── main.py
├── services/
│   └── openfoodfacts.py
├── tests/
│   ├── test_inventory.py
│   ├── test_openfoodfacts.py
│   └── test_cli.py
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd inventory-management-system
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Run the API

Start the Flask server:

```bash
python app.py
```

The API will run at:

```text
http://127.0.0.1:5000
```

Keep this terminal running.

## Run the CLI

Open a **second terminal**, activate the virtual environment, and run:

```bash
python cli/main.py
```

You can then use the menu to manage inventory and search/add products from OpenFoodFacts.

## API Endpoints

| Method | Endpoint                        | Description                            |
| ------ | ------------------------------- | -------------------------------------- |
| GET    | `/`                             | API status                             |
| GET    | `/inventory`                    | Get all inventory                      |
| GET    | `/inventory/<id>`               | Get one item                           |
| POST   | `/inventory`                    | Add an item                            |
| PATCH  | `/inventory/<id>`               | Update an item                         |
| DELETE | `/inventory/<id>`               | Delete an item                         |
| GET    | `/products/barcode/<barcode>`   | Find product by barcode                |
| GET    | `/products/search?name=<name>`  | Search products                        |
| POST   | `/inventory/from-api/<barcode>` | Add OpenFoodFacts product to inventory |

## Run Tests

Make sure the virtual environment is activated, then run:

```bash
pytest -v
```

The test suite covers the Flask API, CLI, and OpenFoodFacts integration.

## Example

To add an inventory item using the API:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
-H "Content-Type: application/json" \
-d '{
  "barcode": "123456789",
  "product_name": "Sample Product",
  "brand": "Sample Brand",
  "category": "Food",
  "price": 250,
  "stock": 10,
  "ingredients": "Example ingredients"
}'
```

## External API

Product information is retrieved from **OpenFoodFacts** using a product barcode or name search.

The application does not store OpenFoodFacts data permanently. Products are added to the application's in-memory inventory when requested through the API or CLI.
