#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py migrate

echo "Creating default super admin and seed data..."
python -c "
import asyncio, uuid
from app.database import async_session
from app.models.user import User, UserRole
from app.models.computer import Computer, ComputerGroup
from app.models.policy import Policy, PolicyAssignment
from app.utils.security import hash_password
from sqlalchemy import select

async def seed():
    async with async_session() as session:
        # Admin
        result = await session.execute(select(User).where(User.username == 'admin'))
        if not result.scalar_one_or_none():
            user = User(
                username='admin',
                email='admin@educontrol.local',
                password_hash=hash_password('Admin123!'),
                role=UserRole.super_admin,
                full_name='System Administrator',
            )
            session.add(user)
            await session.commit()
            print('Default admin created (admin / Admin123!)')

        # Groups
        groups = {}
        for name, color, desc in [
            ('1-Qator', '#3498db', 'Birinchi qator kompyuterlari'),
            ('2-Qator', '#2ecc71', 'Ikkinchi qator kompyuterlari'),
            ('3-Qator', '#e74c3c', 'Uchinchi qator kompyuterlari'),
        ]:
            result = await session.execute(select(ComputerGroup).where(ComputerGroup.name == name))
            g = result.scalar_one_or_none()
            if not g:
                g = ComputerGroup(name=name, color=color, description=desc)
                session.add(g)
                await session.commit()
            groups[name] = g

        # Computers
        comps = [
            ('PC-001', 'DESKTOP-001', '192.168.1.101', '1-Qator'),
            ('PC-002', 'DESKTOP-002', '192.168.1.102', '1-Qator'),
            ('PC-003', 'DESKTOP-003', '192.168.1.103', '1-Qator'),
            ('PC-004', 'DESKTOP-004', '192.168.1.104', '2-Qator'),
            ('PC-005', 'DESKTOP-005', '192.168.1.105', '2-Qator'),
        ]
        for name, hostname, ip, gname in comps:
            result = await session.execute(select(Computer).where(Computer.name == name))
            if not result.scalar_one_or_none():
                c = Computer(
                    name=name, hostname=hostname, ip_address=ip,
                    group_id=groups[gname].id,
                    status='online' if name != 'PC-003' else 'offline',
                    cpu_usage=23, ram_usage=45, disk_usage=67,
                    current_user='student' if name != 'PC-003' else None,
                )
                session.add(c)
        await session.commit()
        print('Seed data created')
asyncio.run(seed())
"

echo "Starting: $@"
exec "$@"
