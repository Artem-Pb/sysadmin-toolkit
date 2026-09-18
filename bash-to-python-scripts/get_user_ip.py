#!/usr/bin/env python3
"""
Выводит одну строку "имя_пользователя@локальный_ip" — определяет текущего
пользователя ОС и его локальный IP-адрес (первый неloopback-интерфейс).

Зачем был нужен оригинал (bash, ssh_scan.sh, на деле whoip.sh):
Несмотря на имя файла, скрипт не сканирует SSH — он просто быстро
показывает "кто я и какой у меня IP" одной строкой, что удобно
подставлять в другие команды/логи (например при подключении по SSH).

Как запускать:
    python3 get_user_ip.py

Аргументы: нет.
"""

import getpass
import socket


def get_local_ip() -> str:
    # Открываем UDP-сокет "в никуда" — реального пакета не уходит,
    # но ОС резолвит исходящий интерфейс и его IP.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def main() -> None:
    user = getpass.getuser()
    ip = get_local_ip()
    print(f"{user}@{ip}")


if __name__ == "__main__":
    main()
