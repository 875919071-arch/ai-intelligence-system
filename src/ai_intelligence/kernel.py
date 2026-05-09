from __future__ import annotations

from typing import Any

from ai_intelligence.config import Settings, get_settings
from ai_intelligence.memory.working_memory import WorkingMemoryStore
from ai_intelligence.providers import llm as llm_mod
from ai_intelligence.providers.llm import LLMClient
from ai_intelligence.tools.registry import ToolRegistry, default_registry


class IntelligenceKernel:
    """
    Coordinates working memory, tool execution, and LLM calls.
    One round-trip may involve multiple tool iterations (bounded).
    """

    def __init__(
        self,
        settings: Settings | None = None,
        memory: WorkingMemoryStore | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._memory = memory or WorkingMemoryStore()
        self._tools = tools or default_registry()
        self._llm = LLMClient(self._settings)

    @property
    def memory(self) -> WorkingMemoryStore:
        return self._memory

    @property
    def tools(self) -> ToolRegistry:
        return self._tools

    async def query(self, message: str, session_id: str | None = None) -> tuple[str, str, list[str], str]:
        """
        Returns: (session_id, reply, used_tool_names, mode)
        """
        sid = self._memory.get_or_create(session_id)
        self._memory.append(sid, "user", message)

        used_tools: list[str] = []

        if not self._llm.enabled:
            # Optional: run tools heuristically in echo mode for demos
            tool_hint = ""
            lowered = message.lower()
            if "time" in lowered or "时间" in message:
                out = await self._tools.run("get_utc_time", "{}")
                used_tools.append("get_utc_time")
                tool_hint = llm_mod.summarize_tool_results_for_echo([("get_utc_time", out)])
            reply = llm_mod.echo_reply(message, tool_hint or None)
            self._memory.append(sid, "assistant", reply)
            return sid, reply, used_tools, "echo"

        messages = self._build_messages(sid)
        tools_payload = self._tools.specs_for_llm()

        max_rounds = 6
        for _ in range(max_rounds):
            data = await self._llm.chat(messages, tools=tools_payload)
            text, tool_calls = llm_mod.parse_assistant_message(data)

            if not tool_calls:
                final = (text or "").strip() or "(empty model response)"
                self._memory.append(sid, "assistant", final)
                return sid, final, used_tools, "llm"

            # Append assistant tool-call message then tool results
            call_parts: list[dict[str, Any]] = []
            for tc in tool_calls:
                name = str(tc.get("name", ""))
                args = str(tc.get("arguments", "{}"))
                tc_id = str(tc.get("id", ""))
                call_parts.append({"id": tc_id, "name": name, "arguments": args})

            messages.append(llm_mod.build_assistant_tool_calls_message(call_parts))

            for part in call_parts:
                name = part["name"]
                out = await self._tools.run(name, part["arguments"])
                used_tools.append(name)
                messages.append(
                    llm_mod.build_tool_result_message(part["id"], name, out),
                )

        fallback = "Stopped after maximum tool rounds."
        self._memory.append(sid, "assistant", fallback)
        return sid, fallback, used_tools, "llm"

    def _build_messages(self, session_id: str) -> list[dict[str, Any]]:
        system = {
            "role": "system",
            "content": (
                "You are the AI Intelligence System kernel. "
                "Use tools when they help answer factually. "
                "Be concise; prefer calling tools over guessing numbers or time."
            ),
        }
        hist = self._memory.transcript(session_id)
        out: list[dict[str, Any]] = [system]
        for row in hist:
            out.append({"role": row["role"], "content": row["content"]})
        return out
