from __future__ import annotations

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.settings import get_channel_ref


class SubscribeCheckError(Exception):
    """Любая проблема проверки подписки (не настройка/нет доступа/канал не найден)."""


class BotNotInChannelError(SubscribeCheckError):
    """Бот не имеет доступа к каналу (не добавлен / не админ / канал приватный)."""


class ChannelNotConfiguredError(SubscribeCheckError):
    """channel_id не задан или задан неверно."""


async def is_user_subscribed(bot: Bot, session: AsyncSession, user_id: int) -> bool:
    channel_ref = await get_channel_ref(session)
    if channel_ref is None:
        raise ChannelNotConfiguredError("channel_id is not configured or invalid")

    try:
        member = await bot.get_chat_member(chat_id=channel_ref, user_id=user_id)
    except TelegramForbiddenError as e:
        raise BotNotInChannelError(
            "Bot has no access to channel. Add bot to channel and give admin rights."
        ) from e
    except TelegramBadRequest as e:
        msg = str(e)
        if "chat not found" in msg.lower():
            raise ChannelNotConfiguredError(
                f"Channel not found. Check channel_id={channel_ref}"
            ) from e
        raise SubscribeCheckError(msg) from e

    return member.status in {"member", "administrator", "creator"}
