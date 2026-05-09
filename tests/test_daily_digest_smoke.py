import asyncio
from datetime import date
from pathlib import Path

from ai_intelligence.domain.models import NewsItem
from ai_intelligence.news.fetcher import NewsFetcher
from ai_intelligence.pipelines.daily_digest import DailyDigestPipeline
from ai_intelligence.storage.markdown_store import MarkdownReportStore


class _FakeFetcher(NewsFetcher):
    async def fetch(self, sources=None):  # noqa: ANN001
        return [
            NewsItem(
                title="New multimodal model ships",
                summary="Vision and audio in one API.",
                source_name="Test",
                source_url="https://example.com/a",
            )
        ]


def test_pipeline_writes_markdown(tmp_path: Path) -> None:
    async def _run() -> None:
        store = MarkdownReportStore(base_dir=tmp_path)
        pipeline = DailyDigestPipeline(fetcher=_FakeFetcher(), store=store)
        await pipeline.run(report_date=date(2026, 5, 7))

    asyncio.run(_run())
    out = tmp_path / "2026-05-07.md"
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "AI 情报日报" in text
    assert "多模态" in text


def test_import_public_modules() -> None:
    from ai_intelligence import analysis, domain, news, pipelines, reports, storage  # noqa: F401

    assert domain.NewsItem is not None
