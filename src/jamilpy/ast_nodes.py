from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TranspiledProgram:
    code: str
    source_map: dict[int, list[int]] | None
