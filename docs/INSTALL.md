# EDU Control Pro - O'rnatish qo'llanmasi

## Tezkor o'rnatish (Docker)

```bash
# 1. Loyihani klonlash
git clone https://github.com/username/edu-control-pro.git
cd edu-control-pro

# 2. Docker orqali ishga tushirish
docker-compose up -d

# 3. Super admin yaratish
docker exec -it edu-control-pro-server python manage.py create_superadmin
```

Server http://localhost:8000 da ishlaydi.

## Server o'rnatish (Ubuntu 22.04)

```bash
# 1. Kerakli paketlar
sudo apt update
sudo apt install python3.12 python3.12-venv postgresql redis nginx certbot -y

# 2. PostgreSQL sozlash
sudo -u postgres createdb educontrol
sudo -u postgres psql -c "CREATE USER educontrol_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE educontrol TO educontrol_user;"
psql -U educontrol_user -d educontrol -f database/schema.sql

# 3. Redis sozlash
sudo systemctl enable redis
sudo systemctl start redis

# 4. Virtual muhit va bog'liqliklar
cd server
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Muhit o'zgaruvchilari
cp .env.example .env
# .env faylni o'z sozlamalaringizga moslang

# 6. Alembic migratsiya
alembic upgrade head

# 7. Super admin yaratish
python manage.py create_superadmin

# 8. Systemd xizmati
sudo tee /etc/systemd/system/educontrol-server.service <<EOF
[Unit]
Description=EDU Control Pro Server
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/educontrol/server
EnvironmentFile=/opt/educontrol/server/.env
ExecStart=/opt/educontrol/server/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable educontrol-server
sudo systemctl start educontrol-server

# 9. Nginx sozlash
sudo tee /etc/nginx/sites-available/educontrol <<EOF
server {
    listen 80;
    server_name educontrol.local;
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_read_timeout 86400s;
    }

    location /ws/agent {
        proxy_pass http://127.0.0.1:8000/ws/agent;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/educontrol /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## Agent o'rnatish (Windows)

```batch
@echo off
REM Administrator sifatida ishga tushiring

REM 1. Python 3.12 o'rnatilganligini tekshirish
python --version || (
    echo Python 3.12 o'rnatilmagan!
    exit /b 1
)

REM 2. Virtual muhit yaratish
cd client_agent
python -m venv venv
call venv\Scripts\activate

REM 3. Kutubxonalarni o'rnatish
pip install -r requirements.txt

REM 4. Agentni xizmat sifatida o'rnatish
python main.py install

REM 5. Xizmatni ishga tushirish
python main.py start

echo Agent muvaffaqiyatli o'rnatildi!
```

## Xavfsizlik masalalari

1. `.env` faylidagi `SECRET_KEY` ni o'zgartiring
2. PostgreSQL parolini o'zgartiring
3. Let's Encrypt bilan HTTPS o'rnating: `sudo certbot --nginx -d educontrol.local`
4. Nginx access loglarni kuzatib boring
5. Muntazam zaxira nusxalarini oling: `pg_dump -U educontrol educontrol > backup.sql`
