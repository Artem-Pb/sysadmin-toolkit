#!/usr/bin/env python3
"""
Проверяет HTTP(S)-доступность URL: итоговый статус-код, полную цепочку
редиректов, время ответа и основные заголовки.

Типовая задача техподдержки: диагностика "сайт не открывается" или
"выдаёт ошибку" — увидеть, куда реально ведут редиректы (например,
зацикленный редирект http->https), какой код отдаёт сервер и сколько
он отвечает, не открывая сайт в браузере с DevTools.

Требует стороннюю библиотеку requests:
    pip install requests

Как запускать:
    python3 http_health_check.py https://example.com
    python3 http_health_check.py example.com --timeout 5
"""

from __future__ import annotations

import argparse
import sys
import time

try:
    import requests
except ImportError:
    print("Требуется пакет requests: pip install requests", file=sys.stderr)
    sys.exit(1)

DEFAULT_HEADERS_TO_SHOW = [
    "server", "content-type", "content-length", "cache-control", "location",
]


def normalize_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return f"https://{url}"
    return url


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", help="URL или домен, например example.com или https://example.com/path")
    parser.add_argument("--timeout", type=float, default=10.0, help="таймаут запроса в секундах")
    parser.add_argument("--no-verify", action="store_true", help="не проверять валидность SSL-сертификата")
    args = parser.parse_args()

    url = normalize_url(args.url)
    print(f"HTTP-проверка: {url}")
    print("-" * 50)

    start = time.monotonic()
    try:
        response = requests.get(
            url, timeout=args.timeout, allow_redirects=True, verify=not args.no_verify,
        )
    except requests.exceptions.SSLError as exc:
        print(f"❌ Ошибка SSL: {exc}")
        sys.exit(1)
    except requests.exceptions.ConnectionError as exc:
        print(f"❌ Не удалось подключиться: {exc}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"❌ Таймаут ({args.timeout}с) — сервер не ответил вовремя")
        sys.exit(1)
    elapsed = time.monotonic() - start

    if response.history:
        print("Цепочка редиректов:")
        for step in response.history:
            print(f"  {step.status_code}  {step.url}")
        print(f"  {response.status_code}  {response.url}  (итог)")
    else:
        print(f"Редиректов не было, итоговый URL: {response.url}")

    print()
    print(f"Статус-код:     {response.status_code} {response.reason}")
    print(f"Время ответа:   {elapsed:.3f} с")
    print(f"Размер тела:    {len(response.content)} байт")
    print()

    print("Ключевые заголовки:")
    for header in DEFAULT_HEADERS_TO_SHOW:
        value = response.headers.get(header)
        if value:
            print(f"  {header}: {value}")

    if 200 <= response.status_code < 300:
        print()
        print("🟢 Сайт отвечает нормально")
    elif 300 <= response.status_code < 400:
        print()
        print("🟡 Финальный ответ — редирект (возможно, зациклен или не долетает до цели)")
    else:
        print()
        print(f"🔴 Сайт отвечает ошибкой {response.status_code}")
        sys.exit(2)


if __name__ == "__main__":
    main()
