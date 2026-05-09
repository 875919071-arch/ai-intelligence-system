"""每日情报流水线编排。"""

from datetime import date

from ai_intelligence.news.fetcher import NewsFetcher
from ai_intelligence.reports.daily import DailyReportBuilder
from ai_intelligence.reports.markdown import render_daily_report_markdown
from ai_intelligence.storage.markdown_store import MarkdownReportStore


class DailyDigestPipeline:
    """抓取全球 AI 新闻，分析趋势与主题，生成中文 Markdown 日报并保存。"""

    def __init__(
        self,
        fetcher: NewsFetcher | None = None,
        builder: DailyReportBuilder | None = None,
        store: MarkdownReportStore | None = None,
    ) -> None:
        self._fetcher = fetcher or NewsFetcher()
        self._builder = builder or DailyReportBuilder()
        self._store = store or MarkdownReportStore()

    async def run(self, report_date: date | None = None) -> str:
        day = report_date or date.today()
        items = await self._fetcher.fetch()
        payload = self._builder.build(items, report_date=day)
        md = render_daily_report_markdown(payload)
        self._store.save_daily(day.isoformat(), md)
        return md
