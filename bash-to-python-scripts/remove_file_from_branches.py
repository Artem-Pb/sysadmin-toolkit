#!/usr/bin/env python3
"""
Проходит по всем локальным веткам git (кроме main), и если в ветке есть
указанный файл — удаляет его, коммитит и пушит ветку в origin.

Зачем был нужен оригинал (bash, scriptc.sh):
Массовая чистка одного и того же файла (например README.md, случайно
закоммиченного во все ветки студенческого репозитория) без ручного
переключения на каждую ветку по отдельности.

ВНИМАНИЕ: скрипт переключает ветки, коммитит и пушит в origin — то есть
изменяет удалённый репозиторий. Запускать осознанно, на "чистом" дереве.

Как запускать:
    python3 remove_file_from_branches.py [--file README.md] [--remote origin] [--keep main] [--dry-run]

Аргументы:
    --file     Какой файл удалять из веток (по умолчанию: README.md)
    --remote   Имя удалённого репозитория для push (по умолчанию: origin)
    --keep     Ветка, которую пропускаем (по умолчанию: main)
    --dry-run  Только показать, что было бы сделано, без реальных изменений
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def list_local_branches() -> list[str]:
    result = run(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/"])
    return [line for line in result.stdout.splitlines() if line]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", default="README.md")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--keep", default="main")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for branch in list_local_branches():
        if branch == args.keep:
            print(f"Пропускаем ветку '{branch}'")
            continue

        if args.dry_run:
            has_file = run(["git", "cat-file", "-e", f"{branch}:{args.file}"], check=False).returncode == 0
            if has_file:
                print(f"[DRY RUN] {branch}: git rm {args.file} && git commit && git push {args.remote} {branch}")
            else:
                print(f"[DRY RUN] {branch}: файл не найден, пропуск")
            continue

        checkout = run(["git", "checkout", branch], check=False)
        if checkout.returncode != 0:
            print(f"Не удалось переключиться на '{branch}', пропускаем")
            continue

        if not Path(args.file).is_file():
            print(f"Файл не найден в ветке '{branch}'")
            continue

        run(["git", "rm", args.file])
        run(["git", "commit", "-m", f"Remove file from {branch}"])
        run(["git", "push", args.remote, branch])


if __name__ == "__main__":
    main()
