from __future__ import annotations

from dataclasses import dataclass

KEYWORDS = {
    "if",
    "elif",
    "else",
    "for",
    "while",
    "def",
    "class",
    "try",
    "except",
    "finally",
    "with",
    "return",
    "yield",
    "import",
    "from",
    "as",
    "pass",
    "break",
    "continue",
    "raise",
    "lambda",
}


@dataclass(frozen=True)
class Token:
    type: str
    value: str
    line: int
    column: int


class Lexer:
    def __init__(self, source: str, filename: str = "<input>") -> None:
        self.source = source
        self.filename = filename
        self.length = len(source)
        self.index = 0
        self.line = 1
        self.column = 1

    def _peek(self, offset: int = 0) -> str:
        pos = self.index + offset
        if pos >= self.length:
            return ""
        return self.source[pos]

    def _advance(self, count: int = 1) -> str:
        text = self.source[self.index : self.index + count]
        for char in text:
            if char == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        self.index += count
        return text

    def _emit(self, token_type: str, value: str, line: int, column: int) -> Token:
        return Token(token_type, value, line, column)

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self.index < self.length:
            char = self._peek()
            if char in " \t\r":
                start_line, start_col = self.line, self.column
                value = self._consume_whitespace()
                tokens.append(self._emit("WHITESPACE", value, start_line, start_col))
                continue
            if char == "\n":
                tokens.append(self._emit("NEWLINE", "\n", self.line, self.column))
                self._advance()
                continue
            if char == "#":
                start_line, start_col = self.line, self.column
                value = self._consume_comment()
                tokens.append(self._emit("COMMENT", value, start_line, start_col))
                continue
            if self._starts_string():
                tokens.append(self._consume_string())
                continue
            if char.isalpha() or char == "_":
                tokens.append(self._consume_identifier())
                continue
            if char.isdigit():
                tokens.append(self._consume_number())
                continue
            start_line, start_col = self.line, self.column
            if char == "{":
                tokens.append(self._emit("LBRACE", char, start_line, start_col))
                self._advance()
                continue
            if char == "}":
                tokens.append(self._emit("RBRACE", char, start_line, start_col))
                self._advance()
                continue
            if char == "(":
                tokens.append(self._emit("LPAREN", char, start_line, start_col))
                self._advance()
                continue
            if char == ")":
                tokens.append(self._emit("RPAREN", char, start_line, start_col))
                self._advance()
                continue
            if char == "[":
                tokens.append(self._emit("LBRACKET", char, start_line, start_col))
                self._advance()
                continue
            if char == "]":
                tokens.append(self._emit("RBRACKET", char, start_line, start_col))
                self._advance()
                continue
            if char == ";":
                tokens.append(self._emit("SEMI", char, start_line, start_col))
                self._advance()
                continue
            # Operators and punctuation
            tokens.append(self._emit("OP", char, start_line, start_col))
            self._advance()
        return tokens

    def _consume_whitespace(self) -> str:
        start = self.index
        while self._peek() in " \t\r":
            self._advance()
        return self.source[start : self.index]

    def _consume_comment(self) -> str:
        start = self.index
        while self.index < self.length and self._peek() != "\n":
            self._advance()
        return self.source[start : self.index]

    def _starts_string(self) -> bool:
        char = self._peek()
        if char in ('"', "'"):
            return True
        if char.isalpha():
            prefix = ""
            offset = 0
            while True:
                peek = self._peek(offset)
                if peek and peek.isalpha():
                    prefix += peek
                    offset += 1
                    continue
                break
            if prefix and self._peek(offset) in ('"', "'"):
                return True
        return False

    def _consume_string(self) -> Token:
        start_line, start_col = self.line, self.column
        start = self.index
        prefix = ""
        while True:
            peek = self._peek()
            if peek and peek.isalpha() and self._peek(len(prefix)).isalpha():
                prefix += self._advance()
                continue
            break
        quote = self._peek()
        if quote not in ('"', "'"):
            quote = self._peek()
        triple = self._peek(0) == quote and self._peek(1) == quote and self._peek(2) == quote
        if triple:
            self._advance(3)
            terminator = quote * 3
        else:
            self._advance()
            terminator = quote
        while self.index < self.length:
            if triple and self.source.startswith(terminator, self.index):
                self._advance(3)
                break
            if not triple and self._peek() == "\\":
                self._advance(2)
                continue
            if not triple and self._peek() == quote:
                self._advance()
                break
            self._advance()
        value = self.source[start : self.index]
        return self._emit("STRING", value, start_line, start_col)

    def _consume_identifier(self) -> Token:
        start_line, start_col = self.line, self.column
        start = self.index
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        value = self.source[start : self.index]
        token_type = "KEYWORD" if value in KEYWORDS else "IDENT"
        return self._emit(token_type, value, start_line, start_col)

    def _consume_number(self) -> Token:
        start_line, start_col = self.line, self.column
        start = self.index
        while self._peek().isdigit() or self._peek() in ".eE+-":
            self._advance()
        value = self.source[start : self.index]
        return self._emit("NUMBER", value, start_line, start_col)
