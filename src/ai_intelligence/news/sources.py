"""新闻源清单（RSS / 站点入口）。后续可改为数据库或远程配置。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class NewsSource:
    """单个新闻源定义。"""

    name: str
    feed_url: str
    language: str = "en"


# 占位：上线前请替换为稳定可抓取的 RSS，并遵守各站点 ToS / robots。
DEFAULT_AI_NEWS_SOURCES: tuple[NewsSource, ...] = (
    NewsSource(name="OpenAI News", feed_url="https://openai.com/blog/rss.xml", language="en"),
    NewsSource(
        name="MIT Technology Review — AI",
        feed_url="https://www.technologyreview.com/topic/artificial-intelligence/feed/",
        language="en",
    ),
)
