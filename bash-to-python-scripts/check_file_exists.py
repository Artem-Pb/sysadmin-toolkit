#!/usr/bin/env python3
"""
Спрашивает у пользователя имя файла и сообщает, существует он или нет.

Зачем был нужен оригинал (bash, file_checker.sh):
Учебный/вспомогательный скрипт-заготовка для проверки существования
файла в интерактивном режиме (ввод пути с клавиатуры).

Как запускать:
    python3 check_file_exists.py

Аргументы: нет — путь к файлу запрашивается интерактивно (как в оригинале).
"""

from pathlib import Path


def main() -> None:
    file_name = input("File Name\n")
    if Path(file_name).is_file():
        print(f"file {file_name} is true")
    else:
        print(f"file {file_name} is false")


if __name__ == "__main__":
    main()
