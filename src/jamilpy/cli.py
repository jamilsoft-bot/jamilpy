from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jamilpy.errors import JamilpyError, format_error
from jamilpy.runner import run_file
from jamilpy.transpiler import Transpiler


def _load_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cmd_transpile(args: argparse.Namespace) -> int:
    source = _load_source(args.file)
    transpiler = Transpiler(source, filename=str(args.file))
    program = transpiler.transpile(emit_map=args.emit_map)
    if args.output:
        args.output.write_text(program.code, encoding="utf-8")
    else:
        sys.stdout.write(program.code)
    if args.emit_map and program.source_map is not None:
        map_path = (args.output or args.file.with_suffix(".py")).with_suffix(".map.json")
        map_path.write_text(json.dumps(program.source_map, indent=2), encoding="utf-8")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    source = _load_source(args.file)
    transpiler = Transpiler(source, filename=str(args.file))
    transpiler.transpile(emit_map=False)
    sys.stdout.write(f"{args.file}: OK\n")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    return run_file(args.file, args.args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jamilpy", description="Jamilpy .jpy transpiler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a .jpy file")
    run_parser.add_argument("file", type=Path)
    run_parser.add_argument("args", nargs=argparse.REMAINDER)
    run_parser.set_defaults(func=cmd_run)

    transpile_parser = subparsers.add_parser("transpile", help="Transpile .jpy to Python")
    transpile_parser.add_argument("file", type=Path)
    transpile_parser.add_argument("-o", "--output", type=Path)
    transpile_parser.add_argument("--emit-map", action="store_true")
    transpile_parser.set_defaults(func=cmd_transpile)

    check_parser = subparsers.add_parser("check", help="Check a .jpy file")
    check_parser.add_argument("file", type=Path)
    check_parser.set_defaults(func=cmd_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except JamilpyError as exc:
        source = _load_source(args.file)
        sys.stderr.write(format_error(exc, source) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
