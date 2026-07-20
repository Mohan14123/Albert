"""Tool Registry package.

Provides plug-and-play tool boundaries, registry manager, and execution stubs.
"""

from .base import Tool
from .service import (
    ToolRegistry,
    DefaultToolExecutor,
    SearchTool,
    GmailTool,
    CalendarTool,
    CalculatorTool,
    NewsTool,
)

__all__ = [
    "Tool",
    "ToolRegistry",
    "DefaultToolExecutor",
    "SearchTool",
    "GmailTool",
    "CalendarTool",
    "CalculatorTool",
    "NewsTool",
]
