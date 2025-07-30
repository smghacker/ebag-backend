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
brew install mariadb
brew services start mariadb
brew install mariadb-connector-c

export LDFLAGS="-L/opt/homebrew/opt/mariadb-connector-c/lib"
export CPPFLAGS="-I/opt/homebrew/opt/mariadb-connector-c/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/mariadb-connector-c/lib/pkgconfig"

pip install --upgrade pip
pip install django djangorestframework mysqlclient python-dotenv

echo "🗄️  Creating database and user (if not exist)..."
/opt/homebrew/bin/mysql -u $(whoami) <<EOF
CREATE DATABASE IF NOT EXISTS ebag_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'ebag_user'@'localhost' IDENTIFIED BY 'strongpassword';
GRANT ALL PRIVILEGES ON ebag_db.* TO 'ebag_user'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "🧱 Applying Django migrations..."
python manage.py migrate || echo "📌 Skipped (no models yet)"

echo "✅ Setup complete! Activate with: source venv/bin/activate"
