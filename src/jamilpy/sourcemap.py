from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SourceMap:
    mapping: dict[int, list[int]] = field(default_factory=dict)

    def add(self, source_line: int, output_line: int) -> None:
        if source_line <= 0:
            return
        self.mapping.setdefault(source_line, []).append(output_line)

    def to_dict(self) -> dict[int, list[int]]:
        return {key: value[:] for key, value in sorted(self.mapping.items())}
