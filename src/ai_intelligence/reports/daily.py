"""将分析结果组装为 DailyReportPayload。"""

from datetime import date

from ai_intelligence.domain.models import DailyReportPayload, NewsItem, TrendSignal
from ai_intelligence.analysis.themes import ThemeClassifier
from ai_intelligence.analysis.trends import TrendAnalyzer


class DailyReportBuilder:
    """串联趋势分析与主题分桶，生成日报载荷。"""

    def __init__(
        self,
        trend_analyzer: TrendAnalyzer | None = None,
        theme_classifier: ThemeClassifier | None = None,
    ) -> None:
        self._trends = trend_analyzer or TrendAnalyzer()
        self._themes = theme_classifier or ThemeClassifier()

    def build(
        self,
        items: list[NewsItem],
        report_date: date | None = None,
        executive_summary_zh: str = "",
    ) -> DailyReportPayload:
        day = report_date or date.today()
        trends: list[TrendSignal] = self._trends.analyze(items)
        by_theme = self._themes.classify(items)
        return DailyReportPayload(
            report_date=day,
            trends=trends,
            by_theme=by_theme,
            executive_summary_zh=executive_summary_zh,
        )
