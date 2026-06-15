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
