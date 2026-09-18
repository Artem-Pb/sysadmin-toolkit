#!/usr/bin/env python3
"""
Периодически делает скриншоты экрана (macOS) и складывает их в отдельную
папку с последовательной нумерацией — типовая задача при сборе датасета
для обучения нейросети (например, классификатора экранов/состояний UI):
нужен поток кадров через равные интервалы, а не один снимок.

Использует встроенную в macOS утилиту `screencapture` (модуль subprocess) —
никаких внешних зависимостей не требуется.

Как запускать:
    python3 capture_training_screenshots.py --output-dir ./dataset
    python3 capture_training_screenshots.py --output-dir ./dataset --interval 2 --count 100
    python3 capture_training_screenshots.py --output-dir ./dataset --format jpg --prefix frame

Аргументы:
    --output-dir   Папка для сохранения скриншотов (создаётся, если её нет)
    --interval     Пауза между снимками в секундах (по умолчанию: 5)
    --count        Сколько снимков сделать; без этого флага работает до Ctrl+C
    --prefix       Префикс имени файла (по умолчанию: frame)
    --format       Формат: png, jpg, tiff, pdf (по умолчанию: png)
    --display      Номер экрана для мультимониторных систем (по умолчанию: основной)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def capture_screenshot(output_path: Path, image_format: str, display: int | None) -> None:
    cmd = ["screencapture", "-x", "-t", image_format]
    if display is not None:
        cmd += ["-D", str(display)]
    cmd.append(str(output_path))
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output-dir", required=True, help="папка для сохранения скриншотов")
    parser.add_argument("--interval", type=float, default=5.0, help="пауза между снимками, сек")
    parser.add_argument("--count", type=int, default=None, help="сколько снимков сделать (по умолчанию: бесконечно)")
    parser.add_argument("--prefix", default="frame", help="префикс имени файла")
    parser.add_argument("--format", default="png", choices=["png", "jpg", "tiff", "pdf"], help="формат файла")
    parser.add_argument("--display", type=int, default=None, help="номер экрана для мультимониторных систем")
    args = parser.parse_args()

    if sys.platform != "darwin":
        print("Скрипт использует macOS-утилиту screencapture — работает только на macOS.", file=sys.stderr)
        raise SystemExit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Сохраняю в: {output_dir.resolve()}")
    print(f"Интервал: {args.interval} с" + (f", всего кадров: {args.count}" if args.count else ", без ограничения (Ctrl+C для остановки)"))

    taken = 0
    try:
        while args.count is None or taken < args.count:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"{args.prefix}_{timestamp}_{taken:05d}.{args.format}"
            target = output_dir / filename

            capture_screenshot(target, args.format, args.display)
            taken += 1
            print(f"  [{taken}] {filename}")

            if args.count is None or taken < args.count:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print()
    except subprocess.CalledProcessError as exc:
        print(f"Ошибка screencapture: {exc}", file=sys.stderr)
        raise SystemExit(1)

    print(f"Готово. Снимков сделано: {taken}")


if __name__ == "__main__":
    main()
