#!/usr/bin/env python3
"""
Объединяющая диагностика домена: прогоняет DNS-записи, открытые порты,
SSL-сертификат, HTTP-доступность и (опционально) WHOIS, выводит единый
читаемый отчёт.

Типовая задача техподдержки: "полный тест домена" при обращении вида
"сайт не работает" — вместо того чтобы вручную запускать dns_lookup.py,
port_check.py, ssl_cert_checker.py и http_health_check.py по отдельности,
один запуск даёт цельную картину и помогает быстро понять, на каком
этапе проблема (DNS не резолвится / порт закрыт / сертификат просрочен /
сайт отвечает ошибкой).

Требует зависимости остальных скриптов этой папки:
    pip install dnspython requests
    pip install python-whois   # опционально, для блока WHOIS

Как запускать:
    python3 domain_full_check.py example.com
    python3 domain_full_check.py example.com --skip-whois
    python3 domain_full_check.py example.com --ports 80 443 22
"""

from __future__ import annotations

import argparse
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dns.resolver  # noqa: E402
import requests  # noqa: E402

from dns_lookup import RECORD_TYPES, lookup as dns_lookup_record  # noqa: E402
from port_check import DEFAULT_PORTS, WELL_KNOWN_NAMES, check_port  # noqa: E402
from ssl_cert_checker import fetch_certificate, format_name, CERT_DATE_FORMAT  # noqa: E402
from http_health_check import normalize_url  # noqa: E402

import datetime  # noqa: E402
import time  # noqa: E402


def section(title: str) -> None:
    print()
    print(f"== {title} ==")
    print("-" * 50)


def run_dns_section(domain: str, resolver_ip: str | None) -> None:
    section("DNS")
    resolver = dns.resolver.Resolver()
    if resolver_ip:
        resolver.nameservers = [resolver_ip]

    for record_type in RECORD_TYPES:
        try:
            values = dns_lookup_record(domain, record_type, resolver)
        except dns.resolver.NXDOMAIN:
            print(f"❌ Домен {domain} не существует (NXDOMAIN)")
            return
        if values:
            print(f"{record_type}: {', '.join(values)}")
        else:
            print(f"{record_type}: (нет записей)")


def run_port_section(host: str, ports: list[int], timeout: float) -> None:
    section("Порты")
    try:
        resolved_ip = socket.gethostbyname(host)
    except socket.gaierror as exc:
        print(f"❌ Не удалось разрешить имя {host}: {exc}")
        return

    print(f"IP: {resolved_ip}")
    for port in ports:
        is_open = check_port(host, port, timeout)
        name = WELL_KNOWN_NAMES.get(port, "")
        label = f"{port}/{name}" if name else str(port)
        status = "открыт" if is_open else "закрыт/фильтруется"
        print(f"  {label:<14} {status}")


def run_ssl_section(host: str, port: int, timeout: float, warn_days: int) -> None:
    section("SSL-сертификат")
    try:
        cert, protocol, cipher = fetch_certificate(host, port, timeout)
    except Exception as exc:  # noqa: BLE001 — здесь нужен единый fallback для отчёта
        print(f"❌ Не удалось проверить сертификат: {exc}")
        return

    subject = format_name(cert.get("subject", []))
    issuer = format_name(cert.get("issuer", []))
    not_after = datetime.datetime.strptime(cert["notAfter"], CERT_DATE_FORMAT)
    days_left = (not_after - datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)).days

    print(f"Subject:  {subject}")
    print(f"Issuer:   {issuer}")
    print(f"До:       {not_after:%Y-%m-%d} ({days_left} дн.)")
    print(f"Протокол: {protocol}, шифр: {cipher}")

    if days_left < 0:
        print(f"🔴 Сертификат просрочен {-days_left} дн. назад")
    elif days_left <= warn_days:
        print(f"🟡 Истекает через {days_left} дн.")
    else:
        print("🟢 Валиден")


def run_http_section(url: str, timeout: float) -> None:
    section("HTTP")
    start = time.monotonic()
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
    except requests.exceptions.RequestException as exc:
        print(f"❌ Ошибка запроса: {exc}")
        return
    elapsed = time.monotonic() - start

    if response.history:
        for step in response.history:
            print(f"  {step.status_code}  {step.url}")
    print(f"Итог: {response.status_code} {response.reason}  ({elapsed:.3f} с, {response.url})")


def run_whois_section(domain: str) -> None:
    section("WHOIS")
    try:
        import whois  # type: ignore
    except ImportError:
        print("Пропущено: не установлен пакет python-whois (pip install python-whois)")
        return

    try:
        record = whois.whois(domain)
    except Exception as exc:  # noqa: BLE001 — библиотека кидает разные исключения на разные TLD
        print(f"❌ Не удалось получить WHOIS: {exc}")
        return

    registrar = record.get("registrar") if hasattr(record, "get") else getattr(record, "registrar", None)
    creation = record.get("creation_date") if hasattr(record, "get") else getattr(record, "creation_date", None)
    expiration = record.get("expiration_date") if hasattr(record, "get") else getattr(record, "expiration_date", None)

    print(f"Registrar:   {registrar}")
    print(f"Создан:      {creation}")
    print(f"Истекает:    {expiration}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("domain", help="домен для полной проверки, например example.com")
    parser.add_argument("--ports", nargs="*", type=int, default=DEFAULT_PORTS)
    parser.add_argument("--ssl-port", type=int, default=443)
    parser.add_argument("--dns-resolver", default=None, help="IP DNS-сервера (по умолчанию: системный)")
    parser.add_argument("--warn-days", type=int, default=14, help="порог предупреждения по SSL")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--skip-whois", action="store_true", help="не выполнять WHOIS-запрос")
    args = parser.parse_args()

    print(f"Полная диагностика домена: {args.domain}")
    print("=" * 50)

    run_dns_section(args.domain, args.dns_resolver)
    run_port_section(args.domain, args.ports, args.timeout)
    run_ssl_section(args.domain, args.ssl_port, args.timeout, args.warn_days)
    run_http_section(normalize_url(args.domain), args.timeout)
    if not args.skip_whois:
        run_whois_section(args.domain)

    print()
    print("=" * 50)
    print("Готово.")


if __name__ == "__main__":
    main()
