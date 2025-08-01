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
  - Depth in tree

---

## 📋 Prerequisites

Ensure the following tools are installed before running:

- [Homebrew](https://brew.sh/)
- [pyenv](https://github.com/pyenv/pyenv)
- `mysql` CLI (installed via Homebrew)
- macOS system (tested with Apple Silicon)

Optional but recommended:

- `pyenv-virtualenv`
- `direnv` (to auto-activate venvs)

---

## 🛠️ Quick Start (macOS with Homebrew)

Run the full setup script:

```bash
./setup.sh
```

It installs Python (via pyenv),
MariaDB (via Homebrew),
creates a virtual environment,
sets up the database and user,
installs requirements,
applies migrations,
and creates a Django admin user.

> Admin credentials: `admin / strongpassword`

To setup mock data and then run the server run these commands:
```bash
source venv/bin/activate

python manage.py runserver 0.0.0.0:8000 & #start server background process

python setup_mock_data.py

---

## UI Usage
```bash
open http://127.0.0.1:8000/admin/catalog/category/tree-view/
```
---

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
curl http://localhost:8000/categories/?parent=<category_id>
```

#### Retrieve
```bash
curl http://localhost:8000/categories/<category_id>/
```

#### Update
```bash
curl -X PUT http://localhost:8000/categories/<category_id>/ -H "Content-Type: application/json" -d '{
  "name": "Fresh Fruits", "description": "Updated", "parent": null
}'
```

#### Delete (only if no children)
```bash
curl -X DELETE http://localhost:8000/categories/<category_id>/
```

#### Get full tree
```bash
curl http://localhost:8000/categories/tree/
```

#### Get subtree
```bash
curl http://localhost:8000/categories/<category_id>/subtree/
```

#### Get by depth
```bash
curl http://localhost:8000/categories/by_depth/?depth=<depth>
```

### 🔁 Similarity Endpoints

#### Create (idempotent)
```bash
curl -X POST http://localhost:8000/similarities/ -H "Content-Type: application/json" -d '{
  "category_a": <category_id_1>, "category_b": <category_id_2>
}'
```

#### List all similarities
```bash
curl http://localhost:8000/similarities/
```

#### Delete similarity
```bash
curl -X DELETE http://localhost:8000/similarities/<similarity_id>/
```

---

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
