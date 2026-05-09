"""Evaluate arithmetic expressions with ast (no code execution)."""

from __future__ import annotations

import ast
import operator as op


_ALLOWED_BINOPS: dict[type[ast.AST], type] = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.FloorDiv: op.floordiv,
}

_ALLOWED_UNARY: dict[type[ast.AST], type] = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}


def eval_arithmetic(expr: str) -> float | int:
    node = ast.parse(expr, mode="eval")
    if not isinstance(node, ast.Expression):
        raise ValueError("invalid_expression")
    return _eval_node(node.body)


def _eval_node(node: ast.AST) -> float | int:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        fn = _ALLOWED_UNARY[type(node.op)]
        return fn(_eval_node(node.operand))  # type: ignore[operator]
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        fn = _ALLOWED_BINOPS[type(node.op)]
        return fn(_eval_node(node.left), _eval_node(node.right))  # type: ignore[operator]
    raise ValueError("unsupported_syntax")
