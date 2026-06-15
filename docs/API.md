# EDU Control Pro API hujjatlari

## Asosiy ma'lumotlar

- **Base URL:** `http://localhost:8000/api/v1`
- **WebSocket:** `ws://localhost:8000/ws/agent`
- **Swagger:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Autentifikatsiya

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| POST | `/auth/login` | Kirish |
| POST | `/auth/refresh` | Tokenni yangilash |
| POST | `/auth/logout` | Chiqish |
| GET | `/auth/me` | Joriy foydalanuvchi |

## Kompyuterlar

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| GET | `/computers` | Ro'yxat (filter, pagination) |
| GET | `/computers/{id}` | Batafsil |
| PUT | `/computers/{id}` | Yangilash |
| DELETE | `/computers/{id}` | O'chirish |
| GET | `/computers/{id}/stats` | CPU/RAM/Disk tarixi |
| GET | `/computers/{id}/audit` | Audit loglari |
| GET | `/computers/{id}/commands` | Buyruqlar tarixi |

## Siyosatlar

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| GET | `/policies` | Ro'yxat |
| POST | `/policies` | Yangi siyosat |
| GET | `/policies/{id}` | Batafsil |
| PUT | `/policies/{id}` | Yangilash |
| DELETE | `/policies/{id}` | O'chirish |
| POST | `/policies/{id}/assign` | Tayinlash |
| DELETE | `/policies/{id}/assign/{assignment_id}` | Bekor qilish |
| GET | `/policies/computer/{computer_id}` | Kompyuter siyosatlari |

## Buyruqlar

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| POST | `/computers/{id}/commands` | Buyruq yuborish |
| POST | `/groups/{id}/commands` | Guruhga buyruq |
| POST | `/computers/broadcast` | Hammaga buyruq |

## Audit

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| GET | `/audit` | Loglarni ko'rish |

## Hisobotlar

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| POST | `/reports/generate` | Hisobot yaratish |
| GET | `/reports/{task_id}/status` | Holatni tekshirish |
| GET | `/reports/{task_id}/download` | Yuklab olish |

## Health check

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| GET | `/health` | Server holati |
