from __future__ import annotations

from jamilpy.transpiler import Transpiler


def test_dict_literal_preserved() -> None:
    source = """
    data = {"a": 1, "b": 2}
    if (data["a"] == 1) {
      print(data)
    }
    """.strip()
    program = Transpiler(source, filename="dicts.jpy").transpile()
    assert "data = {\"a\": 1, \"b\": 2}" in program.code
    assert "if data[\"a\"] == 1:" in program.code


def test_set_literal_preserved() -> None:
    source = """
    items = {1, 2, 3}
    for (x in items) {
      print(x)
    }
    """.strip()
    program = Transpiler(source, filename="sets.jpy").transpile()
    assert "items = {1, 2, 3}" in program.code
