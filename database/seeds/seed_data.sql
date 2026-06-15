-- EDU Control Pro - Test ma'lumotlar
-- Ishlatish: psql -U educontrol -d educontrol -f seed_data.sql

-- NOTE: Super admin server ishga tushganda manage.py orqali yaratiladi
-- Test guruhlar
INSERT INTO computer_groups (name, description, color)
VALUES ('1-Qator', 'Birinchi qator kompyuterlari', '#3498db'),
       ('2-Qator', 'Ikkinchi qator kompyuterlari', '#2ecc71'),
       ('3-Qator', 'Uchinchi qator kompyuterlari', '#e74c3c')
ON CONFLICT DO NOTHING;

-- Test kompyuterlar
INSERT INTO computers (name, hostname, ip_address, mac_address, group_id, os_version, agent_version, status, cpu_usage, ram_usage, disk_usage, current_user)
VALUES
    ('PC-001', 'DESKTOP-001', '192.168.1.101', 'AA:BB:CC:DD:EE:01', (SELECT id FROM computer_groups WHERE name='1-Qator'), 'Windows 11 Pro', '1.0.0', 'online', 23, 45, 67, 'student01'),
    ('PC-002', 'DESKTOP-002', '192.168.1.102', 'AA:BB:CC:DD:EE:02', (SELECT id FROM computer_groups WHERE name='1-Qator'), 'Windows 11 Pro', '1.0.0', 'online', 45, 78, 55, 'student02'),
    ('PC-003', 'DESKTOP-003', '192.168.1.103', 'AA:BB:CC:DD:EE:03', (SELECT id FROM computer_groups WHERE name='1-Qator'), 'Windows 10 Pro', '1.0.0', 'offline', 0, 0, 0, NULL),
    ('PC-004', 'DESKTOP-004', '192.168.1.104', 'AA:BB:CC:DD:EE:04', (SELECT id FROM computer_groups WHERE name='2-Qator'), 'Windows 11 Pro', '1.0.0', 'online', 12, 34, 80, 'student03'),
    ('PC-005', 'DESKTOP-005', '192.168.1.105', 'AA:BB:CC:DD:EE:05', (SELECT id FROM computer_groups WHERE name='2-Qator'), 'Windows 10 Pro', '1.0.0', 'locked', 5, 20, 44, 'student04')
ON CONFLICT DO NOTHING;

-- Test siyosatlar
INSERT INTO policies (name, description, policy_type, config, created_by)
VALUES
    ('Standart Internet', 'Oquvchilar uchun ruxsat etilgan saytlar', 'internet',
     '{"mode": "whitelist", "allowed_domains": ["github.com", "python.org", "w3schools.com", "*.google.com"], "blocked_domains": [], "log_attempts": true}',
     (SELECT id FROM users WHERE username='admin')),
    ('Dastur cheklovi', 'Faqat oquv dasturlariga ruxsat', 'application',
     '{"mode": "whitelist", "allowed_apps": [{"name": "VS Code", "exe": "Code.exe"}, {"name": "Chrome", "exe": "chrome.exe"}, {"name": "PyCharm", "exe": "pycharm64.exe"}], "kill_on_detect": true, "block_installers": true}',
     (SELECT id FROM users WHERE username='admin')),
    ('USB Blok', 'USB qurilmalarni bloklash', 'usb',
     '{"mode": "block_all", "log_connections": true, "notify_admin": true}',
     (SELECT id FROM users WHERE username='admin'))
ON CONFLICT DO NOTHING;

-- Siyosat tayinlash (hammaga)
INSERT INTO policy_assignments (policy_id, target_type, target_id, assigned_by)
SELECT id, 'all', NULL, (SELECT id FROM users WHERE username='admin')
FROM policies
ON CONFLICT DO NOTHING;

-- Test audit log
INSERT INTO audit_logs (event_type, severity, description, metadata)
VALUES
    ('user_login', 'info', 'Admin tizimga kirdi', '{"ip": "192.168.1.100"}'),
    ('app_blocked', 'warning', 'game.exe bloklandi', '{"process": "game.exe", "pid": 1234}'),
    ('web_blocked', 'info', 'facebook.com ga kirish bloklandi', '{"domain": "facebook.com"}'),
    ('usb_connected', 'info', 'USB qurilma ulandi', '{"vid": "0781", "pid": "5583"}');
