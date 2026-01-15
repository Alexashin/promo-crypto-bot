from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.scheduler.jobs import reminders_job


def build_scheduler(bot, interval_minutes: int = 10) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(reminders_job, "interval", minutes=interval_minutes, args=[bot])
    return scheduler
