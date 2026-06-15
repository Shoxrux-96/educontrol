# EDU Control Pro

O'quv markazlari uchun kompyuterlarni markazlashtirilgan boshqarish tizimi.

## Imkoniyatlar

- 500+ kompyuterni bir vaqtda boshqarish
- Internet whitelist/blacklist
- Dastur nazorati
- USB qurilmalarni bloklash
- Ekran monitoring (screenshot)
- Audit log (o'chirib bo'lmaydigan)
- Hisobotlar (PDF/Excel/CSV)
- Xabar yuborish
- Masofaviy boshqaruv (lock, restart, shutdown)

## Arxitektura

```
[Admin Desktop] <──> [Server (FastAPI)]
                           │
                    [PostgreSQL + Redis]
                           │
              ┌────────────┴────────────┐
         [Agent Win]  [Agent Win]  ... [Agent Win]
```

## Tezkor boshlash

```bash
docker-compose up -d
```

## Komponentlar

- **Server** - FastAPI backend, WebSocket hub, Celery tasklar
- **Admin Desktop** - PySide6 grafik interfeys
- **Client Agent** - Windows Service (PyInstaller bilan exe)

## Texnologiyalar

- Python 3.12, FastAPI, SQLAlchemy 2.0, PostgreSQL 16, Redis 7
- PySide6 (Qt6), WebSocket, Celery
- Argon2id, JWT, TLS 1.3

## Hujjatlar

- [Texnik Topshiriq](docs/TZ.md)
- [O'rnatish qo'llanmasi](docs/INSTALL.md)
- [Foydalanuvchi qo'llanmasi](docs/USER_MANUAL.md)
- [API hujjatlari](docs/API.md)

## Yakunlanmagan ishlar

### Server
- [x] Docker compose (6 service: nginx, server, postgres, redis, celery-worker, celery-beat)
- [x] 55/55 pytest testlari o'tadi
- [x] Monitoring + Alert tizimi (9 ta endpoint)
- [x] Agent auto-update (build upload, check, download)
- [x] Celery reports + scheduled tasks
- [x] Nginx reverse proxy + HTTPS (SSL self-signed)
- [x] Rate limiting (Redis asosida, opt-in: `RATE_LIMIT_ENABLED=true`)
- [x] API docs (Swagger/Redoc, `docs_enabled=false` bilan yopish mumkin)
- [x] Backup automation (Celery daily schedule)

### Client Agent (Windows)
- [x] Barcha modullar yozilgan (internet, app, USB, screen, print, system)
- [x] WebSocket ulanish, heartbeat, screenshot
- [x] Auto-update tekshirish va yuklab olish
- [ ] **PyInstaller bilan .exe build** (Windows'da bajariladi)
- [ ] **Windows Service sifatida ishga tushirish** (pywin32)
- [ ] Real kompyuterda sinov

### Admin Desktop (Windows)
- [x] Barcha widgetlar yozilgan (dashboard, computers, policies, audit, reports, screen monitor)
- [x] WebSocket ulanish
- [ ] **Bir marta ishga tushirish va sinash** (PySide6)
- [ ] Auto-update (agent bilan birgalikda)

### Boshqa
- [ ] `.exe` installer yaratish (Inno Setup yoki NSIS)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Client Agent va Admin Desktop uchun SSL sertifikat tekshiruvi
- [ ] Email notification (SMTP sozlash)
