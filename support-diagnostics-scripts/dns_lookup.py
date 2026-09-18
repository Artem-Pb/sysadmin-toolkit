#!/usr/bin/env python3
"""
Выводит полный набор DNS-записей домена: A, AAAA, MX, TXT, NS, CNAME.

Типовая задача техподдержки: диагностика недоступности домена или почты
("сайт не открывается", "письма не доходят") — быстро посмотреть, что
реально отдаёт DNS (правильно ли настроен A/CNAME, есть ли MX для почты,
не потерялась ли TXT-запись с SPF/DKIM), не открывая сторонние онлайн-
сервисы.

Требует стороннюю библиотеку dnspython:
    pip install dnspython

Как запускать:
    python3 dns_lookup.py example.com
    python3 dns_lookup.py example.com --types A MX TXT
    python3 dns_lookup.py example.com --resolver 8.8.8.8
"""

from __future__ import annotations

import argparse
import sys

try:
    import dns.resolver
except ImportError:
    print("Требуется пакет dnspython: pip install dnspython", file=sys.stderr)
    sys.exit(1)

RECORD_TYPES = ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]


def lookup(domain: str, record_type: str, resolver: "dns.resolver.Resolver") -> list[str]:
    try:
        answer = resolver.resolve(domain, record_type)
        return [rdata.to_text() for rdata in answer]
    except dns.resolver.NoAnswer:
        return []
    except dns.resolver.NXDOMAIN:
        raise
    except dns.exception.DNSException as exc:
        return [f"(ошибка: {exc})"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("domain", help="домен для проверки, например example.com")
    parser.add_argument("--types", nargs="*", default=RECORD_TYPES, help="какие типы записей запрашивать")
    parser.add_argument("--resolver", default=None, help="IP DNS-сервера для запроса (по умолчанию: системный)")
    parser.add_argument("--timeout", type=float, default=5.0, help="таймаут запроса в секундах")
    args = parser.parse_args()

    resolver = dns.resolver.Resolver()
    resolver.lifetime = args.timeout
    resolver.timeout = args.timeout
    if args.resolver:
        resolver.nameservers = [args.resolver]

    print(f"DNS-записи для {args.domain}")
    if args.resolver:
        print(f"(через резолвер {args.resolver})")
    print("-" * 50)

    for record_type in args.types:
        try:
            values = lookup(args.domain, record_type, resolver)
        except dns.resolver.NXDOMAIN:
            print(f"❌ Домен {args.domain} не существует (NXDOMAIN)")
            sys.exit(1)

        if values:
            print(f"{record_type}:")
            for value in values:
                print(f"  {value}")
        else:
            print(f"{record_type}: (нет записей)")


if __name__ == "__main__":
    main()
