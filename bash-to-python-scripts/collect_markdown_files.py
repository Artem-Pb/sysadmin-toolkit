#!/usr/bin/env python3
"""
Рекурсивно собирает содержимое всех .md файлов из домашней директории
(или указанного корня) в один markdown-отчёт со сводкой и полным дампом.

Зачем был нужен оригинал (bash, fi2.sh / collect-all-md.sh):
Автор хотел единый обзор всей markdown-документации, разбросанной по
проектам (README, заметки, планы), с группировкой по папкам — чтобы не
открывать каждый файл вручную.

Как запускать:
    python3 collect_markdown_files.py [--root ROOT] [-o OUTPUT]

Аргументы:
    --root      Где искать .md файлы (по умолчанию: домашняя директория)
    -o, --output  Куда сохранить отчёт (по умолчанию: ~/all-md-collection.md)
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path

EXCLUDED_PARTS = {
    "node_modules", ".Trash", "Caches", "Application Support", ".git",
    ".npm", ".cache", "Pods", "build", "dist", ".next", ".venv", "venv",
    "__pycache__", "target",
}


def is_excluded(path: Path) -> bool:
    return any(p in EXCLUDED_PARTS for p in path.parts)


def find_markdown_files(root: Path) -> list[Path]:
    files = [p for p in root.rglob("*.md") if p.is_file() and not is_excluded(p)]
    return sorted(files)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path.home()))
    parser.add_argument("-o", "--output", default=str(Path.home() / "all-md-collection.md"))
    args = parser.parse_args()

    root = Path(args.root)
    output = Path(args.output)
    md_files = find_markdown_files(root)

    out: list[str] = []
    out.append("# All .md files collection")
    out.append("")
    out.append(f"**Generated:** {datetime.now():%Y-%m-%d %H:%M:%S}  ")
    out.append(f"**Root:** $HOME = {root}")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 📊 Summary")
    out.append("")
    out.append(f"Total files found: **{len(md_files)}**")
    out.append("")

    out.append("### Files by directory")
    out.append("")
    out.append("```")
    dir_counts = Counter(str(f.parent) for f in md_files)
    for directory, count in sorted(dir_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:40]:
        out.append(f"{count:>6} {directory}")
    out.append("```")
    out.append("")

    out.append("---")
    out.append("")

    out.append("# 📚 Full contents")
    out.append("")

    current_dir = None
    for count, md_file in enumerate(md_files, start=1):
        directory = str(md_file.parent)
        size = md_file.stat().st_size
        content = md_file.read_text(encoding="utf-8", errors="replace")
        lines = content.count("\n") + 1

        if directory != current_dir:
            out.append("")
            out.append("---")
            out.append("")
            out.append(f"## 📁 `{directory}`")
            out.append("")
            current_dir = directory

        out.append(f"### [{count}] `{md_file.name}`")
        out.append("")
        out.append(f"- **Path:** `{md_file}`")
        out.append(f"- **Size:** {size} bytes, {lines} lines")
        out.append("")

        if size > 100_000:
            out.append("_File >100KB, showing first 100 lines:_")
            out.append("")
            out.append("```markdown")
            out.append("\n".join(content.splitlines()[:100]))
            out.append("")
            out.append(f"... [TRUNCATED, {lines} lines total] ...")
            out.append("```")
        elif size > 30_000:
            out.append("_File >30KB, showing first 300 lines:_")
            out.append("")
            out.append("```markdown")
            out.append("\n".join(content.splitlines()[:300]))
            out.append("")
            out.append(f"... [TRUNCATED, {lines} lines total] ...")
            out.append("```")
        else:
            out.append("```markdown")
            out.append(content.rstrip("\n"))
            out.append("```")
        out.append("")

    out.append("")
    out.append("---")
    out.append("")
    out.append(f"_End of collection. Total files: {len(md_files)}_")

    text = "\n".join(out) + "\n"
    output.write_text(text, encoding="utf-8")

    print("✅ Done!")
    print(f"📄 Output: {output}")
    print(f"📊 Files collected: {len(md_files)}")
    size_kb = len(text.encode('utf-8')) / 1024
    print(f"📏 Size: {len(text.splitlines())} lines, {size_kb:.1f}K")


if __name__ == "__main__":
    main()
