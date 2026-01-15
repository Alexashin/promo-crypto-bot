from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str = Field(alias="BOT_TOKEN")
    admin_ids: str = Field(default="", alias="ADMIN_IDS")

    database_url: str = Field(alias="DATABASE_URL")

    channel_id: str = Field(alias="CHANNEL_ID")  # "@channel" или "-100..."
    channel_url: str = Field(alias="CHANNEL_URL")  # "https://t.me/..."

    default_inactive_hours: int = Field(default=48, alias="DEFAULT_INACTIVE_HOURS")
    default_max_reminders: int = Field(default=5, alias="DEFAULT_MAX_REMINDERS")

    @property
    def admin_id_set(self) -> set[int]:
        ids: list[int] = []
        for part in (self.admin_ids or "").replace(" ", "").split(","):
            if part:
                ids.append(int(part))
        return set(ids)


settings = Settings()
