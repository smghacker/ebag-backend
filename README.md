
# eBag Category Backend

A Django-based backend system for managing a tree of product categories with image support and bidirectional similarity tracking.

## ✅ Features

- Nested categories (tree structure)
- Category CRUD + move within tree
- Tree depth tracking
- Image upload & thumbnailing (max 1MB)
- Bidirectional category similarity (A ↔ B)
- Custom rules:
  - Cannot delete a category with children
  - Cannot be similar to self
  - Adding A→B and B→A is idempotent
- Query categories by:
  - Parent ID
  - Full tree
  - Subtree of a node

## 🚀 Setup

```bash
# 1. Clone the project and navigate into it
cd ebag-backend

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. (Optional) Add mock data
python setup_mock_data.py

# 6. Run server
python manage.py runserver
```

## 🧪 API Usage

All endpoints are under `/categories/` and `/similarities/`.

### 📁 Category Endpoints

#### Create
```bash
curl -X POST http://localhost:8000/categories/ -H "Content-Type: application/json" -d '{
  "name": "Fruits", "description": "Fresh fruits section"
}'
```

#### List (optionally filtered by parent)
```bash
curl http://localhost:8000/categories/
curl http://localhost:8000/categories/?parent=3
```

#### Retrieve
```bash
curl http://localhost:8000/categories/5/
```

#### Update
```bash
curl -X PUT http://localhost:8000/categories/5/ -H "Content-Type: application/json" -d '{
  "name": "Fresh Fruits", "description": "Updated", "parent": null
}'
```

#### Delete (only if no children)
```bash
curl -X DELETE http://localhost:8000/categories/5/
```

#### Get full tree
```bash
curl http://localhost:8000/categories/tree/
```

#### Get subtree
```bash
curl http://localhost:8000/categories/5/subtree/
```

### 🔁 Similarity Endpoints

#### Create (idempotent)
```bash
curl -X POST http://localhost:8000/similarities/ -H "Content-Type: application/json" -d '{
  "category_a": 3, "category_b": 7
}'
```

#### List all similarities
```bash
curl http://localhost:8000/similarities/
```

#### Delete similarity
```bash
curl -X DELETE http://localhost:8000/similarities/12/
```

## 🧠 Similarity Concepts

### Rabbit Hole

The shortest similarity path from one category to another.

### Rabbit Island

Connected components formed via similarity. A set of categories that are all reachable through similarity links.

To analyze this:

```bash
python analyze_similarity.py
```

This prints the longest rabbit hole and lists of rabbit islands.

---

© eBag Engineering – Built for clarity and robustness.
