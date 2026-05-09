#!/usr/bin/env python3
"""从多个 RSS/Atom 源抓取 AI 相关新闻，去重后写入 output/news/YYYY-MM-DD.json。"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_FEEDS: tuple[tuple[str, str], ...] = (
    ("OpenAI", "https://openai.com/blog/rss.xml"),
    ("Anthropic", "https://www.anthropic.com/index.xml"),
    ("Hugging Face", "https://huggingface.co/blog/feed.xml"),
    ("Simon Willison", "https://simonwillison.net/atom/everything/"),
    ("Hacker News (AI)", "https://hnrss.org/newest?q=AI&count=50"),
)

USER_AGENT = (
    "ai-intelligence-system/0.1 (+https://github.com/; local research fetch; respects robots)"
)


def _localname(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _child_text(parent: ET.Element, name: str) -> str:
    for el in parent:
        if _localname(el.tag) == name:
            return "".join(el.itertext()).strip()
    return ""


def _parse_rfc2822_date(s: str) -> datetime | None:
    s = (s or "").strip()
    if not s:
        return None
    try:
        dt = parsedate_to_datetime(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return None


def _parse_iso_datetime(s: str) -> datetime | None:
    s = (s or "").strip()
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def _to_published_date_str(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.astimezone(timezone.utc).date().isoformat()


def _atom_link_href(entry: ET.Element) -> str:
    best = ""
    for el in entry:
        if _localname(el.tag) != "link":
            continue
        href = (el.get("href") or "").strip()
        rel = (el.get("rel") or "alternate").lower()
        if not href:
            continue
        if rel in ("alternate", "self") or not best:
            best = href
    return best


def _parse_rss_items(channel: ET.Element, source_name: str, max_items: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for el in channel:
        if _localname(el.tag) != "item":
            continue
        if len(out) >= max_items:
            break
        title = _child_text(el, "title")
        link = _child_text(el, "link") or _child_text(el, "guid")
        summary = _child_text(el, "description") or _child_text(el, "summary") or ""
        pub_raw = _child_text(el, "pubDate")
        dt = _parse_rfc2822_date(pub_raw)
        out.append(
            {
                "title": title,
                "summary": _strip_html(summary)[:2000],
                "link": link.strip(),
                "published_date": _to_published_date_str(dt),
                "source_name": source_name,
            }
        )
    return out


def _parse_atom_entries(root: ET.Element, source_name: str, max_items: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for el in root:
        if _localname(el.tag) != "entry":
            continue
        if len(out) >= max_items:
            break
        title = _child_text(el, "title")
        link = _atom_link_href(el) or _child_text(el, "id")
        summary = (
            _child_text(el, "summary")
            or _child_text(el, "content")
            or _child_text(el, "subtitle")
            or ""
        )
        pub_raw = _child_text(el, "published") or _child_text(el, "updated")
        dt = _parse_iso_datetime(pub_raw) or _parse_rfc2822_date(pub_raw)
        out.append(
            {
                "title": title,
                "summary": _strip_html(summary)[:2000],
                "link": link.strip(),
                "published_date": _to_published_date_str(dt),
                "source_name": source_name,
            }
        )
    return out


def _strip_html(s: str) -> str:
    if not s or "<" not in s:
        return s
    # 极简去标签，避免依赖第三方库
    out: list[str] = []
    i, n = 0, len(s)
    in_tag = False
    while i < n:
        c = s[i]
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            out.append(c)
        i += 1
    return " ".join("".join(out).split())


def parse_feed_xml(xml_text: str, source_name: str, max_items: int) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    name = _localname(root.tag)
    if name == "rss":
        for ch in root:
            if _localname(ch.tag) == "channel":
                return _parse_rss_items(ch, source_name, max_items)
        return []
    if name == "feed":
        return _parse_atom_entries(root, source_name, max_items)
    return []


def _dedupe_key(item: dict[str, Any]) -> str:
    link = (item.get("link") or "").strip().lower()
    if link:
        try:
            p = urlparse(link)
            key = f"{p.netloc}{p.path}".rstrip("/")
            if key:
                return key
        except ValueError:
            pass
        return link
    title = (item.get("title") or "").strip().lower()
    return f"title:{title}"


def dedupe_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for it in items:
        k = _dedupe_key(it)
        if not k or k == "title:":
            continue
        if k not in seen:
            order.append(k)
            seen[k] = it
    return [seen[k] for k in order]


@dataclass(frozen=True)
class FetchResult:
    source: str
    url: str
    ok: bool
    error: str = ""
    items: tuple[dict[str, Any], ...] = ()


def fetch_one(
    client: httpx.Client,
    source: str,
    url: str,
    max_items: int,
    max_bytes: int,
) -> FetchResult:
    try:
        r = client.get(url, follow_redirects=True)
        r.raise_for_status()
        body = r.content[:max_bytes]
        text = body.decode(r.encoding or "utf-8", errors="replace")
        items = parse_feed_xml(text, source, max_items)
        return FetchResult(source=source, url=url, ok=True, items=tuple(items))
    except Exception as e:  # noqa: BLE001
        return FetchResult(source=source, url=url, ok=False, error=str(e))


def main() -> int:
    parser = argparse.ArgumentParser(description="抓取多源 RSS/Atom 并写入 JSON")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="输出文件名日期 YYYY-MM-DD，默认今天（本地）",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="输出 JSON 路径；默认 output/news/<日期>.json",
    )
    parser.add_argument(
        "--max-per-feed",
        type=int,
        default=40,
        help="每个源最多保留的条目数",
    )
    args = parser.parse_args()

    day = args.date or date.today().isoformat()
    try:
        date.fromisoformat(day)
    except ValueError:
        print("错误：--date 须为 YYYY-MM-DD", file=sys.stderr)
        return 1

    out_path = args.output or (ROOT / "output" / "news" / f"{day}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    merged: list[dict[str, Any]] = []
    errors: list[str] = []

    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    with httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=httpx.Timeout(45.0),
        limits=limits,
    ) as client:
        for source, url in DEFAULT_FEEDS:
            res = fetch_one(client, source, url, args.max_per_feed, max_bytes=2_000_000)
            if not res.ok:
                errors.append(f"{source} ({url}): {res.error}")
                continue
            merged.extend(list(res.items))

    # 输出字段与 analyze_news 约定一致（去掉 source_name，若需可保留）
    slim: list[dict[str, str]] = []
    for it in merged:
        slim.append(
            {
                "title": str(it.get("title", "")),
                "summary": str(it.get("summary", "")),
                "link": str(it.get("link", "")),
                "published_date": str(it.get("published_date", "")),
            }
        )

    deduped = dedupe_items([dict(x) for x in slim])

    payload: dict[str, Any] = {
        "date": day,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "sources": [{"name": s, "url": u} for s, u in DEFAULT_FEEDS],
        "errors": errors,
        "items": deduped,
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(str(out_path))
    if errors:
        for e in errors:
            print(f"警告：{e}", file=sys.stderr)
    return 0 if deduped else 1


if __name__ == "__main__":
    raise SystemExit(main())
