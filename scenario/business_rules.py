def get_inventory_from_items(items, inventory_len):
    inventory = []
    for i in range(1, inventory_len + 1):
        item = [x for x in items if x.position == i]
        if item:
            inventory.append(
                {
                    "id": item[0].id,
                    "item_id": item[0].item_id,
                }
            )
        else:
            inventory.append(None)
    return inventory
