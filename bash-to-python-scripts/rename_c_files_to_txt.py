#!/usr/bin/env python3
"""
Рекурсивно переименовывает все .c/.h файлы в указанной папке (по
умолчанию — папке скрипта) в .txt, сохраняя остальное имя без изменений.

Зачем был нужен оригинал (bash, rename.sh):
Быстро превратить исходники C в обычный текст (.txt) — например, чтобы
их можно было прикрепить/загрузить туда, где принимаются только
текстовые файлы, без изменения содержимого.

Как запускать:
    python3 rename_c_files_to_txt.py [папка]

Аргументы:
    папка   Где искать .c/.h файлы (по умолчанию: папка, где лежит скрипт)
"""

from __future__ import annotations

import argparse
from pathlib import Path


def rename_to_txt(root: Path) -> int:
    count = 0
    for file in sorted(root.rglob("*")):
        if file.is_file() and file.suffix in (".c", ".h"):
            new_name = file.with_suffix(".txt")
            file.rename(new_name)
            print(f"Переименован: {file} -> {new_name}")
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root", nargs="?", default=str(Path(__file__).resolve().parent),
        help="папка с .c/.h файлами",
    )
    args = parser.parse_args()
    count = rename_to_txt(Path(args.root))
    print(f"Готово. Переименовано файлов: {count}")


if __name__ == "__main__":
    main()
