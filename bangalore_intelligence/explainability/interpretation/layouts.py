"""Data-only layouts for deep interpretation content."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InterpretationSection:
    """A structured renderable interpretation section."""

    title: str
    body: str | tuple[str, ...]


__all__ = ["InterpretationSection"]
