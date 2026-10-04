def get_next_id(inventory):
    if not inventory:
        return 1

    return max(item["id"] for item in inventory) + 1