from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ThemeCategory(StrEnum):
    """与产品关注方向对齐的主题分类。"""

    AGENT = "agent"
    MULTIMODAL = "multimodal"
    AI_COMPANION = "ai_companion"
    GENERAL = "general"


class NewsItem(BaseModel):
    """单条新闻（抓取层标准化后的结构）。"""

    title: str
    summary: str = ""
    source_name: str = ""
    source_url: str = ""
    published_at: datetime | None = None
    language: str = ""
    raw: dict[str, Any] = Field(default_factory=dict)


class TrendSignal(BaseModel):
    """趋势分析输出的结构化信号（后续可由 LLM 或规则填充）。"""

    headline: str
    detail: str = ""
    related_news_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class DailyReportPayload(BaseModel):
    """中文日报生成前的中间表示。"""

    report_date: date
    trends: list[TrendSignal] = Field(default_factory=list)
    by_theme: dict[ThemeCategory, list[NewsItem]] = Field(default_factory=dict)
    executive_summary_zh: str = ""
