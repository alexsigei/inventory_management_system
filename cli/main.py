import requests


API_URL = "http://127.0.0.1:5000"

def handle_request_error(error):
    print(f"Unable to connect to the API: {error}")

def make_request(method, endpoint, **kwargs):
    try:
        return requests.request(
            method,
            f"{API_URL}{endpoint}",
            **kwargs
        )
    except requests.RequestException:
        print("Unable to connect to the Flask API.")
        print("Make sure the Flask server is running.")
        return None

def display_inventory():
    response = requests.get(f"{API_URL}/inventory")

    if response.status_code != 200:
        print("Failed to retrieve inventory.")
        return

    items = response.json()

    if not items:
        print("\nInventory is empty.")
        return

    print("\n" + "=" * 80)
    print("INVENTORY")
    print("=" * 80)

    for item in items:
        print(f"ID:          {item['id']}")
        print(f"Product:     {item['product_name']}")
        print(f"Brand:       {item['brand']}")
        print(f"Category:    {item['category']}")
        print(f"Barcode:     {item['barcode']}")
        print(f"Price:       KES {item['price']}")
        print(f"Stock:       {item['stock']}")
        print(f"Ingredients: {item['ingredients']}")
        print("-" * 80)


def display_inventory_item():
    item_id = input("Enter inventory item ID: ")

    try:
        item_id = int(item_id)
    except ValueError:
        print("ID must be a number.")
        return

    response = requests.get(f"{API_URL}/inventory/{item_id}")

    if response.status_code == 404:
        print("Inventory item not found.")
        return

    if response.status_code != 200:
        print("Failed to retrieve inventory item.")
        return

    item = response.json()

    print("\n" + "=" * 40)
    print("INVENTORY ITEM")
    print("=" * 40)
    print(f"ID:          {item['id']}")
    print(f"Product:     {item['product_name']}")
    print(f"Brand:       {item['brand']}")
    print(f"Category:    {item['category']}")
    print(f"Barcode:     {item['barcode']}")
    print(f"Price:       KES {item['price']}")
    print(f"Stock:       {item['stock']}")
    print(f"Ingredients: {item['ingredients']}")


def add_inventory_item():
    print("\n=== Add Inventory Item ===")

    barcode = input("Barcode: ")
    product_name = input("Product name: ")
    brand = input("Brand: ")
    category = input("Category: ")
    ingredients = input("Ingredients: ")

    try:
        price = float(input("Price: "))
        stock = int(input("Stock: "))
    except ValueError:
        print("Price must be a number and stock must be a whole number.")
        return

    item = {
        "barcode": barcode,
        "product_name": product_name,
        "brand": brand,
        "category": category,
        "price": price,
        "stock": stock,
        "ingredients": ingredients,
    }

    response = requests.post(
        f"{API_URL}/inventory",
        json=item
    )

    if response.status_code == 201:
        print("\nInventory item added successfully.")
        print(response.json())
    else:
        print("\nFailed to add inventory item.")
        print(response.json())


def update_inventory_item():
    print("\n=== Update Inventory Item ===")

    try:
        item_id = int(input("Enter inventory item ID: "))
    except ValueError:
        print("ID must be a number.")
        return

    print("\nWhat would you like to update?")
    print("1. Price")
    print("2. Stock")
    print("3. Product name")
    print("4. Brand")
    print("5. Category")

    choice = input("Select an option: ")

    fields = {
        "1": "price",
        "2": "stock",
        "3": "product_name",
        "4": "brand",
        "5": "category",
    }

    field = fields.get(choice)

    if field is None:
        print("Invalid option.")
        return

    value = input(f"Enter new {field}: ")

    if field == "price":
        try:
            value = float(value)
        except ValueError:
            print("Price must be a number.")
            return

    elif field == "stock":
        try:
            value = int(value)
        except ValueError:
            print("Stock must be a whole number.")
            return

    response = requests.patch(
        f"{API_URL}/inventory/{item_id}",
        json={field: value}
    )

    if response.status_code == 404:
        print("Inventory item not found.")
        return

    if response.status_code == 200:
        print("\nInventory item updated successfully.")
        print(response.json())
    else:
        print("\nFailed to update inventory item.")


def delete_inventory_item():
    print("\n=== Delete Inventory Item ===")

    try:
        item_id = int(input("Enter inventory item ID: "))
    except ValueError:
        print("ID must be a number.")
        return

    response = requests.delete(
        f"{API_URL}/inventory/{item_id}"
    )

    if response.status_code == 404:
        print("Inventory item not found.")
        return

    if response.status_code == 200:
        print("\nInventory item deleted successfully.")
    else:
        print("\nFailed to delete inventory item.")


def search_openfoodfacts():
    print("\n=== Search OpenFoodFacts ===")

    name = input("Enter product name: ")

    response = requests.get(
        f"{API_URL}/products/search",
        params={"name": name}
    )

    if response.status_code != 200:
        print("Failed to search OpenFoodFacts.")
        return

    products = response.json()["products"]

    if not products:
        print("No products found.")
        return

    print("\nProducts found:")

    for index, product in enumerate(products, start=1):
        print(f"\n{index}. {product['product_name']}")
        print(f"   Barcode: {product['barcode']}")
        print(f"   Brand: {product['brand']}")
        print(f"   Category: {product['category']}")


def add_product_from_openfoodfacts():
    print("\n=== Add Product from OpenFoodFacts ===")

    barcode = input("Enter product barcode: ")

    response = requests.get(
        f"{API_URL}/products/barcode/{barcode}"
    )

    if response.status_code == 404:
        print("Product was not found on OpenFoodFacts.")
        return

    if response.status_code != 200:
        print("Failed to retrieve product.")
        return

    product = response.json()

    print("\nProduct found:")
    print(f"Name:        {product['product_name']}")
    print(f"Brand:       {product['brand']}")
    print(f"Category:    {product['category']}")
    print(f"Ingredients: {product['ingredients']}")

    try:
        price = float(input("\nEnter selling price (KES): "))
        stock = int(input("Enter stock quantity: "))
    except ValueError:
        print("Price must be a number and stock must be a whole number.")
        return

    response = requests.post(
        f"{API_URL}/inventory/from-api/{barcode}",
        json={
            "price": price,
            "stock": stock
        }
    )

    if response.status_code == 201:
        print("\nProduct added to inventory successfully.")
        print(response.json())
    else:
        print("\nFailed to add product to inventory.")
        print(response.json())


def main():
    while True:
        print("\n")
        print("=" * 40)
        print(" INVENTORY MANAGEMENT SYSTEM")
        print("=" * 40)
        print("1. View all inventory")
        print("2. View inventory item")
        print("3. Add inventory item")
        print("4. Update inventory item")
        print("5. Delete inventory item")
        print("6. Search OpenFoodFacts")
        print("7. Add product from OpenFoodFacts")
        print("8. Exit")
        print("=" * 40)

        choice = input("Select an option: ")

        if choice == "1":
            display_inventory()

        elif choice == "2":
            display_inventory_item()

        elif choice == "3":
            add_inventory_item()

        elif choice == "4":
            update_inventory_item()

        elif choice == "5":
            delete_inventory_item()

        elif choice == "6":
            search_openfoodfacts()

        elif choice == "7":
            add_product_from_openfoodfacts()

        elif choice == "8":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()