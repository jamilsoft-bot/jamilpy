from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JamilpyError(Exception):
    message: str
    filename: str
    line: int
    column: int
    hint: str | None = None

    def __str__(self) -> str:  # pragma: no cover - handled via formatter
        return self.message


def format_error(error: JamilpyError, source: str) -> str:
    lines = source.splitlines()
    if 1 <= error.line <= len(lines):
        offending = lines[error.line - 1]
    else:
        offending = ""
    caret = " " * (max(error.column - 1, 0)) + "^"
    hint = f"Hint: {error.hint}" if error.hint else ""
    return (
        f"{error.filename}:{error.line}:{error.column}: {error.message}\n"
        f"{offending}\n"
        f"{caret}\n"
        f"{hint}".rstrip()
    )
