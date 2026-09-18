#!/usr/bin/env python3
"""
Рекурсивно ищет заданную подстроку во всех .c файлах папки (по
умолчанию — папки скрипта), печатает прогресс по каждому файлу и
сохраняет подробный отчёт (найденные строки + статистику) в файл.

Зачем был нужен оригинал (bash, mini_grep.sh):
Простой самописный аналог grep для учебных C-проектов: не просто
находит совпадения, а формирует читаемый отчёт с номерами строк и
итоговой статистикой (сколько файлов проверено, где есть совпадения),
что готовому grep из коробки не выдаёт.

Как запускать:
    python3 search_string_in_c_files.py <строка_для_поиска> [--dir DIR] [-o OUTPUT]

Аргументы:
    строка_для_поиска   Подстрока, которую ищем построчно в .c файлах
    --dir                Папка поиска (по умолчанию: папка скрипта)
    -o, --output         Файл отчёта (по умолчанию: search_results.txt
                         рядом со скриптом)
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def search_in_files(search_string: str, search_dir: Path) -> tuple[list[str], int, int, int]:
    report_lines: list[str] = []
    total_matches = 0
    files_with_matches = 0
    total_files = 0

    for file in sorted(search_dir.rglob("*.c")):
        if not file.is_file():
            continue
        total_files += 1
        print(f"Проверяем файл: {file.name}")

        report_lines.append(f"Файл: {file}")

        matches_in_file = 0
        found_lines: list[str] = []
        for line_num, line in enumerate(
            file.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            if search_string in line:
                matches_in_file += 1
                found_lines.append(f"  Строка {line_num}: {line}")

        total_matches += matches_in_file
        if matches_in_file > 0:
            files_with_matches += 1
            print(f"  ✓ Найдено совпадений: {matches_in_file}")
            report_lines.append(f"  Совпадений: {matches_in_file}")
            report_lines.extend(found_lines)
        else:
            print("  ✗ Совпадений не найдено")
            report_lines.append("  Совпадений: 0")
            report_lines.append("  (нет совпадений)")

        report_lines.append("")

    return report_lines, total_files, files_with_matches, total_matches


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("search_string", help="подстрока для поиска")
    parser.add_argument("--dir", default=str(Path(__file__).resolve().parent))
    parser.add_argument("-o", "--output", default=None)
    args = parser.parse_args()

    search_dir = Path(args.dir)
    output = Path(args.output) if args.output else search_dir / "search_results.txt"

    print(f"Поиск строки '{args.search_string}' в .c файлах...")
    print(f"Текущая папка: {search_dir}")
    print(f"Результаты будут сохранены в: {output}")
    print()

    report_lines, total_files, files_with_matches, total_matches = search_in_files(
        args.search_string, search_dir
    )

    header = [
        f"Поиск строки: '{args.search_string}'",
        f"Дата поиска: {datetime.now():%a %b %d %H:%M:%S %Y}",
        f"Папка поиска: {search_dir}",
        "=" * 50,
        "",
    ]
    footer = [
        "=" * 50,
        "ИТОГОВАЯ СТАТИСТИКА:",
        f"Проверено файлов: {total_files}",
        f"Файлов с совпадениями: {files_with_matches}",
        f"Общее количество совпадений: {total_matches}",
    ]

    output.write_text("\n".join(header + report_lines + footer) + "\n", encoding="utf-8")

    print()
    print("=" * 50)
    print("ПОИСК ЗАВЕРШЕН!")
    print(f"Проверено файлов: {total_files}")
    print(f"Файлов с совпадениями: {files_with_matches}")
    print(f"Общее количество совпадений: {total_matches}")
    print(f"Результаты сохранены в: {output}")


if __name__ == "__main__":
    main()
