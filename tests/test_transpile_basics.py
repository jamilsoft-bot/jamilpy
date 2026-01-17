from __future__ import annotations

from jamilpy.transpiler import Transpiler


def test_basic_if_else() -> None:
    source = """
    x = 10;
    if (x > 5) {
      print(\"big\");
    } else {
      print(\"small\");
    }
    """.strip()
    transpiler = Transpiler(source, filename="example.jpy")
    program = transpiler.transpile()
    assert (
        program.code
        == """x = 10
if x > 5:
    print(\"big\")
else:
    print(\"small\")
"""
    )


def test_for_and_while() -> None:
    source = """
    total = 0
    for (x in [1, 2, 3]) {
      total += x
    }
    while (total < 10) {
      total += 1
    }
    """.strip()
    program = Transpiler(source, filename="loop.jpy").transpile()
    assert "for x in [1, 2, 3]:" in program.code
    assert "while total < 10:" in program.code
