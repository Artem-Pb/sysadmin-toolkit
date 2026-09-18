#!/usr/bin/env python3
"""
Учебный скрипт-приветствие: выводит текущего пользователя, домашнюю
папку, рабочую директорию, спрашивает имя и печатает текущую дату/время.

Зачем был нужен оригинал (bash, hello_world.sh):
Первый тренировочный скрипт для знакомства с переменными окружения
($USER, $HOME, $PWD), чтением ввода и выводом даты в shell.

Как запускать:
    python3 greet_user.py

Аргументы: нет — имя запрашивается интерактивно.
"""

import os
from datetime import datetime
from pathlib import Path


def main() -> None:
    print(f"Hello, {os.environ.get('USER', os.getlogin())}")
    print(f"You are home dir: {Path.home()}")
    print(f"You are have dir: {Path.cwd()}")
    print("What you name, man?")
    name = input()
    print(f"Hello, {name}")
    print(" ".join(datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y").split()))


if __name__ == "__main__":
    main()
