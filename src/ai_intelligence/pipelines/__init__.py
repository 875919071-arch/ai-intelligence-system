"""端到端流水线：抓取 → 分析 → 日报 → 落盘。"""

from ai_intelligence.pipelines.daily_digest import DailyDigestPipeline

__all__ = ["DailyDigestPipeline"]
