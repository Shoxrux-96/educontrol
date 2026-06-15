#!/bin/bash
set -e

echo "=== EDU Control Pro - Server Installer ==="

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Install dependencies
apt update
apt install -y python3.12 python3.12-venv postgresql redis nginx certbot

# Setup PostgreSQL
echo "Creating database..."
sudo -u postgres createdb educontrol 2>/dev/null || echo "Database exists"
sudo -u postgres psql -c "CREATE USER educontrol WITH PASSWORD 'changeme';" 2>/dev/null || echo "User exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE educontrol TO educontrol;" 2>/dev/null || true

# Setup application
mkdir -p /opt/educontrol
cp -r ../.. /opt/educontrol/
cd /opt/educontrol/server

python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
echo "Edit .env file with your settings!"
echo "Then run: python manage.py migrate"
echo "And: python manage.py create_superadmin"
echo ""
echo "=== Installation complete ==="
