"""将新闻归类到 Agent、多模态、AI Companion 等方向。"""

from ai_intelligence.domain.models import NewsItem, ThemeCategory


# 极简关键词规则占位；后续可替换为向量检索或 LLM 分类。
_KEYWORDS: dict[ThemeCategory, tuple[str, ...]] = {
    ThemeCategory.AGENT: ("agent", "agents", "tool use", "autonomous", "orchestration"),
    ThemeCategory.MULTIMODAL: ("multimodal", "vision", "audio", "video", "image", "speech"),
    ThemeCategory.AI_COMPANION: ("companion", "character", "personalized", "chatbot", "copilot"),
}


class ThemeClassifier:
    """按标题/摘要做轻量主题识别。"""

    def classify(self, items: list[NewsItem]) -> dict[ThemeCategory, list[NewsItem]]:
        buckets: dict[ThemeCategory, list[NewsItem]] = {k: [] for k in ThemeCategory}
        for item in items:
            text = f"{item.title} {item.summary}".lower()
            matched = ThemeCategory.GENERAL
            for theme, kws in _KEYWORDS.items():
                if any(kw in text for kw in kws):
                    matched = theme
                    break
            buckets[matched].append(item)
        return buckets
