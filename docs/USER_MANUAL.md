# EDU Control Pro - Foydalanuvchi qo'llanmasi

## Tizimga kirish

1. Admin Desktop dasturini ishga tushiring
2. Foydalanuvchi nomi va parolni kiriting
3. "Kirish" tugmasini bosing

## Asosiy imkoniyatlar

### Dashboard
- Kompyuterlarning umumiy holati (online/offline soni)
- Ogohlantirishlar
- Real-time statistik ma'lumotlar

### Kompyuterlar ro'yxati
- Barcha kompyuterlarni jadval ko'rinishida ko'rish
- Status bo'yicha filtrlash (Online, Offline, Locked)
- Qidirish (nomi yoki IP bo'yicha)
- Kompyuterga buyruq yuborish

### Screen Monitoring
- Online kompyuterlarning thumbnail ko'rinishi
- Real-time yangilanish
- To'liq ekran ko'rinishi (kompyuterni tanlash orqali)

### Siyosatlar
- Internet whitelist/blacklist yaratish
- Dastur cheklovlari
- USB qurilma boshqaruvi
- Siyosatlarni kompyuter yoki guruhga tayinlash

### Audit Log
- Barcha hodisalarni ko'rish
- Muhimlik darajasi bo'yicha filtrlash
- Hodisa turi bo'yicha qidirish

### Hisobotlar
- Kunlik/haftalik/oylik hisobotlar
- PDF, Excel, CSV formatlarida eksport
- Avtomatik generatsiya

## Buyruqlar turlari

| Buyruq | Tavsif |
|--------|--------|
| lock_screen | Kompyuter ekranini bloklash |
| unlock_screen | Blokni ochish |
| take_screenshot | Screenshot olish |
| send_message | Xabar yuborish |
| restart | Kompyuterni qayta yuklash |
| shutdown | Kompyuterni o'chirish |
| kill_process | Jarayonni to'xtatish |
| open_app | Dastur ochish |

## Tez-tez so'raladigan savollar

**Agent kompyuterda ko'rinmayapti?**
Windows Service sifatida ishlaydi. Task Manager da "EDUControlAgent" nomi bilan ko'rinadi.

**Internet bloklandi, qanday ochish mumkin?**
Admin Desktop orqali internet siyosatini o'zgartiring yoki o'chiring.

**Screenshot olinmayapti?**
Agentning `screenshot_interval` sozlamasini tekshiring. Kamida 5 soniya bo'lishi kerak.

**Hisobot qayerda saqlanadi?**
Serverning `backups/reports/` papkasida. Admin Desktop orqali yuklab olish mumkin.
