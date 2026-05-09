from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from ai_intelligence.tools.safe_math import eval_arithmetic


ToolHandler = Callable[[dict[str, Any]], Awaitable[str]]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters_schema: dict[str, Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._specs: dict[str, ToolSpec] = {}
        self._handlers: dict[str, ToolHandler] = {}

    def register(self, spec: ToolSpec, handler: ToolHandler) -> None:
        self._specs[spec.name] = spec
        self._handlers[spec.name] = handler

    def specs_for_llm(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": s.name,
                    "description": s.description,
                    "parameters": s.parameters_schema,
                },
            }
            for s in self._specs.values()
        ]

    async def run(self, name: str, arguments_json: str) -> str:
        handler = self._handlers.get(name)
        if not handler:
            return json.dumps({"error": f"unknown_tool:{name}"})
        try:
            args = json.loads(arguments_json or "{}")
        except json.JSONDecodeError:
            args = {}
        return await handler(args)


def default_registry() -> ToolRegistry:
    reg = ToolRegistry()

    async def tool_now(_: dict[str, Any]) -> str:
        return datetime.now(UTC).isoformat()

    async def tool_calculator(args: dict[str, Any]) -> str:
        expr = str(args.get("expression", "")).strip()
        if not expr:
            return json.dumps({"error": "missing_expression"})
        try:
            value = eval_arithmetic(expr)
        except Exception as e:  # noqa: BLE001
            return json.dumps({"error": str(e)})
        return json.dumps({"result": value})

    reg.register(
        ToolSpec(
            name="get_utc_time",
            description="Return current UTC time in ISO-8601 format.",
            parameters_schema={"type": "object", "properties": {}, "additionalProperties": False},
        ),
        tool_now,
    )
    reg.register(
        ToolSpec(
            name="calculator",
            description="Evaluate a simple arithmetic expression using digits and + - * / ( ).",
            parameters_schema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Arithmetic expression to evaluate."}
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        ),
        tool_calculator,
    )
    return reg
