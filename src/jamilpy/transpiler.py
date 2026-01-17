from __future__ import annotations

from dataclasses import dataclass

from jamilpy.ast_nodes import TranspiledProgram
from jamilpy.errors import JamilpyError
from jamilpy.lexer import Token
from jamilpy.parser import Parser
from jamilpy.sourcemap import SourceMap


@dataclass
class BraceContext:
    kind: str
    line: int
    column: int


@dataclass
class HeaderState:
    kind: str
    require_paren: bool = False
    remove_outer: bool = False
    awaiting_paren: bool = False
    paren_depth: int = 0
    stage: str = ""
    line: int = 0
    column: int = 0


BLOCK_KEYWORDS = {
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
}

REQUIRE_PAREN = {"if", "elif", "for", "while", "with"}


class Transpiler:
    def __init__(self, source: str, filename: str = "<input>") -> None:
        self.source = source
        self.filename = filename

    def transpile(self, emit_map: bool = False) -> TranspiledProgram:
        parser = Parser(self.source, self.filename)
        program = parser.parse()
        output_lines: list[str] = []
        source_map = SourceMap() if emit_map else None

        indent_level = 0
        brace_stack: list[BraceContext] = []
        header_state: HeaderState | None = None
        expect_block = False
        line_tokens: list[str] = []
        line_source_line: int | None = None
        at_statement_start = True
        just_closed_block = False

        def add_to_line(token: Token, text: str | None = None) -> None:
            nonlocal line_source_line
            if line_source_line is None and token.type not in {"WHITESPACE"}:
                line_source_line = token.line
            line_tokens.append(text if text is not None else token.value)

        def finalize_line(add_colon: bool = False) -> None:
            nonlocal line_tokens, line_source_line
            if not line_tokens:
                line_source_line = None
                return
            line = "".join(line_tokens)
            line = line.strip()
            if not line:
                line_tokens = []
                line_source_line = None
                return
            if add_colon and not line.endswith(":"):
                line = f"{line}:"
            output_lines.append("    " * indent_level + line)
            if source_map and line_source_line is not None:
                source_map.add(line_source_line, len(output_lines))
            line_tokens = []
            line_source_line = None

        def error(token: Token, message: str, hint: str) -> None:
            raise JamilpyError(message, self.filename, token.line, token.column, hint)

        tokens = program.tokens
        idx = 0
        while idx < len(tokens):
            token = tokens[idx]
            if just_closed_block and token.type not in {"WHITESPACE", "NEWLINE", "COMMENT"}:
                just_closed_block = False
            if token.type == "NEWLINE":
                finalize_line()
                at_statement_start = True
                idx += 1
                continue
            if token.type == "COMMENT":
                add_to_line(token)
                finalize_line()
                at_statement_start = True
                idx += 1
                continue
            if token.type == "SEMI":
                finalize_line()
                at_statement_start = True
                idx += 1
                continue
            if token.type == "WHITESPACE":
                add_to_line(token)
                idx += 1
                continue

            if header_state and header_state.awaiting_paren and token.type not in {"WHITESPACE", "COMMENT"}:
                if token.type != "LPAREN":
                    error(
                        token,
                        f"Expected '(' after {header_state.kind}",
                        "Add parentheses around the condition or expression.",
                    )

            if at_statement_start and token.type == "KEYWORD" and token.value in BLOCK_KEYWORDS:
                keyword = token.value
                if keyword in REQUIRE_PAREN:
                    header_state = HeaderState(
                        kind=keyword,
                        require_paren=True,
                        remove_outer=True,
                        awaiting_paren=True,
                        line=token.line,
                        column=token.column,
                    )
                elif keyword == "def":
                    header_state = HeaderState(kind=keyword, stage="need_name", line=token.line, column=token.column)
                elif keyword == "class":
                    header_state = HeaderState(kind=keyword, stage="need_name", line=token.line, column=token.column)
                elif keyword == "except":
                    header_state = HeaderState(kind=keyword, stage="awaiting", line=token.line, column=token.column)
                else:
                    expect_block = True
                add_to_line(token)
                at_statement_start = False
                idx += 1
                continue

            if header_state:
                if header_state.require_paren:
                    if token.type == "LPAREN":
                        header_state.paren_depth += 1
                        if header_state.awaiting_paren:
                            header_state.awaiting_paren = False
                            idx += 1
                            continue
                    if token.type == "RPAREN":
                        if header_state.paren_depth == 0:
                            error(token, "Unexpected ')'", "Remove the extra parenthesis.")
                        if header_state.paren_depth == 1:
                            header_state.paren_depth -= 1
                            expect_block = True
                            header_state = None
                            idx += 1
                            continue
                        header_state.paren_depth -= 1
                    add_to_line(token)
                    at_statement_start = False
                    idx += 1
                    continue

                if header_state.kind == "def":
                    if header_state.stage == "need_name":
                        if token.type == "IDENT":
                            header_state.stage = "need_params"
                            add_to_line(token)
                            at_statement_start = False
                            idx += 1
                            continue
                        if token.type not in {"WHITESPACE", "COMMENT"}:
                            error(token, "Expected function name", "Provide a name after 'def'.")
                    if header_state.stage == "need_params":
                        if token.type == "LPAREN":
                            header_state.stage = "in_params"
                            header_state.paren_depth = 1
                            add_to_line(token)
                            at_statement_start = False
                            idx += 1
                            continue
                        if token.type not in {"WHITESPACE", "COMMENT"}:
                            error(token, "Expected '(' after function name", "Add parameter parentheses.")
                    if header_state.stage == "in_params":
                        if token.type == "LPAREN":
                            header_state.paren_depth += 1
                        if token.type == "RPAREN":
                            header_state.paren_depth -= 1
                            if header_state.paren_depth == 0:
                                expect_block = True
                                header_state = None
                    add_to_line(token)
                    at_statement_start = False
                    idx += 1
                    continue

                if header_state.kind == "class":
                    if header_state.stage == "need_name":
                        if token.type == "IDENT":
                            header_state.stage = "maybe_bases"
                            add_to_line(token)
                            at_statement_start = False
                            idx += 1
                            continue
                        if token.type not in {"WHITESPACE", "COMMENT"}:
                            error(token, "Expected class name", "Provide a name after 'class'.")
                    if header_state.stage == "maybe_bases":
                        if token.type == "LBRACE":
                            expect_block = True
                            header_state = None
                            continue
                        if token.type == "LPAREN":
                            header_state.stage = "in_bases"
                            header_state.paren_depth = 1
                            add_to_line(token)
                            at_statement_start = False
                            idx += 1
                            continue
                    if header_state.stage == "in_bases":
                        if token.type == "LPAREN":
                            header_state.paren_depth += 1
                        if token.type == "RPAREN":
                            header_state.paren_depth -= 1
                            if header_state.paren_depth == 0:
                                expect_block = True
                                header_state = None
                    add_to_line(token)
                    at_statement_start = False
                    idx += 1
                    continue

                if header_state.kind == "except":
                    if header_state.stage == "awaiting" and token.type == "LPAREN":
                        header_state.require_paren = True
                        header_state.remove_outer = True
                        header_state.awaiting_paren = False
                        header_state.paren_depth = 1
                        idx += 1
                        continue
                    if header_state.stage == "awaiting" and token.type == "LBRACE":
                        expect_block = True
                        header_state = None
                    elif header_state.stage == "awaiting" and token.type not in {"WHITESPACE", "COMMENT"}:
                        error(token, "Expected '(' or '{' after except", "Wrap the exception in parentheses.")

            if header_state and header_state.kind == "class" and header_state.stage == "maybe_bases" and token.type == "LBRACE":
                expect_block = True
                header_state = None

            if header_state and header_state.kind in {"def", "class"} and token.type == "LBRACE" and not expect_block:
                error(token, "Expected header before '{'", "Complete the definition header before starting a block.")

            if token.type == "LBRACE":
                if expect_block:
                    finalize_line(add_colon=True)
                    brace_stack.append(BraceContext("block", token.line, token.column))
                    indent_level += 1
                    expect_block = False
                    at_statement_start = True
                    idx += 1
                    continue
                brace_stack.append(BraceContext("literal", token.line, token.column))
                add_to_line(token)
                at_statement_start = False
                idx += 1
                continue

            if token.type == "RBRACE":
                if not brace_stack:
                    error(token, "Unexpected '}'", "Remove the extra brace.")
                context = brace_stack.pop()
                if context.kind == "literal":
                    add_to_line(token)
                    at_statement_start = False
                    idx += 1
                    continue
                finalize_line()
                indent_level = max(indent_level - 1, 0)
                at_statement_start = True
                just_closed_block = True
                idx += 1
                continue

            add_to_line(token)
            at_statement_start = False
            idx += 1

        finalize_line()
        if header_state and header_state.awaiting_paren:
            raise JamilpyError(
                f"Expected '(' after {header_state.kind}",
                self.filename,
                header_state.line,
                header_state.column,
                hint="Add parentheses around the condition or expression.",
            )
        if expect_block:
            raise JamilpyError(
                "Expected '{' to start block",
                self.filename,
                tokens[-1].line,
                tokens[-1].column,
                hint="Add '{' after the block header.",
            )
        for context in brace_stack:
            if context.kind == "block":
                raise JamilpyError(
                    "Expected '}' to close block",
                    self.filename,
                    context.line,
                    context.column,
                    hint=f"Block opened at line {context.line}.",
                )
        code = "\n".join(output_lines) + ("\n" if output_lines else "")
        return TranspiledProgram(code=code, source_map=source_map.to_dict() if source_map else None)
