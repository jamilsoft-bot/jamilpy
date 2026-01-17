from __future__ import annotations

import pytest

from jamilpy.errors import JamilpyError
from jamilpy.transpiler import Transpiler


def test_missing_brace_error() -> None:
    source = """
    if (x > 1) {
      print(x)
    """.strip()
    with pytest.raises(JamilpyError) as excinfo:
        Transpiler(source, filename="missing.jpy").transpile()
    assert "Expected '}'" in excinfo.value.message


def test_paren_required_error() -> None:
    source = """
    if x > 1 {
      print(x)
    }
    """.strip()
    with pytest.raises(JamilpyError) as excinfo:
        Transpiler(source, filename="paren.jpy").transpile()
    assert "Expected '('" in excinfo.value.message
