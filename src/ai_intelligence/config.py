from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    daily_report_output_dir: Path = Field(
        default=Path("output/daily_reports"),
        description="中文日报 Markdown 输出目录（相对当前工作目录）",
    )


def get_settings() -> Settings:
    return Settings()
