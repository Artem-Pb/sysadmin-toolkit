#!/usr/bin/env python3
"""
Проверка системных ресурсов macOS (CPU, RAM, диск) с рекомендацией
лимитов для запуска Colima (Docker runtime для macOS).

Зачем был нужен оригинал (bash, check-res.sh):
Перед стартом Colima автор хотел быстро увидеть, сколько ядер и памяти
свободно на Mac, и получить готовую рекомендацию (--cpu / --memory),
не считая это вручную каждый раз.

Как запускать:
    python3 check_mac_resources.py

Аргументы: нет. Скрипт работает только на macOS (использует sysctl/top/df).
Результат построчно выводится в консоль и дублируется в лог-файл
~/resources.log (как и в оригинальном bash-скрипте).
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / "resources.log"


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, errors="replace", check=True)
    return result.stdout.strip()


def get_cpu_info() -> tuple[int, int, float]:
    physical = int(run(["sysctl", "-n", "hw.physicalcpu"]))
    logical = int(run(["sysctl", "-n", "hw.logicalcpu"]))

    top_output = run(["top", "-l", "1"])
    idle = 0.0
    for line in top_output.splitlines():
        if "CPU usage" in line:
            # пример строки: "CPU usage: 12.5% user, 5.0% sys, 82.5% idle"
            match = re.search(r"([\d.]+)%\s*idle", line)
            if match:
                idle = float(match.group(1))
    return physical, logical, idle


def get_ram_info() -> tuple[float, float]:
    mem_total_bytes = int(run(["sysctl", "-n", "hw.memsize"]))
    mem_total_gb = mem_total_bytes / 1024 / 1024 / 1024

    top_output = run(["top", "-l", "1"])
    mem_used_gb = 0.0
    for line in top_output.splitlines():
        if line.startswith("PhysMem"):
            match = re.search(r"([\d.]+)([MG])\s+used", line)
            if match:
                value, unit = float(match.group(1)), match.group(2)
                mem_used_gb = value / 1024 if unit == "M" else value
    return mem_total_gb, mem_used_gb


def get_disk_info() -> tuple[str, str, str]:
    df_output = run(["df", "-h", "/"])
    fields = df_output.splitlines()[1].split()
    total, used, avail = fields[1], fields[2], fields[3]
    return total, used, avail


def main() -> None:
    lines: list[str] = []

    lines.append("=== Проверка ресурсов Mac ===")
    lines.append(f"Дата/Время: {datetime.now():%a %b %d %H:%M:%S %Y}")

    physical, logical, cpu_idle = get_cpu_info()
    cpu_used_int = int(round(100 - cpu_idle))
    lines.append(f"CPU: физические ядра = {physical}, логические ядра = {logical}")
    lines.append(f"Загрузка CPU ≈ {cpu_used_int}%")

    # оставляем 1-2 ядра для macOS, остальное отдаём Colima
    cpu_recommended = max(logical - 2, 1)
    lines.append(f"Рекомендовано для Colima: {cpu_recommended} ядер")

    mem_total_gb, mem_used_gb = get_ram_info()
    mem_free_gb = mem_total_gb - mem_used_gb
    # оставляем минимум 4 GB для macOS
    mem_recommended = max(mem_free_gb - 4, 1)
    lines.append(
        f"RAM: всего = {mem_total_gb:.2f}GB, занято ≈ {mem_used_gb:.2f}GB, "
        f"свободно ≈ {mem_free_gb:.2f}GB"
    )
    lines.append(f"Рекомендовано для Colima: {mem_recommended:.2f}GB")

    disk_total, disk_used, disk_avail = get_disk_info()
    lines.append(f"Диск: всего = {disk_total}, занято = {disk_used}, свободно = {disk_avail}")

    lines.append("=== Рекомендации перед стартом Colima ===")
    lines.append(
        f"docker run / colima start с настройками: "
        f"--cpu {cpu_recommended} --memory {mem_recommended:.2f}"
    )

    output = "\n".join(lines)
    print(output)
    LOG_FILE.write_text(output + "\n", encoding="utf-8")
    print(f"Лог сохранён в {LOG_FILE}")


if __name__ == "__main__":
    main()
