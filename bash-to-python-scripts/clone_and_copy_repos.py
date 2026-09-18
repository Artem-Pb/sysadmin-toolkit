#!/usr/bin/env python3
"""
Клонирует список git-репозиториев (по одному URL в строке из текстового
файла), переключается на ветку develop, удаляет служебные/учебные файлы
(LICENSE, CHANGELOG, датасеты и т.п.) и копирует каждый репозиторий без
истории .git в отдельную папку назначения как ProjectN.

Зачем был нужен оригинал (bash, for_rebuild_repo.sh):
Перенос набора студенческих репозиториев (school21) в личный архив/
портфолио: сохранить только код, без служебных файлов школы и без
git-истории, пронумеровав проекты по порядку.

В оригинале путь к списку репозиториев и путь назначения были
захардкожены (в т.ч. содержали реальное имя пользователя) — здесь оба
передаются аргументами командной строки.

Как запускать:
    python3 clone_and_copy_repos.py --repo-list repos.txt --dest ~/School21 \\
        [--work-dir ../pro] [--strip LICENSE CHANGELOG data-samples] [--branch develop]

Аргументы:
    --repo-list   Файл со списком URL репозиториев (по одному на строку)
    --dest        Папка назначения, куда копируются проекты (Project1, Project2, ...)
    --work-dir    Временная папка для клонирования (по умолчанию: ./_repo_work)
    --strip       Какие файлы/папки удалять перед копированием (glob-паттерны)
    --branch      Какую ветку выкладывать (по умолчанию: develop)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

DEFAULT_STRIP_PATTERNS = [
    "LICENSE", "*UZB.md", "code-samples", "data-samples",
    "materials", "ACTIVE_*", "CHANGELOG",
]


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def strip_paths(repo_dir: Path, patterns: list[str]) -> None:
    for pattern in patterns:
        for path in repo_dir.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-list", required=True, help="файл со списком URL репозиториев")
    parser.add_argument("--dest", required=True, help="папка назначения для скопированных проектов")
    parser.add_argument("--work-dir", default="_repo_work", help="временная папка для клонов")
    parser.add_argument("--strip", nargs="*", default=DEFAULT_STRIP_PATTERNS, help="что удалять перед копированием")
    parser.add_argument("--branch", default="develop", help="какую ветку выкладывать")
    args = parser.parse_args()

    repo_list = Path(args.repo_list)
    dest = Path(args.dest)
    work_dir = Path(args.work_dir)

    work_dir.mkdir(parents=True, exist_ok=True)
    dest.mkdir(parents=True, exist_ok=True)

    urls = [line.strip() for line in repo_list.read_text().splitlines() if line.strip()]

    count = 0
    for repo_url in urls:
        repo_name = Path(repo_url).stem  # аналог `basename "$repo_url" .git`
        clone_path = work_dir / repo_name

        run(["git", "clone", repo_url, str(clone_path)])
        run(["git", "checkout", args.branch], cwd=clone_path)

        shutil.rmtree(clone_path / ".git", ignore_errors=True)
        strip_paths(clone_path, args.strip)

        count += 1
        new_name = f"Project{count}"
        shutil.copytree(clone_path, dest / new_name)
        print(f"Успешно: {repo_url} скопирован как {new_name}")

    print(f"Обработано {count} репозиториев")

    shutil.rmtree(work_dir, ignore_errors=True)
    print(f"Обработано {count} репозиториев")


if __name__ == "__main__":
    main()
