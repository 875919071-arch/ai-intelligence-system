"""将 DailyReportPayload 渲染为 Markdown 正文。"""

from ai_intelligence.domain.models import DailyReportPayload, ThemeCategory

_THEME_TITLES_ZH: dict[ThemeCategory, str] = {
    ThemeCategory.AGENT: "Agent 与自动化",
    ThemeCategory.MULTIMODAL: "多模态",
    ThemeCategory.AI_COMPANION: "AI Companion",
    ThemeCategory.GENERAL: "综合与其他",
}


def render_daily_report_markdown(payload: DailyReportPayload) -> str:
    lines: list[str] = [
        f"# AI 情报日报 — {payload.report_date.isoformat()}",
        "",
    ]
    if payload.executive_summary_zh:
        lines.extend(["## 摘要", "", payload.executive_summary_zh.strip(), ""])

    lines.extend(["## 趋势要点", ""])
    if payload.trends:
        for t in payload.trends:
            lines.append(f"- **{t.headline}** — {t.detail}".rstrip(" —"))
    else:
        lines.append("_（暂无趋势信号，待分析模块接入后填充）_")
    lines.append("")

    lines.append("## 分主题动态")
    lines.append("")
    for theme, title_zh in _THEME_TITLES_ZH.items():
        items = payload.by_theme.get(theme, [])
        lines.append(f"### {title_zh}")
        if not items:
            lines.append("_（本日无归类条目）_")
        else:
            for it in items:
                link = str(it.source_url) if it.source_url else ""
                suffix = f" [{it.source_name}]({link})" if link else f" _{it.source_name}_"
                lines.append(f"- {it.title}{suffix}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"
