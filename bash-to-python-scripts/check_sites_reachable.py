#!/usr/bin/env python3
"""
Проверяет доступность списка сайтов через ping и печатает "доступен" /
"недоступен" для каждого.

Зачем был нужен оригинал (bash, site.sh):
Быстрая проверка интернет-соединения/доступности нескольких известных
сайтов одной командой, без открытия браузера.

Как запускать:
    python3 check_sites_reachable.py
    python3 check_sites_reachable.py example.com example.org

Аргументы:
    [сайты...]   Список доменов для проверки (по умолчанию — тот же
                 набор, что и в оригинальном скрипте: google.com, ya.ru,
                 eapteka.ru, dzen.ru, gitlab.com)
"""

from __future__ import annotations

import argparse
import platform
import subprocess

DEFAULT_SITES = ["google.com", "ya.ru", "eapteka.ru", "dzen.ru", "gitlab.com"]


def is_reachable(site: str) -> bool:
    count_flag = "-n" if platform.system() == "Windows" else "-c"
    result = subprocess.run(
        ["ping", count_flag, "1", site],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sites", nargs="*", default=DEFAULT_SITES, help="список доменов")
    args = parser.parse_args()

    for site in args.sites:
        if is_reachable(site):
            print(f"{site} доступен")
        else:
            print(f"{site} недоступен")


if __name__ == "__main__":
    main()
