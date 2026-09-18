#!/usr/bin/env python3
"""
Проверяет SSL/TLS-сертификат домена или host:port: срок действия,
издателя (issuer), субъект, использованный протокол/шифр и
предупреждает, если сертификат истекает скоро или уже истёк.

Типовая задача техподдержки: быстрая проверка валидности SSL-сертификата
перед эскалацией ("сайт не открывается — ошибка сертификата") — понять,
просрочен ли сертификат, кем выпущен и сколько дней осталось, не
открывая браузер и не гоняя `openssl` вручную.

Использует только стандартную библиотеку (модуль ssl + socket) —
устанавливает TLS-соединение и читает сертификат сервера.

Как запускать:
    python3 ssl_cert_checker.py example.com
    python3 ssl_cert_checker.py example.com:8443
    python3 ssl_cert_checker.py example.com --port 443 --warn-days 14
"""

from __future__ import annotations

import argparse
import datetime
import socket
import ssl
import sys

CERT_DATE_FORMAT = "%b %d %H:%M:%S %Y %Z"


def parse_target(target: str, default_port: int) -> tuple[str, int]:
    if ":" in target:
        host, port_str = target.rsplit(":", 1)
        return host, int(port_str)
    return target, default_port


def fetch_certificate(host: str, port: int, timeout: float) -> tuple[dict, str, str]:
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=host) as tls_sock:
            cert = tls_sock.getpeercert()
            protocol = tls_sock.version() or "unknown"
            cipher = tls_sock.cipher()[0] if tls_sock.cipher() else "unknown"
            return cert, protocol, cipher


def format_name(name_tuples) -> str:
    parts = []
    for rdn in name_tuples:
        for key, value in rdn:
            parts.append(f"{key}={value}")
    return ", ".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", help="домен или host:port, например example.com или example.com:8443")
    parser.add_argument("--port", type=int, default=443, help="порт, если не указан в target (по умолчанию: 443)")
    parser.add_argument("--warn-days", type=int, default=14, help="за сколько дней до истечения предупреждать")
    parser.add_argument("--timeout", type=float, default=10.0, help="таймаут соединения в секундах")
    args = parser.parse_args()

    host, port = parse_target(args.target, args.port)

    print(f"Проверка SSL-сертификата: {host}:{port}")
    print("-" * 50)

    try:
        cert, protocol, cipher = fetch_certificate(host, port, args.timeout)
    except ssl.SSLCertVerificationError as exc:
        print(f"❌ Сертификат не прошёл проверку доверия: {exc.verify_message}")
        sys.exit(1)
    except (socket.timeout, socket.gaierror, ConnectionRefusedError, OSError) as exc:
        print(f"❌ Не удалось подключиться к {host}:{port}: {exc}")
        sys.exit(1)

    subject = format_name(cert.get("subject", []))
    issuer = format_name(cert.get("issuer", []))
    not_before = datetime.datetime.strptime(cert["notBefore"], CERT_DATE_FORMAT)
    not_after = datetime.datetime.strptime(cert["notAfter"], CERT_DATE_FORMAT)
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    days_left = (not_after - now).days

    san = cert.get("subjectAltName", [])
    san_list = ", ".join(value for _, value in san) if san else "—"

    print(f"Subject:      {subject}")
    print(f"Issuer:       {issuer}")
    print(f"SAN:          {san_list}")
    print(f"Действителен: {not_before:%Y-%m-%d} — {not_after:%Y-%m-%d}")
    print(f"Протокол:     {protocol}")
    print(f"Шифр:         {cipher}")
    print()

    if days_left < 0:
        print(f"🔴 Сертификат ПРОСРОЧЕН {-days_left} дн. назад")
        sys.exit(2)
    elif days_left <= args.warn_days:
        print(f"🟡 Сертификат истекает через {days_left} дн. — требует внимания")
        sys.exit(1)
    else:
        print(f"🟢 Сертификат действителен, осталось {days_left} дн.")


if __name__ == "__main__":
    main()
