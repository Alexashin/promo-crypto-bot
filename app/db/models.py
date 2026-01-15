from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_registered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    registered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    reminder_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_reminder_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(String(512), nullable=False)


class MediaType(PyEnum):
    voice = "voice"
    audio = "audio"
    photo = "photo"
    video = "video"
    document = "document"
    video_note = "video_note"


class PostTemplate(Base):
    """
    CMS-единица контента.
    key: welcome / not_subscribed / podcast_1 / reminder_1 ...
    text: текст / caption
    media_type + file_id: опционально
    buttons: JSON массив кнопок (url/callback)
    """

    __tablename__ = "post_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    key: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )

    text: Mapped[str | None] = mapped_column(Text, nullable=True)

    media_type: Mapped[MediaType | None] = mapped_column(
        Enum(MediaType, name="media_type"),
        nullable=True,
    )
    file_id: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # buttons пример:
    # [
    #   {"text": "Перейти в канал", "url": "https://t.me/..."},
    #   {"text": "Проверить подписку", "callback": "check_sub"},
    #   {"text": "Я зарегистрировался", "callback": "registered"}
    # ]
    buttons: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
