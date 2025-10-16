"""Utility helpers for structured console output.

The goal of this module is to centralize console formatting so that examples can
present their output using consistent sections and with fewer ad-hoc print
statements.  The helpers here focus on grouping related information, aligning
key/value details, and providing lightweight building blocks for blocks,
headers, and bullet lists.
"""
from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple


class ConsoleLayout:
    """Format structured sections for console output."""

    def __init__(self, width: int = 70, indent: int = 2) -> None:
        self.width = width
        self.indent = " " * indent

    def banner(self, title: str, subtitle: str | None = None) -> str:
        """Return a full-width banner with an optional subtitle."""
        border = "═" * self.width
        lines: List[str] = [border, title.center(self.width)]
        if subtitle:
            lines.append(subtitle.center(self.width))
        lines.append(border)
        return "\n".join(lines)

    def section(self, title: str, lines: Sequence[str] | None = None, *,
                border: str = "─") -> str:
        """Return a titled section with an optional body."""
        border_line = border * self.width
        body: List[str] = [border_line, title, border_line]
        if lines:
            body.extend(lines)
        return "\n".join(body)

    def key_values(self, pairs: Iterable[Tuple[str, object]]) -> List[str]:
        """Format key/value pairs with consistent alignment."""
        items = list(pairs)
        if not items:
            return []
        width = max(len(str(key)) for key, _ in items)
        return [f"{self.indent}{str(key).ljust(width)} : {value}" for key, value in items]

    def bullet_list(self, items: Iterable[str], *, bullet: str = "•") -> List[str]:
        """Format a bullet list."""
        return [f"{self.indent}{bullet} {item}" for item in items]

    def highlight(self, prefix: str, message: str) -> str:
        """Return a highlighted line prefixed with an emoji or tag."""
        return f"{prefix} {message}".strip()

    def spacer(self) -> str:
        """Return an empty line for spacing purposes."""
        return ""

    def compose(self, *blocks: str) -> str:
        """Join multiple blocks with blank lines while skipping empties."""
        return "\n\n".join(block for block in blocks if block)
