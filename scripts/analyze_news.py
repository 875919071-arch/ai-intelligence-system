#!/usr/bin/env python3
"""读取今日 AI 新闻 JSON，调用 OpenAI 生成中文结构化分析 JSON。"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ai_intelligence.config import get_settings  # noqa: E402
from ai_intelligence.providers.llm import LLMClient, parse_assistant_message  # noqa: E402

OUTPUT_SCHEMA_HINT = """
请只输出一个 JSON 对象（不要 Markdown 代码围栏），键名固定为：
{
  "分析日期": "YYYY-MM-DD",
  "元信息": {
    "输入新闻条数": 数字,
    "纳入分析条数": 数字,
    "分析说明": "一两句中文，说明筛选与分析范围"
  },
  "AI能力跃迁": {
    "概述": "中文段落",
    "要点": [ { "结论": "", "依据": "", "相关标题": [] } ]
  },
  "Agent趋势": {
    "概述": "",
    "要点": [ { "观察": "", "证据与新闻标题": [] } ]
  },
  "多模态趋势": {
    "概述": "",
    "要点": [ { "观察": "", "证据与新闻标题": [] } ]
  },
  "用户行为变化": {
    "概述": "",
    "要点": [ { "变化": "", "可能原因": "", "证据与新闻标题": [] } ]
  },
  "产品机会": {
    "概述": "",
    "机会列表": [ { "方向": "", "目标用户": "", "为何是现在": "", "风险与前提": "" } ]
  }
}
所有叙述性字段使用简体中文；数组元素为对象时字段名保持上述中文。
"""


def _parse_date(s: str | None) -> date | None:
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        try:
            return date.fromisoformat(s[:10])
        except ValueError:
            pass
    try:
        iso = s[:-1] + "+00:00" if s.endswith("Z") else s
        return datetime.fromisoformat(iso).date()
    except ValueError:
        return None


def _load_news_items(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if isinstance(raw, dict):
        for key in ("items", "news", "articles", "data"):
            v = raw.get(key)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
    return []


def _normalize_item(it: dict[str, Any]) -> dict[str, Any]:
    title = it.get("title") or it.get("Title") or ""
    summary = it.get("summary") or it.get("description") or ""
    link = it.get("link") or it.get("url") or ""
    pub = it.get("published_date") or it.get("published_at") or it.get("pubDate") or ""
    return {
        "title": str(title),
        "summary": str(summary),
        "link": str(link),
        "published_date": str(pub) if pub is not None else "",
    }


def _filter_today(items: list[dict[str, Any]], day: date, include_undated: bool) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for it in items:
        d = _parse_date(it.get("published_date"))
        if d == day:
            out.append(it)
        elif d is None and include_undated:
            out.append(it)
    return out


def _build_user_payload(day: date, items: list[dict[str, Any]], *, date_filtered: bool) -> str:
    body = {
        "分析目标日期": day.isoformat(),
        "新闻列表": items,
    }
    scope = (
        "列表已按「分析目标日期」筛选为当日新闻。"
        if date_filtered
        else "列表为输入文件中的全部新闻（未按日期筛选）。"
    )
    return (
        f"以下 JSON 为待分析新闻。{scope}\n"
        "请基于事实归纳，不要编造不存在的来源；无足够证据的维度可写简短说明并给出空要点数组。\n"
        f"{json.dumps(body, ensure_ascii=False, indent=2)}\n\n"
        "请输出符合此前约定的 JSON 字符串。"
    )


async def _run_llm(client: LLMClient, user_text: str) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "你是资深 AI 产业与产品研究分析师，擅长从新闻中提炼结构化洞察。"
                "必须严格输出可解析的 JSON。"
                + OUTPUT_SCHEMA_HINT
            ),
        },
        {
            "role": "user",
            "content": user_text + "\n\n输出必须是 JSON。",
        },
    ]
    data = await client.chat(
        messages,
        response_format={"type": "json_object"},
    )
    content, _ = parse_assistant_message(data)
    if not content:
        raise RuntimeError("empty_model_response")
    return json.loads(content)


async def async_main() -> int:
    parser = argparse.ArgumentParser(description="用 OpenAI 分析今日 AI 新闻并写出中文 JSON")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="新闻 JSON 路径；默认 output/news/<今日>.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="分析结果输出路径；默认 output/analysis/<今日>.json",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="分析日期 YYYY-MM-DD，默认今天（本地）",
    )
    parser.add_argument(
        "--include-undated",
        action="store_true",
        help="纳入无 published_date 的条目（仍优先筛当天）",
    )
    parser.add_argument(
        "--no-date-filter",
        action="store_true",
        help="不按日期筛选，使用文件内全部新闻",
    )
    args = parser.parse_args()

    settings = get_settings()
    client = LLMClient(settings)
    if not client.enabled:
        print("错误：未配置 OPENAI_API_KEY，无法调用 OpenAI。", file=sys.stderr)
        return 1

    day = date.fromisoformat(args.date) if args.date else date.today()
    in_path = args.input or (_ROOT / "output" / "news" / f"{day.isoformat()}.json")
    if not in_path.is_file():
        print(f"错误：找不到输入文件 {in_path}", file=sys.stderr)
        return 1

    raw = json.loads(in_path.read_text(encoding="utf-8"))
    items = [_normalize_item(x) for x in _load_news_items(raw)]
    if not args.no_date_filter:
        filtered = _filter_today(items, day, include_undated=args.include_undated)
    else:
        filtered = items

    if not filtered and not args.no_date_filter:
        print(f"警告：{day.isoformat()} 无匹配新闻；将仍请求模型生成空证据下的框架性分析。", file=sys.stderr)

    to_analyze = filtered if (filtered or args.no_date_filter) else items
    user_text = _build_user_payload(
        day,
        to_analyze,
        date_filtered=not args.no_date_filter,
    )
    try:
        result = await _run_llm(client, user_text)
    except json.JSONDecodeError as e:
        print(f"错误：模型返回非合法 JSON：{e}", file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"错误：{e}", file=sys.stderr)
        return 1

    out_path = args.output or (_ROOT / "output" / "analysis" / f"{day.isoformat()}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(str(out_path))
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(async_main()))


if __name__ == "__main__":
    main()
