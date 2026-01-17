from __future__ import annotations

from dataclasses import dataclass

from jamilpy.errors import JamilpyError
from jamilpy.lexer import Lexer, Token


@dataclass
class ParsedProgram:
    tokens: list[Token]
    source: str
    filename: str


class Parser:
    def __init__(self, source: str, filename: str = "<input>") -> None:
        self.source = source
        self.filename = filename

    def parse(self) -> ParsedProgram:
        lexer = Lexer(self.source, self.filename)
        tokens = lexer.tokenize()
        if not tokens:
            return ParsedProgram(tokens=tokens, source=self.source, filename=self.filename)
        # Basic sanity check for invalid control characters
        for token in tokens:
            if token.type == "OP" and ord(token.value) < 32 and token.value not in ("\t", "\n", "\r"):
                raise JamilpyError(
                    "Invalid control character",
                    self.filename,
                    token.line,
                    token.column,
                    hint="Remove the control character or replace it with whitespace.",
                )
        return ParsedProgram(tokens=tokens, source=self.source, filename=self.filename)
