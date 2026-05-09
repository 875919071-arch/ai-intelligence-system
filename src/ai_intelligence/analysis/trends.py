"""基于新闻列表提取趋势信号。后续可接入 LLM 或统计方法。"""

from ai_intelligence.domain.models import NewsItem, TrendSignal


class TrendAnalyzer:
    """趋势分析占位实现。"""

    def analyze(self, items: list[NewsItem]) -> list[TrendSignal]:
        if not items:
            return []
        # TODO: 调用 LLM 或关键词聚合生成 TrendSignal
        return []
