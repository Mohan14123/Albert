from __future__ import annotations

import logging
from typing import Any, Sequence
from ..orchestrator.contracts import ToolExecutor
from ..orchestrator.models import ChatRequest
from .base import Tool
from ..exceptions import ToolError


class ToolRegistry:
    """Registry to register and inspect available plug-and-play tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a new tool instance."""
        if tool.name in self._tools:
            logging.warning(f"Overwriting already registered tool: {tool.name}")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool | None:
        """Retrieve a registered tool by its name."""
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        """List all currently registered tools."""
        return list(self._tools.values())


class DefaultToolExecutor(ToolExecutor):
    """Executes tool calls specified in the plan, routing them through the registry."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    async def execute(
        self, request: ChatRequest, plan: Any
    ) -> Sequence[dict[str, Any]]:
        """Run each step in the plan that matches a tool from the registry."""
        results = []

        # Check if plan has steps attribute (matches ExecutionPlan)
        steps = getattr(plan, "steps", []) if plan else []

        for step in steps:
            tool_name = getattr(step, "tool_name", "unknown")
            args = getattr(step, "args", {})

            tool = self._registry.get_tool(tool_name)
            if not tool:
                results.append(
                    {
                        "tool_name": tool_name,
                        "success": False,
                        "result": None,
                        "error": f"Tool '{tool_name}' not found in registry.",
                    }
                )
                continue

            try:
                # Execute tool run asynchronously
                res = await tool.run(**args)
                results.append(
                    {
                        "tool_name": tool_name,
                        "success": True,
                        "result": res,
                        "error": None,
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "tool_name": tool_name,
                        "success": False,
                        "result": None,
                        "error": str(e),
                    }
                )

        return results


# --- Concrete Example Tool Stubs ---


class SearchTool(Tool):
    """Stub tool to query web search results."""

    @property
    def name(self) -> str:
        return "search.web"

    @property
    def description(self) -> str:
        return "Query search engine to retrieve public web pages and summaries."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query terms."}
            },
            "required": ["query"],
        }

    async def run(self, **kwargs: Any) -> Any:
        query = kwargs.get("query", "")
        return f"Mock search result for '{query}': Found 3 matching articles. Temperatures in Munich are pleasant."


class GmailTool(Tool):
    """Stub tool to simulate sending emails."""

    @property
    def name(self) -> str:
        return "gmail.send"

    @property
    def description(self) -> str:
        return "Send an email message via Gmail to a recipient."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address."},
                "subject": {"type": "string", "description": "Email subject."},
                "body": {"type": "string", "description": "Email body content."},
            },
            "required": ["to", "subject", "body"],
        }

    async def run(self, **kwargs: Any) -> Any:
        to = kwargs.get("to", "")
        subject = kwargs.get("subject", "")
        return f"Email with subject '{subject}' sent successfully to '{to}'."


class CalendarTool(Tool):
    """Stub tool to inspect calendar items."""

    @property
    def name(self) -> str:
        return "calendar.get_events"

    @property
    def description(self) -> str:
        return "Retrieve events from Google Calendar."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max events to return."}
            },
        }

    async def run(self, **kwargs: Any) -> Any:
        limit = kwargs.get("limit", 3)
        return [
            {"summary": "Alfred Code Review", "start": "2026-07-18T14:00:00Z"},
            {"summary": "Lunch with Mohan", "start": "2026-07-18T13:00:00Z"},
        ][:limit]


class CalculatorTool(Tool):
    """Tool to compute simple math statements safely without eval()."""

    @property
    def name(self) -> str:
        return "calculator.compute"

    @property
    def description(self) -> str:
        return "Evaluate a simple math expression safely."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression, e.g. 2 + 2.",
                }
            },
            "required": ["expression"],
        }

    async def run(self, **kwargs: Any) -> Any:
        import ast
        import operator

        expression = kwargs.get("expression", "")

        # Safe operators map
        _ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
            ast.Mod: operator.mod,
            ast.FloorDiv: operator.floordiv,
        }

        def _safe_eval(node: ast.AST) -> float:
            """Recursively evaluate an AST node using only safe arithmetic ops."""
            if isinstance(node, ast.Expression):
                return _safe_eval(node.body)
            elif isinstance(node, ast.Constant) and isinstance(
                node.value, (int, float)
            ):
                return node.value
            elif isinstance(node, ast.BinOp):
                op_func = _ops.get(type(node.op))
                if op_func is None:
                    raise ToolError(f"Unsupported operator: {type(node.op).__name__}")
                return op_func(_safe_eval(node.left), _safe_eval(node.right))  # type: ignore
            elif isinstance(node, ast.UnaryOp):
                op_func = _ops.get(type(node.op))
                if op_func is None:
                    raise ToolError(
                        f"Unsupported unary operator: {type(node.op).__name__}"
                    )
                return op_func(_safe_eval(node.operand))  # type: ignore
            else:
                raise ToolError(
                    f"Unsupported expression element: {type(node).__name__}"
                )

        try:
            tree = ast.parse(expression.strip(), mode="eval")
            return _safe_eval(tree)
        except (SyntaxError, ValueError) as e:
            raise ToolError(f"Invalid math expression: {e}") from e
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Math evaluation failed: {e}") from e
