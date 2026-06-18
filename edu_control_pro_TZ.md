# EDU CONTROL PRO
## Texnik Topshiriq (TZ) — To'liq va Batafsil Versiya

**Versiya:** 1.0  
**Sana:** 2025  
**Holat:** Loyiha bosqichi

---

## MUNDARIJA

1. [Loyiha haqida umumiy ma'lumot](#1-loyiha-haqida)
2. [Tizim arxitekturasi](#2-tizim-arxitekturasi)
3. [Texnologiyalar steki](#3-texnologiyalar-steki)
4. [Ma'lumotlar bazasi sxemasi](#4-malumotlar-bazasi)
5. [API spetsifikatsiyasi](#5-api-spetsifikatsiyasi)
6. [Modullar batafsil tavsifi](#6-modullar)
7. [Xavfsizlik talablari](#7-xavfsizlik)
8. [Ishlash talablari (Performance)](#8-ishlash-talablari)
9. [Papkalar strukturasi](#9-papkalar-strukturasi)
10. [O'rnatish va sozlash](#10-ornatish)
11. [Sinov talablari](#11-sinov)
12. [Qabul qilish mezonlari](#12-qabul-qilish)

---

# 1. LOYIHA HAQIDA

## 1.1 Nima uchun kerak

O'quv markazlarida o'quvchilar kompyuterlarini nazorat qilish murakkab va qo'lda bajarish qiyin. Har bir kompyuterni alohida boshqarish vaqt yo'qotadi, o'quvchilar ruxsatsiz saytlarga kiradi, keraksiz dasturlar o'rnatadi. EDU Control Pro bu muammoni hal qiladi — bitta markazdan hammani boshqarish.

## 1.2 Tizim nima qiladi

- Administrator bitta ekrandan 500+ kompyuterni ko'radi va boshqaradi
- O'quvchilar faqat ruxsat etilgan saytlar va dasturlardan foydalanadi
- Har qanday harakat avtomatik logga yoziladi
- Hisobotlar PDF/Excel formatida yuklab olinadi
- Buyruqlar 2 soniyadan kam vaqtda yetib boradi

## 1.3 Foydalanuvchilar

| Rol | Soni (taxminan) | Asosiy vazifa |
|-----|-----------------|---------------|
| Super Admin | 1–2 kishi | Tizim sozlash, administrator yaratish |
| Administrator | 5–20 kishi | Kunlik monitoring, boshqaruv |
| O'quvchi | 500+ kishi | Faqat ruxsat etilgan resurslardan foydalanish |

---

# 2. TIZIM ARXITEKTURASI

## 2.1 Umumiy sxema

```
[Admin Desktop] <──WebSocket──> [Server (FastAPI)]
                                        │
                                        ├── PostgreSQL (ma'lumotlar)
                                        ├── Redis (kesh, sessiya)
                                        └── WebSocket Hub
                                                │
                              ┌─────────────────┴──────────────────┐
                     [Client Agent 1]  [Client Agent 2]  ... [Client Agent N]
                     (Windows PC)      (Windows PC)           (Windows PC)
```

## 2.2 Server komponenti

**Maqsad:** Markaziy boshqaruv, barcha mantiqni o'z ichiga oladi.

**Vazifalar:**
- REST API orqali admin desktop bilan muloqot
- WebSocket orqali client agentlar bilan real vaqt aloqasi
- Siyosatlarni saqlash va tarqatish
- Audit loglarni yozish
- Hisobotlar generatsiyasi
- Foydalanuvchi autentifikatsiyasi va avtorizatsiyasi

**Muhim xususiyatlar:**
- Bir vaqtda 500+ WebSocket ulanishni ushlab turish
- Har bir buyruq uchun delivery confirmation (tasdiqlash)
- Agent ulanishi uzilsa — offline statusga o'tkazish, qayta ulanganda siyosatlarni resend qilish

## 2.3 Admin Desktop komponenti

**Maqsad:** Administratorlar uchun vizual boshqaruv paneli.

**Ekranlar:**
1. **Dashboard** — real-time umumiy ko'rinish
2. **Kompyuterlar ro'yxati** — jadval ko'rinishida barcha agentlar
3. **Screen monitoring** — thumbnail va to'liq ekran ko'rinish
4. **Guruhlar boshqaruvi** — kompyuterlarni guruhlarga ajratish
5. **Siyosatlar** — internet, dastur, USB cheklovlari
6. **Hisobotlar** — kunlik/haftalik/oylik, eksport
7. **Audit log** — filtrlash, qidirish
8. **Sozlamalar** — tizim konfiguratsiyasi

## 2.4 Client Agent komponenti

**Maqsad:** O'quvchi kompyuterida fonda ishlaydigan xizmat.

**Xususiyatlar:**
- Windows Service sifatida o'rnatiladi (TaskManager'da ko'rinmaydi)
- System tray ikonkasi — faqat administrator yashirish/ko'rsatishni boshqaradi
- Server bilan WebSocket ulanishni saqlab turadi
- Ping/pong mexanizmi (30 soniyada bir marta)
- Ulanish uzilsa — 5, 10, 30, 60 soniya intervalda qayta ulanish urinishi
- Local siyosat keshi — server offline bo'lsa ham ishlaydi

**Buyruqlarni bajarish:**
- Buyruq kelishi → JSON parse → validator → bajaruvchi → natija serverga

---

# 3. TEXNOLOGIYALAR STEKI

## 3.1 Backend (Server)

```
Python 3.12
├── FastAPI 0.111+          — REST API framework
│   ├── Pydantic v2          — validatsiya va sxema
│   ├── python-jose          — JWT token
│   └── passlib[argon2]      — parol xeshlash
├── SQLAlchemy 2.0           — ORM (async)
│   └── asyncpg              — async PostgreSQL driver
├── WebSockets               — real-time aloqa
├── Redis (aioredis)         — sessiya, kesh, pub/sub
├── Celery + Redis           — background tasklar (hisobotlar)
├── ReportLab                — PDF generatsiya
├── openpyxl                 — Excel generatsiya
└── Alembic                  — database migratsiyalar
```

## 3.2 Admin Desktop

```
Python 3.12
├── PySide6 (Qt6)            — UI framework
│   ├── QMainWindow          — asosiy oyna
│   ├── QTableWidget         — jadvallar
│   ├── QChart               — grafiklar
│   └── QWebEngineView       — web kontentni ko'rsatish (agar kerak)
├── websocket-client         — server bilan aloqa
├── httpx                    — REST API so'rovlar
├── Pillow                   — screenshot ko'rsatish
└── pyqtgraph                — real-time grafiklar
```

## 3.3 Client Agent

```
Python 3.12 (PyInstaller bilan exe ga aylantiriladi)
├── websockets               — server bilan aloqa
├── psutil                   — CPU, RAM, disk monitoring
├── pywin32 (win32api, win32con, win32service)
│   ├── Windows Service boshqaruvi
│   ├── Jarayon (process) boshqaruvi
│   ├── Registry boshqaruvi
│   └── USB qurilmalar
├── Pillow + mss             — screenshot olish
├── mss                      — tez screenshot (3 soniyadan kam)
└── requests                 — fallback HTTP aloqa
```

## 3.4 Infratuzilma

```
PostgreSQL 16       — asosiy ma'lumotlar bazasi
Redis 7             — kesh, sessiya, pub/sub
Nginx               — reverse proxy, HTTPS, static fayllar
Certbot             — TLS/SSL sertifikat
Docker + Compose    — konteynerizatsiya (ixtiyoriy)
```

---

# 4. MA'LUMOTLAR BAZASI

## 4.1 Asosiy jadvallar

### users
```sql
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username    VARCHAR(50) UNIQUE NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Argon2id
    role        ENUM('super_admin', 'admin', 'viewer') NOT NULL,
    full_name   VARCHAR(100),
    is_active   BOOLEAN DEFAULT TRUE,
    last_login  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    created_by  UUID REFERENCES users(id)
);
```

### computer_groups
```sql
CREATE TABLE computer_groups (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    color       VARCHAR(7),   -- hex rang (#FF5733)
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### computers
```sql
CREATE TABLE computers (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    hostname    VARCHAR(255),
    ip_address  INET,
    mac_address MACADDR,
    group_id    UUID REFERENCES computer_groups(id),
    os_version  VARCHAR(100),
    agent_version VARCHAR(20),
    status      ENUM('online','offline','busy','locked','maintenance') DEFAULT 'offline',
    last_seen   TIMESTAMPTZ,
    -- Hardware info (agent dan keladi)
    cpu_model   VARCHAR(200),
    ram_gb      SMALLINT,
    disk_gb     SMALLINT,
    -- Current session
    current_user VARCHAR(100),
    cpu_usage   SMALLINT,    -- 0-100%
    ram_usage   SMALLINT,    -- 0-100%
    disk_usage  SMALLINT,    -- 0-100%
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### policies
```sql
CREATE TABLE policies (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    policy_type ENUM('internet','application','usb','print','screen') NOT NULL,
    config      JSONB NOT NULL,  -- siyosat konfiguratsiyasi
    is_active   BOOLEAN DEFAULT TRUE,
    created_by  UUID REFERENCES users(id),
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### policy_assignments
```sql
CREATE TABLE policy_assignments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id   UUID REFERENCES policies(id),
    target_type ENUM('computer','group','all') NOT NULL,
    target_id   UUID,   -- NULL bo'lsa 'all' degan ma'no
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMPTZ DEFAULT NOW()
);
```

### audit_logs
```sql
CREATE TABLE audit_logs (
    id          BIGSERIAL PRIMARY KEY,  -- UUID emas, tez insert uchun
    event_type  VARCHAR(50) NOT NULL,   -- 'login', 'app_launch', 'usb_connect' ...
    severity    ENUM('info','warning','critical') DEFAULT 'info',
    computer_id UUID REFERENCES computers(id),
    user_id     UUID REFERENCES users(id),
    description TEXT NOT NULL,
    metadata    JSONB,                  -- qo'shimcha ma'lumotlar
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
-- Partitioning: har oy yangi partition (performance uchun)
-- Index: (computer_id, created_at), (event_type, created_at)
-- MUHIM: DELETE va UPDATE yo'q — faqat INSERT
```

### screenshots
```sql
CREATE TABLE screenshots (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    computer_id UUID REFERENCES computers(id),
    file_path   VARCHAR(500) NOT NULL,  -- disk da saqlash joyi
    file_size   INTEGER,                -- bytes
    taken_at    TIMESTAMPTZ DEFAULT NOW()
);
-- Eski screenshotlar avtomatik o'chiriladi (30 kundan keyin)
```

### commands
```sql
CREATE TABLE commands (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    computer_id UUID REFERENCES computers(id),
    command_type VARCHAR(50) NOT NULL,  -- 'lock', 'message', 'screenshot', ...
    payload     JSONB,
    status      ENUM('pending','sent','delivered','executed','failed') DEFAULT 'pending',
    sent_by     UUID REFERENCES users(id),
    sent_at     TIMESTAMPTZ DEFAULT NOW(),
    executed_at TIMESTAMPTZ,
    result      JSONB
);
```

### messages
```sql
CREATE TABLE messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title       VARCHAR(200),
    body        TEXT NOT NULL,
    message_type ENUM('info','warning','critical') DEFAULT 'info',
    sender_id   UUID REFERENCES users(id),
    target_type ENUM('computer','group','all') NOT NULL,
    target_id   UUID,
    sent_at     TIMESTAMPTZ DEFAULT NOW()
);
```

## 4.2 JSONB Siyosat konfiguratsiyalari

### Internet siyosati (policy_type = 'internet')
```json
{
  "mode": "whitelist",
  "allowed_domains": [
    "github.com",
    "python.org",
    "w3schools.com",
    "*.google.com"
  ],
  "blocked_domains": [],
  "block_page_url": "http://server/blocked",
  "log_attempts": true
}
```

### Dastur siyosati (policy_type = 'application')
```json
{
  "mode": "whitelist",
  "allowed_apps": [
    {"name": "VS Code", "exe": "Code.exe", "path": "C:\\Program Files\\*"},
    {"name": "Chrome", "exe": "chrome.exe"},
    {"name": "PyCharm", "exe": "pycharm64.exe"}
  ],
  "block_installers": true,
  "block_portable": true,
  "kill_on_detect": true,
  "log_attempts": true
}
```

### USB siyosati (policy_type = 'usb')
```json
{
  "mode": "block_all",
  "allowed_devices": [],
  "log_connections": true,
  "notify_admin": true
}
```

---

# 5. API SPETSIFIKATSIYASI

## 5.1 Authentication

```
POST /api/v1/auth/login
  Body: {username, password}
  Response: {access_token, refresh_token, expires_in, user}

POST /api/v1/auth/refresh
  Body: {refresh_token}
  Response: {access_token, expires_in}

POST /api/v1/auth/logout
  Header: Authorization: Bearer <token>
```

## 5.2 Kompyuterlar

```
GET    /api/v1/computers              — ro'yxat (filter, pagination)
GET    /api/v1/computers/{id}         — batafsil
PUT    /api/v1/computers/{id}         — yangilash (nom, guruh)
DELETE /api/v1/computers/{id}         — o'chirish

GET    /api/v1/computers/{id}/stats   — CPU/RAM/Disk tarixi
GET    /api/v1/computers/{id}/screenshots — screenshot ro'yxati
GET    /api/v1/computers/{id}/audit   — bu kompyuter audit loglari
```

## 5.3 Buyruqlar (Commands)

```
POST /api/v1/computers/{id}/commands
  Body: {command_type, payload}
  
  Buyruq turlari:
  - lock_screen       — ekranni bloklash
  - unlock_screen     — blokni ochish
  - take_screenshot   — screenshot olish
  - send_message      — xabar yuborish
  - restart           — qayta yuklash
  - shutdown          — o'chirish
  - kill_process      — jarayonni to'xtatish {process_name}
  - open_app          — dastur ochish {exe_path}
  - run_command       — buyruq bajarish {cmd} [faqat super_admin]

POST /api/v1/groups/{id}/commands    — guruhga buyruq
POST /api/v1/computers/broadcast     — hammaga buyruq
```

## 5.4 Siyosatlar

```
GET    /api/v1/policies              — ro'yxat
POST   /api/v1/policies              — yangi siyosat
GET    /api/v1/policies/{id}         — batafsil
PUT    /api/v1/policies/{id}         — yangilash
DELETE /api/v1/policies/{id}         — o'chirish

POST   /api/v1/policies/{id}/assign  — kompyuter/guruhga tayinlash
DELETE /api/v1/policies/{id}/assign  — bekor qilish

GET    /api/v1/computers/{id}/policies — kompyuterdagi siyosatlar
```

## 5.5 Hisobotlar

```
POST /api/v1/reports/generate
  Body: {
    report_type: "daily|weekly|monthly|custom",
    start_date: "2025-01-01",
    end_date: "2025-01-31",
    scope: "all|group|computer",
    scope_id: null,
    format: "pdf|excel|csv",
    include: ["internet", "applications", "usb", "print"]
  }
  Response: {task_id}   — asinxron, Celery task

GET /api/v1/reports/{task_id}/status  — holat
GET /api/v1/reports/{task_id}/download — yuklab olish
```

## 5.6 WebSocket Protokoli (Server ↔ Agent)

### Agent → Server

```json
// Ulanish vaqtida
{
  "type": "register",
  "agent_id": "uuid",
  "hostname": "PC-001",
  "ip": "192.168.1.10",
  "mac": "AA:BB:CC:DD:EE:FF",
  "os": "Windows 11 Pro 23H2",
  "agent_version": "1.0.0"
}

// Har 10 soniyada
{
  "type": "heartbeat",
  "agent_id": "uuid",
  "cpu": 45,
  "ram": 62,
  "disk": 78,
  "current_user": "student01",
  "status": "online"
}

// Hodisa yuz berganda
{
  "type": "event",
  "agent_id": "uuid",
  "event": "app_blocked",
  "details": {"process": "game.exe", "pid": 1234}
}

// Buyruq natijasi
{
  "type": "command_result",
  "command_id": "uuid",
  "success": true,
  "data": {}
}
```

### Server → Agent

```json
// Siyosat yangilanishi
{
  "type": "policy_update",
  "policies": [
    {"id": "uuid", "type": "internet", "config": {...}},
    {"id": "uuid", "type": "application", "config": {...}}
  ]
}

// Buyruq
{
  "type": "command",
  "command_id": "uuid",
  "action": "take_screenshot",
  "payload": {}
}

// Xabar
{
  "type": "message",
  "message_id": "uuid",
  "title": "E'tibor!",
  "body": "10 daqiqada sinov boshlanadi",
  "severity": "warning"
}
```

---

# 6. MODULLAR

## 6.1 Internet nazorati moduli

**Ishlash prinsipi:**

1. Agent Windows DNS sozlamalarini o'zgartiradi (loopback ga yo'naltiradi)
2. Agent kompyuterda minimal HTTP proksi ishlatadi (port 8877)
3. Proksi har bir so'rovni siyosat bilan tekshiradi
4. Ruxsat etilmagan domenlar → bloklash sahifasiga yo'naltiradi
5. Barcha kirish urinishlari logga yoziladi

**Whitelist rejimi (standart):**
- Faqat `allowed_domains` dagi domenlar o'tadi
- Wildcard qo'llab-quvvatlanadi: `*.python.org`
- HTTPS uchun SNI (Server Name Indication) ishlatiladi
- Bloklangan urinish → audit log + (agar sozlangan bo'lsa) admin notifikatsiyasi

**Blacklist rejimi:**
- Barcha saytlar ochiq
- Faqat `blocked_domains` bloklanadi

**Cheklov:** Bu modul faqat browser trafikni nazorat qiladi (HTTP/HTTPS). VPN, tunnel orqali chetlab o'tish mumkin. Chuqur nazorat uchun qo'shimcha Windows Firewall qoidalari qo'llanilishi tavsiya etiladi.

## 6.2 Dastur nazorati moduli

**Ishlash prinsipi:**

1. Agent Windows event log'larini kuzatadi (WMI: Win32_ProcessStartTrace)
2. Yangi jarayon boshlanganida — siyosat bilan tekshiradi
3. Ruxsat etilmagan jarayon → darhol to'xtatadi (TerminateProcess)
4. Buyruqlar qatori (cmd.exe, powershell.exe) — alohida siyosat
5. Setup/installer fayllar (.exe, .msi, .msix) — bloklanadi

**Whitelist tekshiruvi:**
- Jarayon nomi (process name) bo'yicha
- Fayl joylashuvi (path) bo'yicha (ixtiyoriy, qo'shimcha xavfsizlik)
- Digital signature (imzo) bo'yicha (ilg'or rejim)

**Logga yoziladi:**
- Jarayon nomi
- To'liq yo'l
- Foydalanuvchi nomi
- Vaqt
- Bloklandi/ruxsat berildi

## 6.3 USB nazorati moduli

**Ishlash prinsipi:**

Windows Registry orqali USB boshqaruvi:

```
HKLM\SYSTEM\CurrentControlSet\Services\USBSTOR
  Start = 4   (disabled — to'liq blok)
  Start = 3   (enabled — oq ro'yxat rejimi)
```

**Rejimlar:**
1. **To'liq blok:** USB storage qurilmalari umuman ishlamaydi
2. **Oq ro'yxat:** Faqat VID:PID (Vendor ID : Product ID) ro'yxatidagi qurilmalar
3. **Erkin:** USB ochiq, faqat log yoziladi

**Ulanganda/uzilganda:**
- WMI event (Win32_DeviceChangeEvent) ushlaydi
- Qurilma ma'lumotlari (VID, PID, serial number) logga yoziladi
- Agar blok rejimda bo'lsa — qurilma darhol disabled qilinadi
- Admin xabardor qilinadi (agar sozlangan)

## 6.4 Screen monitoring moduli

**Screenshot olish:**
- `mss` kutubxonasi ishlatiladi (tez va samarali)
- Sifat: 70% JPEG siqish (fayl hajmini kamaytirish)
- Maksimal razreshenie: 1920x1080 (kattasi kichraytirилади)
- Interval: 5/10/30/60 soniya (sozlanadi)

**Thumbnail ko'rinish (Admin Desktop):**
- Grid: 4x5 (20 kompyuter bir sahifada)
- Thumbnail hajmi: 320x180 px
- Yangilanish: siyosat intervalida

**To'liq ekran ko'rinish:**
- Admin bir kompyuterni tanlaydi
- Server agentdan yangi screenshot so'raydi
- 3 soniyadan kam vaqtda keladi
- Zoom (150%, 200%) qo'llab-quvvatlanadi

**Saqlash siyosati:**
- Screenshotlar serverda 30 kun saqlanadi
- Undan keyin avtomatik o'chiriladi (Celery task)
- Papka strukturasi: `/screenshots/YYYY/MM/DD/{computer_id}/`

## 6.5 Xabar tizimi moduli

**Turlari va ko'rinishi:**

| Tur | Rang | O'quvchi ekranida | Log severity |
|-----|------|-------------------|--------------|
| Info | Ko'k | Oddiy notification | info |
| Warning | Sariq | Katta oyna, "OK" tugma | warning |
| Critical | Qizil | Modal, to'liq ekran | critical |

**Yuborish manzili:**
- Bitta kompyuter: `target_type = 'computer'`
- Guruh: `target_type = 'group'`
- Hammaga: `target_type = 'all'`

**Delivery tracking:**
- Xabar yuborildi → `sent`
- Agent qabul qildi → `delivered`
- O'quvchi ko'rdi (oyna yopildi) → `read`

## 6.6 Audit log moduli

**Yoziladigan hodisalar:**

| Hodisa | event_type | severity |
|--------|-----------|----------|
| Tizimga kirish | `user_login` | info |
| Tizimdan chiqish | `user_logout` | info |
| Muvaffaqiyatsiz kirish | `login_failed` | warning |
| Dastur bloklandi | `app_blocked` | warning |
| Saytga kirish bloklandi | `web_blocked` | info |
| USB ulandi | `usb_connected` | info |
| USB bloklandi | `usb_blocked` | warning |
| Chop etildi | `print_job` | info |
| Kompyuter bloklandi | `computer_locked` | info |
| Siyosat o'zgartirildi | `policy_changed` | warning |
| Administrator harakati | `admin_action` | info |
| Agent offline | `agent_offline` | warning |
| Noma'lum xato | `error` | critical |

**Muhim qoidalar:**
- Audit log hech qachon o'chirilmaydi (immutable)
- Hech kim (super_admin ham) eski loglarni o'chira olmaydi
- Loglar PostgreSQL partitioning bilan yillar bo'yicha saqlanadi
- Eksport: CSV, PDF

## 6.7 Hisobotlar moduli

**Hisobot turlari:**

### Kunlik hisobot
- Jami online/offline vaqt (har bir kompyuter)
- Bloklangan saytlar ro'yxati (eng ko'p 10 ta)
- Bloklangan dasturlar
- USB ulanish urinishlari
- Chop etilgan hujjatlar

### Haftalik hisobot
- Faollik grafigi (haftaning har kuni)
- Eng faol/passiv kompyuterlar
- Internet statistikasi (domenlar bo'yicha)
- Xavfsizlik hodisalari xulasasi

### Oylik hisobot
- Oylik tarendlar
- Qoidabuzarlik statistikasi
- Texnik muammolar (offline vaqtlar)
- Admin harakatlari logi

**Eksport formatlari:**
- **PDF:** Logotip, sarlavha, jadval, grafiklar (ReportLab)
- **Excel:** Har bir bo'lim alohida varaq (openpyxl)
- **CSV:** Raw ma'lumotlar, boshqa tizimlar uchun

---

# 7. XAVFSIZLIK

## 7.1 Autentifikatsiya

**Parollar:**
- Argon2id algoritmi (eng zamonaviy, brute-force ga chidamli)
- Parametrlar: memory=64MB, iterations=3, parallelism=4
- Minimal parol talabi: 8 belgi, katta/kichik harf, raqam

**JWT Tokenlar:**
- Access token: 15 daqiqa
- Refresh token: 7 kun
- Refresh token rotation (har safar yangi token beriladi)
- Token revocation: Redis blacklist

**Sessiya xavfsizligi:**
- Bir foydalanuvchi — maksimal 3 ta aktiv sessiya
- Noma'lum joylashuvdan kirish → tasdiqlash kodi
- 10 marta noto'g'ri parol → 30 daqiqa bloklash

## 7.2 Transport xavfsizligi

- Barcha aloqa HTTPS/WSS (TLS 1.3)
- Self-signed sertifikat (ichki tarmoq uchun) yoki Let's Encrypt
- HTTP → HTTPS redirect (Nginx)
- HSTS header

## 7.3 Agent xavfsizligi

- Server URL va API key agent binary ichida shifrlangan (PyInstaller + obfuscation)
- Agent o'zini o'chirish/to'xtatishdan himoyalangan (Windows Service restart policy)
- Agent fayllarini o'chirish bloklangan (ACL rules)
- Agent konfiguratsiyasi o'zgartirish uchun admin paroli kerak

## 7.4 Ma'lumotlar bazasi xavfsizligi

- PostgreSQL maxsus foydalanuvchi (minimal huquqlar)
- Parollar va maxfiy ma'lumotlar Argon2 bilan saqlanadi
- Backup fayllar AES-256 bilan shifrlangan
- Database faqat localhost'dan ulanish qabul qiladi

## 7.5 Rol asosida kirish nazorati (RBAC)

| Operatsiya | Viewer | Admin | Super Admin |
|------------|--------|-------|-------------|
| Dashboard ko'rish | ✅ | ✅ | ✅ |
| Screenshot ko'rish | ✅ | ✅ | ✅ |
| Kompyuterni boshqarish | ❌ | ✅ | ✅ |
| Siyosat yaratish | ❌ | ✅ | ✅ |
| Foydalanuvchi yaratish | ❌ | ❌ | ✅ |
| Tizim sozlash | ❌ | ❌ | ✅ |
| Audit log ko'rish | ✅ | ✅ | ✅ |
| Audit log o'chirish | ❌ | ❌ | ❌ |

---

# 8. ISHLASH TALABLARI

## 8.1 Javob vaqti (Response Time)

| Operatsiya | Maqsad | Maksimal |
|------------|--------|---------|
| API so'rovi (oddiy) | < 100ms | 500ms |
| Buyruq yetib borishi | < 1s | 2s |
| Screenshot olish | < 2s | 3s |
| Dashboard yangilanishi | real-time (≤1s) | 2s |
| Hisobot generatsiyasi | < 10s | 30s |
| Login | < 300ms | 1s |

## 8.2 Yuklanish (Load)

| Ko'rsatkich | Maqsad |
|-------------|--------|
| Bir vaqtdagi agentlar | 500+ |
| Bir vaqtdagi admin sessiyalar | 20+ |
| Kunlik audit log yozuvlari | 1,000,000+ |
| Screenshot saqlash (oylik) | ~100 GB (500 kompyuter × 30 kun) |

## 8.3 Mavjudlik (Availability)

- Uptime maqsadi: 99.9% (yiliga ~8.7 soat to'xtash ruxsat etiladi)
- Planned maintenance: kechasi 02:00–04:00
- Auto-restart: server crash bo'lsa Nginx va systemd qayta ishga tushiradi
- Health check endpoint: `GET /health` (monitoring uchun)

## 8.4 Serverga tavsiyalar

**Minimal:**
- CPU: 4 core
- RAM: 8 GB
- Disk: 500 GB SSD (screenshotlar uchun)
- Tarmoq: 100 Mbps LAN

**Tavsiya etilgan (500 kompyuter uchun):**
- CPU: 8 core
- RAM: 16 GB
- Disk: 2 TB SSD (RAID 1)
- Tarmoq: 1 Gbps LAN

---

# 9. PAPKALAR STRUKTURASI

```
edu_control_pro/
│
├── server/                         # FastAPI backend
│   ├── app/
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # sozlamalar (env vars)
│   │   ├── database.py             # SQLAlchemy async engine
│   │   ├── models/                 # SQLAlchemy modellari
│   │   │   ├── user.py
│   │   │   ├── computer.py
│   │   │   ├── policy.py
│   │   │   ├── audit_log.py
│   │   │   └── command.py
│   │   ├── schemas/                # Pydantic sxemalar
│   │   │   ├── user.py
│   │   │   ├── computer.py
│   │   │   ├── policy.py
│   │   │   └── command.py
│   │   ├── routers/                # API endpoint'lar
│   │   │   ├── auth.py
│   │   │   ├── computers.py
│   │   │   ├── policies.py
│   │   │   ├── commands.py
│   │   │   ├── reports.py
│   │   │   └── audit.py
│   │   ├── services/               # biznes mantiq
│   │   │   ├── auth_service.py
│   │   │   ├── computer_service.py
│   │   │   ├── policy_service.py
│   │   │   ├── command_service.py
│   │   │   └── report_service.py
│   │   ├── websocket/              # WebSocket hub
│   │   │   ├── manager.py          # ulanishlarni boshqarish
│   │   │   └── handlers.py         # xabarlarni qayta ishlash
│   │   ├── tasks/                  # Celery tasklar
│   │   │   ├── reports.py
│   │   │   └── cleanup.py          # eski screenshotlarni o'chirish
│   │   └── utils/
│   │       ├── security.py         # JWT, Argon2
│   │       └── pagination.py
│   ├── alembic/                    # database migratsiyalar
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── admin_desktop/                  # PySide6 ilovasi
│   ├── main.py                     # kirish nuqtasi
│   ├── app/
│   │   ├── windows/
│   │   │   ├── main_window.py
│   │   │   ├── login_window.py
│   │   │   └── settings_window.py
│   │   ├── widgets/
│   │   │   ├── dashboard_widget.py
│   │   │   ├── computer_list_widget.py
│   │   │   ├── screen_monitor_widget.py
│   │   │   ├── policy_widget.py
│   │   │   ├── audit_widget.py
│   │   │   └── report_widget.py
│   │   ├── services/
│   │   │   ├── api_client.py       # HTTP so'rovlar
│   │   │   └── ws_client.py        # WebSocket
│   │   └── utils/
│   ├── resources/                  # ikonkalar, rasmlar
│   ├── requirements.txt
│   └── build.spec                  # PyInstaller spec
│
├── client_agent/                   # Windows Agent
│   ├── main.py                     # Windows Service kirish nuqtasi
│   ├── agent/
│   │   ├── service.py              # Windows Service
│   │   ├── ws_client.py            # WebSocket aloqa
│   │   ├── modules/
│   │   │   ├── internet_control.py # internet nazorat
│   │   │   ├── app_control.py      # dastur nazorat
│   │   │   ├── usb_control.py      # USB nazorat
│   │   │   ├── screen_monitor.py   # screenshot
│   │   │   ├── print_monitor.py    # chop etish nazorat
│   │   │   └── system_monitor.py   # CPU/RAM/Disk
│   │   ├── policy_engine.py        # siyosatlarni qo'llash
│   │   └── config.py               # server URL, api key
│   ├── requirements.txt
│   └── build.spec                  # PyInstaller spec
│
├── database/
│   ├── migrations/                 # SQL migratsiya fayllari
│   ├── seeds/                      # test ma'lumotlar
│   └── schema.sql                  # to'liq sxema
│
├── installer/
│   ├── server_installer/           # server o'rnatish skripti
│   ├── agent_installer/            # agent MSI paketi
│   └── README.md
│
├── docs/
│   ├── TZ.md                       # bu fayl
│   ├── API.md                      # API hujjatlar
│   ├── INSTALL.md                  # o'rnatish qo'llanma
│   └── USER_MANUAL.md              # foydalanuvchi qo'llanma
│
├── logs/                           # application loglar
├── backups/                        # zaxira nusxalar
├── docker-compose.yml
└── README.md
```

---

# 10. O'RNATISH VA SOZLASH

## 10.1 Server o'rnatish (Ubuntu 22.04)

```bash
# 1. Kerakli paketlar
sudo apt update
sudo apt install python3.12 postgresql redis nginx certbot

# 2. PostgreSQL sozlash
sudo -u postgres createdb educontrol
sudo -u postgres createuser educontrol_user

# 3. Virtual muhit
python3.12 -m venv venv
source venv/bin/activate
pip install -r server/requirements.txt

# 4. Muhit o'zgaruvchilari (.env fayl)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/educontrol
REDIS_URL=redis://localhost:6379
SECRET_KEY=<256-bit random key>
SCREENSHOTS_PATH=/var/educontrol/screenshots

# 5. Database yaratish
alembic upgrade head

# 6. Super admin yaratish
python manage.py create_superadmin

# 7. Systemd service
sudo systemctl enable educontrol-server
sudo systemctl start educontrol-server
```

## 10.2 Agent o'rnatish (Windows)

```batch
# Administrator sifatida ishlatiladi
agent_installer.msi /quiet SERVER_URL=https://server-ip API_KEY=xxxx

# Yoki buyruq qatoridan
python -m client_agent.service install
python -m client_agent.service start
```

## 10.3 Muhit o'zgaruvchilari (server .env)

```ini
# Database
DATABASE_URL=postgresql+asyncpg://educontrol:password@localhost:5432/educontrol

# Redis
REDIS_URL=redis://localhost:6379/0

# Xavfsizlik
SECRET_KEY=very-long-random-secret-key-256-bits
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Fayl saqlash
SCREENSHOTS_PATH=/var/educontrol/screenshots
SCREENSHOTS_RETENTION_DAYS=30
BACKUP_PATH=/var/educontrol/backups

# Email (xabardorlik uchun, ixtiyoriy)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=admin@school.com
SMTP_PASS=password

# Tizim
MAX_AGENTS=500
SCREENSHOT_QUALITY=70
LOG_LEVEL=INFO
```

---

# 11. SINOV TALABLARI

## 11.1 Unit testlar

- Har bir service va utility funksiyasi uchun
- Maqsad: 80%+ code coverage
- Asbob: pytest, pytest-asyncio

## 11.2 Integration testlar

- API endpoint'lar (test database bilan)
- WebSocket aloqa
- Siyosat qo'llash

## 11.3 Load testlar

- 500 ta simulyatsiya qilingan agent
- Asbob: locust
- Maqsad: barcha performance talablar bajarilishi

## 11.4 Security testlar

- SQL injection
- JWT token manipulation
- Unauthorized access urinishlari
- Brute force himoyasi

---

# 12. QABUL QILISH MEZONLARI

Loyiha quyidagi shartlar bajarilganda qabul qilingan hisoblanadi:

### Funksional
- [ ] 500 ta agent bir vaqtda ulana oladi
- [ ] Buyruqlar 2 soniyadan kam vaqtda yetib boradi
- [ ] Screenshot 3 soniyadan kam vaqtda olinadi
- [ ] Internet whitelist/blacklist ishlaydi
- [ ] Dastur bloklash ishlaydi
- [ ] USB nazorat ishlaydi
- [ ] Audit log yoziladi va o'chirib bo'lmaydi
- [ ] Hisobotlar PDF/Excel/CSV da yuklab olinadi

### Texnik
- [ ] Server 24/7 ishlaydi (auto-restart bilan)
- [ ] HTTPS/WSS xavfsiz aloqa
- [ ] Argon2 parol xeshlash
- [ ] JWT sessiya boshqaruvi
- [ ] Zaxira nusxa kundalik ishlaydi
- [ ] Tiklash (restore) 1 klik bilan ishlaydi

### Sifat
- [ ] API hujjatlar (Swagger/ReDoc) mavjud
- [ ] O'rnatish qo'llanmasi yozilgan
- [ ] Foydalanuvchi qo'llanmasi yozilgan
- [ ] Kod GitHub/GitLab da saqlangan

---

*Hujjat EDU Control Pro loyihasi uchun tayyorlangan.*  
*Versiya 1.0 | 2025*
