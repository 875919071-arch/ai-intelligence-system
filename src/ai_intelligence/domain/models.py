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


class MealSlot(StrEnum):
    """一天中的餐别。"""

    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"


class BudgetLevel(StrEnum):
    """用户愿意接受的单餐预算档位。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HealthGoal(StrEnum):
    """第一版支持的饮食目标。"""

    BALANCED = "balanced"
    LIGHT = "light"
    HIGH_PROTEIN = "high_protein"
    COMFORT = "comfort"


class DiningMode(StrEnum):
    """做饭或外食偏好。"""

    ANY = "any"
    COOK = "cook"
    EAT_OUT = "eat_out"


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


class MealOption(BaseModel):
    """可被推荐的一餐候选项。"""

    id: str
    name: str
    slot: MealSlot
    cuisine: str
    budget: BudgetLevel
    dining_modes: list[DiningMode]
    health_tags: list[HealthGoal] = Field(default_factory=list)
    flavor_tags: list[str] = Field(default_factory=list)
    avoid_tags: list[str] = Field(default_factory=list)
    prep_minutes: int = Field(ge=0)
    description: str = ""


class MealRecommendation(BaseModel):
    """推荐给用户的一餐。"""

    meal: MealOption
    reason: str
    score: float
    matched_preferences: list[str] = Field(default_factory=list)
