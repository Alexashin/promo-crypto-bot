from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    registered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    reminder_step: Mapped[int] = mapped_column(Integer, default=0)
    last_reminder_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)


class SettingsRow(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)

    subscribe_channel: Mapped[str] = mapped_column(String(255), default="@your_channel")
    register_url: Mapped[str] = mapped_column(String(1024), default="https://example.com")
    consult_url: Mapped[str] = mapped_column(String(1024), default="https://t.me/username")

    inactive_hours: Mapped[int] = mapped_column(Integer, default=48)
    max_reminders: Mapped[int] = mapped_column(Integer, default=5)


class Post(Base):
    """Один пост = одна строка: text + (опц.) медиа + (опц.) ссылочная кнопка."""
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    title: Mapped[str | None] = mapped_column(String(128), nullable=True)

    text: Mapped[str | None] = mapped_column(Text, nullable=True)

    media_type: Mapped[str | None] = mapped_column(String(32), nullable=True)  # voice/photo/video/document/video_note
    media_file_id: Mapped[str | None] = mapped_column(String(512), nullable=True)

    link_text: Mapped[str | None] = mapped_column(String(64), nullable=True)
    link_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
