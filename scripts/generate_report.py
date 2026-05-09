#!/usr/bin/env python3
"""读取分析结果 JSON，生成 Markdown 日报并写入 reports/daily/YYYY-MM-DD.md。"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]

# 与 analyze_news 默认输出顺序对齐；其余顶层键按字典序追加
_DEFAULT_SECTION_ORDER: tuple[str, ...] = (
    "AI能力跃迁",
    "Agent趋势",
    "多模态趋势",
    "用户行为变化",
    "产品机会",
)

_PROMPT_STYLE_FIELDS: tuple[str, ...] = (
    "发生了什么",
    "为什么重要",
    "对产品的影响",
    "对用户行为的影响",
    "对AI心理产品的启发",
    "是否值得长期关注",
)


def _inline(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _render_list_of_strings(items: list[Any]) -> list[str]:
    lines: list[str] = []
    for x in items:
        lines.append(f"  - {_inline(x)}")
    return lines


def _render_dict_item_block(item: dict[str, Any], index: int) -> list[str]:
    lines: list[str] = [f"#### 条目 {index}", ""]
    if any(k in item for k in _PROMPT_STYLE_FIELDS):
        for k in _PROMPT_STYLE_FIELDS:
            if k not in item:
                continue
            v = item[k]
            if isinstance(v, bool):
                v = "是" if v else "否"
            lines.append(f"- **{k}**：{_inline(v)}")
        for k, v in item.items():
            if k in _PROMPT_STYLE_FIELDS:
                continue
            lines.append(f"- **{k}**：{_inline(v)}")
        lines.append("")
        return lines

    for k, v in item.items():
        if isinstance(v, list) and v and not isinstance(v[0], dict):
            lines.append(f"- **{k}**：")
            lines.extend(_render_list_of_strings(v))
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            lines.append(f"- **{k}**：")
            for i, sub in enumerate(v, start=1):
                if not isinstance(sub, dict):
                    lines.append(f"  - {_inline(sub)}")
                    continue
                lines.append(f"  - 子项 {i}：")
                for sk, sv in sub.items():
                    lines.append(f"    - **{sk}**：{_inline(sv)}")
        else:
            lines.append(f"- **{k}**：{_inline(v)}")
    lines.append("")
    return lines


def _render_section_value(value: Any) -> list[str]:
    if value is None:
        return ["_（空）_", ""]
    if isinstance(value, str):
        return [value.strip() or "_（空）_", ""]
    if isinstance(value, list):
        lines: list[str] = []
        for i, item in enumerate(value, start=1):
            if isinstance(item, dict):
                lines.extend(_render_dict_item_block(item, i))
            else:
                lines.append(f"- {_inline(item)}")
        lines.append("")
        return lines
    if not isinstance(value, dict):
        return [_inline(value), ""]

    lines: list[str] = []
    if "概述" in value and isinstance(value["概述"], str):
        lines.append(value["概述"].strip() or "_（无概述）_")
        lines.append("")

    for list_key in ("要点", "机会列表"):
        if list_key not in value:
            continue
        raw = value[list_key]
        if not isinstance(raw, list):
            continue
        lines.append(f"### {list_key}")
        lines.append("")
        for i, item in enumerate(raw, start=1):
            if isinstance(item, dict):
                lines.extend(_render_dict_item_block(item, i))
            else:
                lines.append(f"- {_inline(item)}")
        lines.append("")

    handled = {"概述", "要点", "机会列表"}
    for k, v in value.items():
        if k in handled:
            continue
        lines.append(f"### {k}")
        lines.append("")
        if isinstance(v, dict):
            lines.extend(_render_section_value(v))
        elif isinstance(v, list):
            lines.extend(_render_section_value(v))
        else:
            lines.append(_inline(v))
            lines.append("")
    return lines


def render_analysis_markdown(data: dict[str, Any], *, fallback_date: str) -> str:
    title_date = str(data.get("分析日期") or fallback_date)
    out: list[str] = [
        f"# AI 情报日报 — {title_date}",
        "",
    ]

    meta = data.get("元信息")
    if isinstance(meta, dict) and meta:
        out.append("## 元信息")
        out.append("")
        for k, v in meta.items():
            out.append(f"- **{k}**：{_inline(v)}")
        out.append("")

    reserved = {"分析日期", "元信息"}
    ordered_keys = [k for k in _DEFAULT_SECTION_ORDER if k in data and k not in reserved]
    extra = sorted(k for k in data if k not in reserved and k not in _DEFAULT_SECTION_ORDER)
    for key in ordered_keys + extra:
        out.append(f"## {key}")
        out.append("")
        out.extend(_render_section_value(data[key]))

    return "\n".join(line.rstrip() for line in out).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="从分析 JSON 生成 Markdown 日报")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="分析结果 JSON；默认 output/analysis/<日期>.json",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="日期 YYYY-MM-DD，用于默认输入/输出文件名；默认今天（本地）",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Markdown 输出目录；默认仓库根下 reports/daily",
    )
    args = parser.parse_args()

    day = args.date or date.today().isoformat()
    try:
        date.fromisoformat(day)
    except ValueError:
        print("错误：--date 须为 YYYY-MM-DD", file=sys.stderr)
        return 1

    in_path = args.input or (_ROOT / "output" / "analysis" / f"{day}.json")
    if not in_path.is_file():
        print(f"错误：找不到分析文件 {in_path}", file=sys.stderr)
        return 1

    raw = json.loads(in_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        print("错误：分析 JSON 须为对象", file=sys.stderr)
        return 1

    body = render_analysis_markdown(raw, fallback_date=day)
    out_dir = args.output_dir or (_ROOT / "reports" / "daily")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{day}.md"
    out_path.write_text(body, encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
