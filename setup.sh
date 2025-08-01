#!/bin/bash

set -e

# Initialize pyenv for script
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

echo "🔧 Setting up Python environment..."
PYTHON_VERSION=3.11.9

echo "📦 Installing Python $PYTHON_VERSION via pyenv..."
pyenv install -s $PYTHON_VERSION
pyenv local $PYTHON_VERSION

echo "🐍 Creating virtualenv..."
rm -rf venv
python -m venv venv
source venv/bin/activate

echo "📚 Installing packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🧱 Applying Django migrations..."
python manage.py migrate

echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(username='admin').exists() or \
User.objects.create_superuser('admin', 'admin@ebag.com', 'strongpassword')" \
| python manage.py shell

echo "✅ Setup complete! Activate with: source venv/bin/activate"
