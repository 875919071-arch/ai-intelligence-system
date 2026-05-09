from __future__ import annotations

import json
from typing import Any

import httpx

from ai_intelligence.config import Settings


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def enabled(self) -> bool:
        return bool(self._settings.openai_api_key.strip())

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("llm_disabled")
        url = f"{self._settings.openai_base_url.rstrip('/')}/chat/completions"
        payload: dict[str, Any] = {
            "model": self._settings.openai_model,
            "messages": messages,
            "temperature": 0.2,
        }
        if response_format is not None:
            payload["response_format"] = response_format
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        headers = {
            "Authorization": f"Bearer {self._settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()


def echo_reply(user_message: str, tool_context: str | None) -> str:
    base = (
        "[echo mode — set OPENAI_API_KEY for live LLM]\n\n"
        f"收到：{user_message.strip()}\n\n"
        "当前为离线占位回复；配置 API Key 后将通过模型与工具链生成回答。"
    )
    if tool_context:
        return base + "\n\n" + tool_context
    return base


def parse_assistant_message(data: dict[str, Any]) -> tuple[str | None, list[dict[str, Any]]]:
    choice = (data.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = msg.get("content")
    tool_calls = msg.get("tool_calls") or []
    normalized: list[dict[str, Any]] = []
    for tc in tool_calls:
        fn = tc.get("function") or {}
        normalized.append(
            {
                "id": tc.get("id", ""),
                "name": fn.get("name", ""),
                "arguments": fn.get("arguments", "") or "{}",
            }
        )
    return (content if isinstance(content, str) else None), normalized


def build_tool_result_message(tool_call_id: str, name: str, output: str) -> dict[str, Any]:
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": name,
        "content": output,
    }


def build_assistant_tool_calls_message(parts: list[dict[str, Any]]) -> dict[str, Any]:
    """Reconstruct assistant message with tool_calls for the next LLM round."""
    tool_calls = []
    for p in parts:
        tool_calls.append(
            {
                "id": p["id"],
                "type": "function",
                "function": {"name": p["name"], "arguments": p["arguments"]},
            }
        )
    return {"role": "assistant", "content": None, "tool_calls": tool_calls}


def summarize_tool_results_for_echo(tool_results: list[tuple[str, str]]) -> str:
    lines = ["工具执行摘要（echo 模式）:"]
    for name, out in tool_results:
        lines.append(f"- {name}: {out[:500]}")
    return "\n".join(lines)
