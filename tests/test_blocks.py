from __future__ import annotations

from jamilpy.transpiler import Transpiler


def test_functions_and_classes() -> None:
    source = """
    def add(a, b) {
      return a + b
    }

    class Greeter {
      def hello(name) {
        return f\"Hello, {name}\"
      }
    }
    """.strip()
    program = Transpiler(source, filename="defs.jpy").transpile()
    assert "def add(a, b):" in program.code
    assert "class Greeter:" in program.code
    assert "def hello(name):" in program.code


def test_try_except_finally() -> None:
    source = """
    try {
      risky()
    } except (ValueError) {
      handle()
    } finally {
      cleanup()
    }
    """.strip()
    program = Transpiler(source, filename="try.jpy").transpile()
    assert "try:" in program.code
    assert "except ValueError:" in program.code
    assert "finally:" in program.code
