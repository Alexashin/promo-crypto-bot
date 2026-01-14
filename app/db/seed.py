from sqlalchemy import select

from app.db.models import SettingsRow
from app.db.session import get_sessionmaker
from app.config import settings


async def ensure_settings_row() -> None:
    SessionLocal = get_sessionmaker()
    async with SessionLocal() as session:
        res = await session.execute(select(SettingsRow).where(SettingsRow.id == 1))
        row = res.scalar_one_or_none()
        if row is None:
            row = SettingsRow(
                id=1,
                inactive_hours=settings.default_inactive_hours,
                max_reminders=settings.default_max_reminders,
            )
            session.add(row)
            await session.commit()
