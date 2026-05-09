#!/usr/bin/env python3
"""本地执行：跑通「抓取 → 分析 → 中文日报 → Markdown 落盘」流水线。"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# 从仓库根目录以 `python scripts/run_daily_digest.py` 运行时补齐 src 路径
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ai_intelligence.pipelines.daily_digest import DailyDigestPipeline  # noqa: E402


async def main() -> None:
    pipeline = DailyDigestPipeline()
    await pipeline.run()
    print("Daily digest finished. Check output/daily_reports/ (or DAILY_REPORT_OUTPUT_DIR).")


if __name__ == "__main__":
    asyncio.run(main())
