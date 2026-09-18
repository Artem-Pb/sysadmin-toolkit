#!/usr/bin/env python3
"""
Рекурсивно собирает все .c/.h файлы из указанной папки (по умолчанию —
текущей) в один текстовый файл, разделяя их заголовками "===== FILE: ... =====".

Зачем был нужен оригинал (bash, collect.sh):
Быстро подготовить единый текстовый дамп всех исходников C-проекта —
например, чтобы вставить их целиком в чат с LLM для ревью или дебага,
не собирая файлы вручную одним по одному.

Как запускать:
    python3 collect_c_source_files.py [папка] [-o OUTPUT]

Аргументы:
    папка       Где искать .c/.h файлы (по умолчанию: текущая директория)
    -o, --output  Куда сохранить результат (по умолчанию: all_code.txt)
"""

from __future__ import annotations

import argparse
from pathlib import Path


def collect_sources(root: Path, output: Path) -> int:
    files = sorted(
        p for p in root.rglob("*") if p.is_file() and p.suffix in (".c", ".h")
    )

    with output.open("w", encoding="utf-8") as out:
        for file in files:
            out.write(f"===== FILE: {file} =====\n")
            out.write(file.read_text(encoding="utf-8", errors="replace"))
            out.write("\n\n")

    return len(files)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="папка с исходниками")
    parser.add_argument(
        "-o", "--output", default="all_code.txt", help="файл для результата"
    )
    args = parser.parse_args()

    root = Path(args.root)
    output = Path(args.output)
    count = collect_sources(root, output)
    print(f"Собрано файлов: {count}")
    print(f"Результат: {output.resolve()}")


if __name__ == "__main__":
    main()
