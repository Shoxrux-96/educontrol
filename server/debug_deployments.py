import asyncio, sys
sys.path.insert(0, '.')
import os
os.environ["DATABASE_URL"] = "postgresql+asyncpg://educontrol:educontrol@localhost:5432/educontrol"

from app.database import async_session
from sqlalchemy import text, select
from app.models.computer_management import SoftwareDeployment

async def test():
    async with async_session() as s:
        try:
            r = await s.execute(text('SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = \'software_deployments\')'))
            print('Table exists:', r.scalar())
            r2 = await s.execute(select(SoftwareDeployment).limit(1))
            items = r2.scalars().all()
            print('Items:', len(items))
            for d in items:
                print(f'  id={d.id} name={d.name} status={d.status} target_type={d.target_type}')
                print(f'  package_id={d.package_id} created_at={d.created_at}')
                print(f'  status.value={d.status.value}')
                print(f'  has package: {hasattr(d, "package")}')
        except Exception as e:
            print(f'Error: {type(e).__name__}: {e}')

asyncio.run(test())
