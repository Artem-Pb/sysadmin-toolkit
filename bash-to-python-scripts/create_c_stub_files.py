#!/usr/bin/env python3
"""
Парсит .c/.h файл, ищет строки, начинающиеся с "int" или "void"
(объявления функций), и для каждой найденной функции создаёт пустой
<имя_функции>.c рядом с исходником и <имя_функции>_test.c в
../test/test_src (заготовки для юнит-тестов).

Зачем был нужен оригинал (bash, touch_c_files.sh / create_c_files.sh):
В школьных C-проектах (school21) для каждой функции модуля нужен
отдельный .c файл и отдельный тестовый файл в стандартной структуре
проекта. Скрипт автоматически создавал эти пустые заготовки по списку
функций, вместо ручного touch для каждой.

Как запускать:
    python3 create_c_stub_files.py <исходный_файл>

Аргументы:
    исходный_файл   .c/.h файл, где построчно ищутся объявления функций
                     вида "int name(...)" / "void name(...)"
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FUNCTION_DECL = re.compile(r"^(int|void)\s+([a-zA-Z0-9_]+)\(.*\)")


def create_stub_files(src_file: Path) -> None:
    src_dir = src_file.parent
    test_dir = src_dir / ".." / "test" / "test_src"
    test_dir.mkdir(parents=True, exist_ok=True)

    for line in src_file.read_text(encoding="utf-8", errors="replace").splitlines():
        match = FUNCTION_DECL.match(line.strip())
        if not match:
            continue

        func_name = match.group(2)

        target_c = src_dir / f"{func_name}.c"
        if not target_c.exists():
            target_c.touch()
            print(f"Created {target_c}")

        target_test = test_dir / f"{func_name}_test.c"
        if not target_test.exists():
            target_test.touch()
            print(f"Created {target_test}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_file", help="файл с объявлениями функций")
    args = parser.parse_args()

    src_file = Path(args.source_file)
    if not src_file.is_file():
        print(f"File not found: {src_file}", file=sys.stderr)
        raise SystemExit(2)

    create_stub_files(src_file)


if __name__ == "__main__":
    main()
