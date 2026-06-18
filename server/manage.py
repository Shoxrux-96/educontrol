#!/usr/bin/env python3
import asyncio
import sys
from sqlalchemy import select

from app.database import async_session
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.utils.security import hash_password


async def create_owner():
    username = input("Username [admin]: ").strip() or "admin"
    email = input("Email [admin@educontrol.local]: ").strip() or "admin@educontrol.local"
    password = input("Password [Admin123!]: ").strip() or "Admin123!"
    full_name = input("Full name [System Owner]: ").strip() or "System Owner"
    org_name = input("Organization name [EDU Control]: ").strip() or "EDU Control"
    org_slug = input("Organization slug [edu-control]: ").strip() or "edu-control"

    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            print(f"User '{username}' already exists!")
            return

        result = await session.execute(select(Organization).where(Organization.slug == org_slug))
        org = result.scalar_one_or_none()
        if not org:
            org = Organization(
                name=org_name,
                slug=org_slug,
                contact_email=email,
            )
            session.add(org)
            await session.flush()

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.owner,
            full_name=full_name,
            organization_id=org.id,
        )
        session.add(user)
        await session.commit()
        print(f"Owner '{username}' created successfully!")
        print(f"Organization: {org.name} (slug: {org.slug})")


async def create_organization():
    name = input("Organization name: ").strip()
    slug = input("Organization slug: ").strip()
    if not name or not slug:
        print("Name and slug required!")
        return

    async with async_session() as session:
        result = await session.execute(select(Organization).where(Organization.slug == slug))
        if result.scalar_one_or_none():
            print(f"Organization '{slug}' already exists!")
            return
        org = Organization(name=name, slug=slug)
        session.add(org)
        await session.commit()
        print(f"Organization '{name}' created successfully!")


def migrate():
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Database migrated successfully!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py [create_owner|create_org|migrate]")
        sys.exit(1)

    action = sys.argv[1]
    if action == "create_owner":
        asyncio.run(create_owner())
    elif action == "create_org":
        asyncio.run(create_organization())
    elif action == "migrate":
        migrate()
    else:
        print(f"Unknown action: {action}")
