#!/usr/bin/env python3
"""
Проверяет, какие TCP-порты открыты на хосте (IP или домен).

Типовая задача техподдержки: диагностика недоступности сервиса
("не могу подключиться по FTP/SSH", "сайт не открывается, но пингуется") —
быстро увидеть, слушает ли сервер вообще нужный порт, прежде чем
разбираться дальше (файрвол, сервис не запущен и т.п.).

Использует только стандартную библиотеку (модуль socket).

Как запускать:
    python3 port_check.py example.com
    python3 port_check.py 192.0.2.10 --ports 22 80 443 3306
    python3 port_check.py example.com --timeout 2
"""

from __future__ import annotations

import argparse
import socket

DEFAULT_PORTS = [21, 22, 25, 80, 443, 3306]

WELL_KNOWN_NAMES = {
    21: "FTP", 22: "SSH", 25: "SMTP", 80: "HTTP", 443: "HTTPS", 3306: "MySQL",
}


def check_port(host: str, port: int, timeout: float) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        return result == 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("host", help="IP-адрес или домен")
    parser.add_argument("--ports", nargs="*", type=int, default=DEFAULT_PORTS, help="список портов для проверки")
    parser.add_argument("--timeout", type=float, default=3.0, help="таймаут на порт, секунды")
    args = parser.parse_args()

    try:
        resolved_ip = socket.gethostbyname(args.host)
    except socket.gaierror as exc:
        print(f"❌ Не удалось разрешить имя {args.host}: {exc}")
        raise SystemExit(1)

    print(f"Проверка портов на {args.host} ({resolved_ip})")
    print("-" * 50)

    open_ports = []
    for port in args.ports:
        is_open = check_port(args.host, port, args.timeout)
        name = WELL_KNOWN_NAMES.get(port, "")
        label = f"{port}/{name}" if name else str(port)
        status = "🟢 открыт" if is_open else "🔴 закрыт/фильтруется"
        print(f"  {label:<14} {status}")
        if is_open:
            open_ports.append(port)

    print("-" * 50)
    print(f"Открыто портов: {len(open_ports)} из {len(args.ports)}")


if __name__ == "__main__":
    main()
