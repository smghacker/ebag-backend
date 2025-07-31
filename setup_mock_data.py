import os
import requests

BASE_URL = "http://localhost:8000/api"
IMAGE_DIR = "test-images"

categories = [
  {
    "id": 1,
    "name": "Fruits",
    "description": "Fruits section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/1/15/Red_Apple.jpg",
    "parent": None
  },
  {
    "id": 2,
    "name": "Vegetables",
    "description": "Vegetables section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Vegetables.jpg",
    "parent": None
  },
  {
    "id": 3,
    "name": "Dairy",
    "description": "Dairy section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/d/db/Milk_glass.jpg",
    "parent": None
  },
  {
    "id": 4,
    "name": "Bakery",
    "description": "Bakery section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/f/f9/Bread.jpg",
    "parent": None
  },
  {
    "id": 5,
    "name": "Meat",
    "description": "Meat section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/9/93/Chicken_meat.jpg",
    "parent": None
  },
  {
    "id": 6,
    "name": "Fish",
    "description": "Fish section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/3/32/Fish_on_plate.jpg",
    "parent": None
  },
  {
    "id": 7,
    "name": "Beverages",
    "description": "Beverages section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/3/36/Coca-Cola_Bottle.JPG",
    "parent": None
  },
  {
    "id": 8,
    "name": "Snacks",
    "description": "Snacks section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/2/29/Potato_chips.jpg",
    "parent": None
  },
  {
    "id": 9,
    "name": "Frozen Foods",
    "description": "Frozen Foods section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/e/ed/Frozen_foods.jpg",
    "parent": None
  },
  {
    "id": 10,
    "name": "Household",
    "description": "Household section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Cleaning_products.jpg",
    "parent": None
  },
  {
    "id": 11,
    "name": "Citrus Fruits",
    "description": "Citrus Fruits section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/c/cd/Orange-Fruit-Pieces.jpg",
    "parent": 1
  },
  {
    "id": 12,
    "name": "Tropical Fruits",
    "description": "Tropical Fruits section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Mango.jpg",
    "parent": 1
  },
  {
    "id": 13,
    "name": "Leafy Greens",
    "description": "Leafy Greens section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/f/f9/Spinach_leaves.jpg",
    "parent": 2
  },
  {
    "id": 14,
    "name": "Root Vegetables",
    "description": "Root Vegetables section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/e/e2/Carrots.jpg",
    "parent": 2
  },
  {
    "id": 15,
    "name": "Milk Products",
    "description": "Milk Products section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/5/53/Milk_products.jpg",
    "parent": 3
  },
  {
    "id": 16,
    "name": "Cheeses",
    "description": "Cheeses section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/5/55/Cheese_platter.jpg",
    "parent": 3
  },
  {
    "id": 17,
    "name": "Cakes",
    "description": "Cakes section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/f/f5/Chocolate_cake.jpg",
    "parent": 4
  },
  {
    "id": 18,
    "name": "Pastries",
    "description": "Pastries section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/b/bb/Pastry.jpg",
    "parent": 4
  },
  {
    "id": 19,
    "name": "Cleaning",
    "description": "Cleaning section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Cleaning_supplies.jpg",
    "parent": 10
  },
  {
    "id": 20,
    "name": "Laundry",
    "description": "Laundry section",
    "image": "https://upload.wikimedia.org/wikipedia/commons/3/32/Laundry_basket.jpg",
    "parent": 10
  }
]
similarities = [
  {
    "id": 1,
    "category_a": 1,
    "category_b": 2
  },
  {
    "id": 2,
    "category_a": 2,
    "category_b": 3
  },
  {
    "id": 3,
    "category_a": 4,
    "category_b": 5
  },
  {
    "id": 4,
    "category_a": 6,
    "category_b": 7
  },
  {
    "id": 5,
    "category_a": 8,
    "category_b": 9
  },
  {
    "id": 6,
    "category_a": 10,
    "category_b": 11
  }
]

def create_categories():
    id_map = {}
    for cat in categories:
        original_id = cat['id']
        name_base = cat['name'].replace(" ", "_").lower()
        jpg_path = os.path.join(IMAGE_DIR, name_base + ".jpg")
        jpeg_path = os.path.join(IMAGE_DIR, name_base + ".jpeg")
        img_path = jpg_path if os.path.exists(jpg_path) else jpeg_path
        if not os.path.exists(img_path):
            print(f"Skipping {cat['name']} (image missing)")
            continue
        files = {
            'image': open(img_path, 'rb')
        }
        data = {
            'name': cat['name'],
            'description': cat['description'],
            'children': [],
            'similar_to': []
        }
        resp = requests.post(f"{BASE_URL}/categories/", data=data, files=files)
        if resp.ok:
            new_id = resp.json().get('id')
            id_map[original_id] = new_id
            print(f"Created {cat['name']}: original_id={original_id} ➜ new_id={new_id}")
        else:
            print(f"Failed to create {cat['name']}: {resp.status_code} {resp.text}")
    return id_map

def patch_children(id_map):
    parent_to_children = {}
    for cat in categories:
        if cat['parent'] is not None:
            parent = cat['parent']
            parent_to_children.setdefault(parent, []).append(cat['id'])

    for original_parent, children in parent_to_children.items():
        new_parent_id = id_map.get(original_parent)
        new_child_ids = [id_map.get(cid) for cid in children if id_map.get(cid)]
        if not new_parent_id or not new_child_ids:
            print(f"Skipping parent patch for ID {original_parent}")
            continue
        payload = { "children": new_child_ids }
        resp = requests.patch(f"{BASE_URL}/categories/{new_parent_id}/", json=payload)
        if resp.ok:
            print(f"Set children for parent {new_parent_id}: {new_child_ids}")
        else:
            print(f"Failed to patch children for parent {new_parent_id}: {resp.status_code} {resp.text}")

def create_similarities(id_map):
    for sim in similarities:
        a = id_map.get(sim['category_a'])
        b = id_map.get(sim['category_b'])
        if not a or not b:
            print(f"Skipping similarity (missing mapped IDs): {sim}")
            continue
        payload = {
            'category_a': a,
            'category_b': b
        }
        resp = requests.post(f"{BASE_URL}/similarities/", json=payload)
        if resp.ok:
            print(f"Linked similarity: {a} <-> {b}")
        else:
            print(f"Failed to link similarity: {a} <-> {b}: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    id_map = create_categories()
    patch_children(id_map)
    create_similarities(id_map)
