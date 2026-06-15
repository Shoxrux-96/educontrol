#!/usr/bin/env python3
import asyncio
import sys
from app.database import async_session
from app.models.user import User, UserRole
from app.utils.security import hash_password


async def create_superadmin():
    username = input("Username [admin]: ").strip() or "admin"
    email = input("Email [admin@educontrol.local]: ").strip() or "admin@educontrol.local"
    password = input("Password [Admin123!]: ").strip() or "Admin123!"
    full_name = input("Full name [System Administrator]: ").strip() or "System Administrator"

    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            print(f"User '{username}' already exists!")
            return

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.super_admin,
            full_name=full_name,
        )
        session.add(user)
        await session.commit()
        print(f"Super admin '{username}' created successfully!")


def migrate():
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Database migrated successfully!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py [create_superadmin|migrate]")
        sys.exit(1)

    action = sys.argv[1]
    if action == "create_superadmin":
        asyncio.run(create_superadmin())
    elif action == "migrate":
        migrate()
    else:
        print(f"Unknown action: {action}")
