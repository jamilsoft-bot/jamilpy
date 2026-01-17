from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from jamilpy.transpiler import Transpiler


def run_file(path: Path, args: list[str]) -> int:
    source = path.read_text(encoding="utf-8")
    transpiler = Transpiler(source, filename=str(path))
    program = transpiler.transpile(emit_map=False)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / (path.stem + ".py")
        tmp_path.write_text(program.code, encoding="utf-8")
        result = subprocess.run([sys.executable, str(tmp_path), *args], check=False)
        return result.returncode
