"""将 Markdown 内容写入约定目录。"""

from pathlib import Path

from ai_intelligence.config import get_settings


class MarkdownReportStore:
    """按日期写入 `output/daily_reports/YYYY-MM-DD.md`（路径可由配置覆盖）。"""

    def __init__(self, base_dir: Path | None = None) -> None:
        settings = get_settings()
        self._base = base_dir or settings.daily_report_output_dir

    def save_daily(self, report_date_iso: str, markdown_body: str) -> Path:
        self._base.mkdir(parents=True, exist_ok=True)
        path = self._base / f"{report_date_iso}.md"
        path.write_text(markdown_body, encoding="utf-8")
        return path
