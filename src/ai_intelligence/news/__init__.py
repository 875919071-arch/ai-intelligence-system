"""全球 AI 新闻抓取：数据源注册、HTTP/RSS 聚合入口。"""

from ai_intelligence.news.fetcher import NewsFetcher, NewsFetcherProtocol

__all__ = ["NewsFetcher", "NewsFetcherProtocol"]
