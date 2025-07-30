# eBag Category API

A clean Django-based backend for managing nested categories, similarity relationships, and graph analysis.

## ✅ Features
- Category tree (with flexible nesting)
- Bidirectional similarity (A ~ B)
- Recursive and flat APIs
- Graph analysis (rabbit islands, longest path)
- Django admin with nested UI
- JSON reports and Postman collection

## 🚀 Setup

```bash
git clone <repo>
cd ebag-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

This project uses Django's development server (runserver) for local development. In a real-world deployment, a production-grade WSGI/ASGI server like Gunicorn or Uvicorn would be used.
