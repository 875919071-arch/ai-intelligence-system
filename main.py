#!/usr/bin/env python3
"""项目入口：可选抓取 → OpenAI 分析 → Markdown 日报（reports/daily）。"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _run_script(rel: str, *extra_args: str) -> int:
    path = ROOT / rel
    if not path.is_file():
        print(f"错误：缺少脚本 {path}", file=sys.stderr)
        return 1
    env = os.environ.copy()
    src = str(ROOT / "src")
    prev = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src if not prev else f"{src}{os.pathsep}{prev}"
    cmd = [sys.executable, str(path), *extra_args]
    return subprocess.call(cmd, cwd=str(ROOT), env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description="运行 AI 情报流水线")
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="不执行 fetch_news.py（若存在）",
    )
    parser.add_argument(
        "--skip-analyze",
        action="store_true",
        help="不调用 OpenAI，仅生成日报（需已有分析 JSON）",
    )
    parser.add_argument(
        "--skip-report",
        action="store_true",
        help="不生成 Markdown",
    )
    args = parser.parse_args()

    ran_fetch = False
    fetch = ROOT / "scripts" / "fetch_news.py"
    if not args.skip_fetch and fetch.is_file():
        if (c := _run_script("scripts/fetch_news.py")) != 0:
            return c
        ran_fetch = True
    elif not args.skip_fetch and not fetch.is_file():
        print("提示：未找到 scripts/fetch_news.py，跳过抓取。", file=sys.stderr)

    if not args.skip_analyze:
        # RSS 条目日期未必等于「本地今天」，抓取成功后用全量条目做分析
        analyze_extra = ("--no-date-filter",) if ran_fetch else ()
        if (c := _run_script("scripts/analyze_news.py", *analyze_extra)) != 0:
            return c

    if not args.skip_report:
        if (c := _run_script("scripts/generate_report.py")) != 0:
            return c

    print("main：流水线执行完毕。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
