# Jamilpy v0.1

Jamilpy is a tiny source-to-source transpiler that lets you write Python-like code with JavaScript-style block braces. Files use the `.jpy` extension and transpile to standard Python, which is then executed by CPython.

## Install

```bash
pip install -e .
```

## CLI usage

```bash
jamilpy run examples/hello.jpy
jamilpy transpile examples/control_flow.jpy -o control_flow.py
jamilpy transpile examples/control_flow.jpy --emit-map
jamilpy check examples/hello.jpy
```

`run` transpiles to a temporary `.py` and executes it with the same Python interpreter running the CLI, forwarding any extra arguments.

## Language rules

Jamilpy keeps Python semantics but uses braces for blocks.

- Blocks use `{ ... }`.
- Optional statement terminator `;` is allowed.
- Parentheses are **required** for block headers that would otherwise be ambiguous:
  - `if (cond) { ... }`
  - `elif (cond) { ... }`
  - `for (x in it) { ... }`
  - `while (cond) { ... }`
  - `with (expr as x) { ... }`
- `def name(args) { ... }`, `class Name { ... }`, `try { ... }`, `except (E) { ... }`, `finally { ... }`.

### Brace collision rule

`{` starts a **block only when it appears immediately after a block header**. Everywhere else `{ ... }` is treated as a dict/set literal or expression, exactly like Python.

## Source maps

`jamilpy transpile <file.jpy> --emit-map` emits a `.map.json` file mapping Jamilpy line numbers to emitted Python line numbers. This is a lightweight integration point for future editor tooling.

## Limitations / TODOs

- The parser is intentionally minimal; it does not yet implement a full Python grammar.
- Multiline statements are supported, but advanced formatting is not preserved.

See `TODO.md` for planned upgrades.
