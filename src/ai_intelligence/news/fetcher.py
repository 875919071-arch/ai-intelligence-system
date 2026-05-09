"""从配置的源抓取并归一化为 NewsItem。实现可在后续迭代中补全。"""

from typing import Protocol

from ai_intelligence.domain.models import NewsItem
from ai_intelligence.news.sources import DEFAULT_AI_NEWS_SOURCES, NewsSource


class NewsFetcherProtocol(Protocol):
    async def fetch(self, sources: tuple[NewsSource, ...] | None = None) -> list[NewsItem]: ...


class NewsFetcher:
    """默认抓取器：当前返回空列表，占位供流水线联调。"""

    async def fetch(self, sources: tuple[NewsSource, ...] | None = None) -> list[NewsItem]:
        _ = sources or DEFAULT_AI_NEWS_SOURCES
        # TODO: httpx 拉取 RSS，xml.etree 或专用库解析，映射为 NewsItem
        return []
