#!/usr/bin/env python3
"""
Сливает историю всех веток из одного git-репозитория (source) в другой
(target): клонирует target, добавляет source как remote, забирает все
его ветки как локальные, гарантирует наличие ветки main и пушит всё в
origin (target).

Зачем был нужен оригинал (bash, for_copy_repo.sh):
Перенос полной истории учебного/рабочего репозитория (со всеми ветками)
в другой репозиторий-приёмник — например, при переезде с одного git-хоста
на другой с сохранением истории коммитов.

В оригинале URL исходного и целевого репозитория были захардкожены —
здесь они обязательные аргументы командной строки, реальные значения
нигде не хранятся.

ВНИМАНИЕ: скрипт делает git push --all и --tags в target-репозиторий —
это изменяет удалённый репозиторий. Проверьте аргументы перед запуском.

Как запускать:
    python3 merge_git_repos.py --target git@host:group/target.git \\
                                --source ssh://git@host:port/path/source.git \\
                                [--workdir work_repo_merge]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def run_capture(cmd: list[str], cwd: Path | None = None) -> str:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True).stdout


def branch_exists(repo_dir: Path, branch: str) -> bool:
    result = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=repo_dir,
    )
    return result.returncode == 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", required=True, help="URL целевого репозитория (куда сливаем)")
    parser.add_argument("--source", required=True, help="URL исходного репозитория (что сливаем)")
    parser.add_argument("--workdir", default="work_repo_merge", help="рабочая папка для клонов")
    args = parser.parse_args()

    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    repo_dir = workdir / "repo_A"

    print("Cloning target repo (A)...")
    run(["git", "clone", args.target, str(repo_dir)])

    print("Adding source repo (B) as remote 'repo_b'...")
    run(["git", "remote", "add", "repo_b", args.source], cwd=repo_dir)

    print("Fetching all branches from repo_b...")
    run(["git", "fetch", "repo_b"], cwd=repo_dir)

    print("Checking out all remote branches from repo_b as local branches...")
    remote_branches = run_capture(["git", "branch", "-r"], cwd=repo_dir)
    for line in remote_branches.splitlines():
        line = line.strip()
        if not line.startswith("repo_b/") or line == "repo_b/HEAD" or "->" in line:
            continue
        branch = line[len("repo_b/"):]
        if branch_exists(repo_dir, branch):
            print(f"Local branch '{branch}' already exists, skipping creation")
        else:
            run(["git", "checkout", "-b", branch, f"repo_b/{branch}"], cwd=repo_dir)

    print("Analyzing main/master branches...")
    main_exists = branch_exists(repo_dir, "main")
    master_exists = branch_exists(repo_dir, "master")
    if main_exists:
        print("✓ 'main' branch exists")
    if master_exists:
        print("✓ 'master' branch exists")

    if not main_exists and master_exists:
        print("Creating 'main' branch from 'master'...")
        run(["git", "checkout", "master"], cwd=repo_dir)
        run(["git", "checkout", "-b", "main"], cwd=repo_dir)

    if not main_exists and not master_exists:
        print("⚠ Neither 'main' nor 'master' branch found. Please create a main branch manually.")
        sys.exit(1)

    run(["git", "checkout", "main"], cwd=repo_dir)

    print("Pushing all branches and tags to origin...")
    run(["git", "push", "origin", "--all"], cwd=repo_dir)
    run(["git", "push", "origin", "--tags"], cwd=repo_dir)

    print("✅ Done! All branches and history from repo_b merged into repo_A and pushed to origin.")


if __name__ == "__main__":
    main()
