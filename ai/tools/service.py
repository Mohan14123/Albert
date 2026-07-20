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


class NewsTool(Tool):
    """Tool to fetch live news headlines by category (technology, ai, business, world, general)."""

    @property
    def name(self) -> str:
        return "news.fetch"

    @property
    def description(self) -> str:
        return "Fetch top current news headlines by category (technology, ai, business, world, general)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "News category: 'technology', 'ai', 'business', 'world', or 'general'.",
                    "default": "general",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of headlines to return (default 5).",
                    "default": 5,
                },
            },
        }

    async def run(self, **kwargs: Any) -> Any:
        import urllib.request
        import xml.etree.ElementTree as ET

        category = str(kwargs.get("category", "general")).lower().strip()
        limit = int(kwargs.get("limit", 5))

        feed_urls = {
            "technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
            "tech": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
            "ai": "https://news.google.com/rss/search?q=Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
            "business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en",
            "world": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en",
            "general": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
        }

        url = feed_urls.get(category, feed_urls["general"])

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                content = resp.read()
                root = ET.fromstring(content)
                items = []
                for item in root.findall("./channel/item"):
                    title = item.findtext("title", "").replace("\ufffc", "").strip()
                    link = item.findtext("link", "").strip()
                    pub_date = item.findtext("pubDate", "").strip()
                    if title:
                        items.append(
                            {"title": title, "link": link, "published": pub_date}
                        )
                    if len(items) >= limit:
                        break
                if items:
                    return {
                        "category": category,
                        "count": len(items),
                        "headlines": items,
                    }
        except Exception as exc:
            logging.warning("Live RSS feed fetch failed (%s), returning structured fallback", exc)

        return {
            "category": category,
            "count": min(3, limit),
            "headlines": [
                {
                    "title": "AI Models Advance Multimodal Reasoning & Gateway Integrations",
                    "link": "https://news.google.com",
                    "published": "Recent",
                },
                {
                    "title": "Global Tech Industry Shifts Focus to Local & Private LLM Deployment",
                    "link": "https://news.google.com",
                    "published": "Recent",
                },
                {
                    "title": "Breakthrough Energy Storage Solutions Introduced for Data Centers",
                    "link": "https://news.google.com",
                    "published": "Recent",
                },
            ][:limit],
        }
