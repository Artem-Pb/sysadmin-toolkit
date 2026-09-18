# support-diagnostics-scripts

CLI-утилиты для диагностики доменов и серверов — типовые проверки,
которые пригождаются в техподдержке хостинга: DNS, открытые порты,
SSL-сертификат, доступность по HTTP и общий отчёт по домену.

Используют только публичные протоколы (DNS, TLS handshake, HTTP,
опционально WHOIS) — никаких обращений к внутренним системам, кредов
или реальных клиентских данных здесь нет и быть не должно.

## Установка

```bash
pip install -r requirements.txt
```

`python-whois` нужен только для блока WHOIS в `domain_full_check.py` —
без него скрипт просто пропустит этот раздел.

## Скрипты

| Скрипт | Назначение | Пример запуска |
|---|---|---|
| [ssl_cert_checker.py](ssl_cert_checker.py) | Проверка SSL-сертификата: срок действия, issuer, протокол/шифр, предупреждение об истечении | `python3 ssl_cert_checker.py example.com` |
| [dns_lookup.py](dns_lookup.py) | Полный набор DNS-записей домена (A, AAAA, MX, TXT, NS, CNAME) | `python3 dns_lookup.py example.com` |
| [port_check.py](port_check.py) | Проверка открытых TCP-портов на хосте (по умолчанию: 21, 22, 25, 80, 443, 3306) | `python3 port_check.py example.com --ports 22 80 443` |
| [http_health_check.py](http_health_check.py) | Статус-код, цепочка редиректов, время ответа и заголовки по URL | `python3 http_health_check.py https://example.com` |
| [domain_full_check.py](domain_full_check.py) | Объединяющий отчёт: DNS + порты + SSL + HTTP + WHOIS одним запуском | `python3 domain_full_check.py example.com` |

## Типовые сценарии применения

- **"Сайт не открывается"** → `domain_full_check.py <домен>` — единый
  отчёт, на каком этапе проблема (DNS не резолвится / порт закрыт /
  сертификат просрочен / сервер отвечает ошибкой).
- **"Ошибка сертификата в браузере"** → `ssl_cert_checker.py <домен>` —
  проверка валидности перед эскалацией на следующую линию.
- **"Почта не доходит"** → `dns_lookup.py <домен> --types MX TXT` —
  проверка MX и SPF/DKIM-подобных TXT-записей.
- **"Не подключается по FTP/SSH"** → `port_check.py <хост> --ports 21 22`.

## Требования

Python 3.10+. Зависимости: `dnspython`, `requests`, опционально
`python-whois` (см. `requirements.txt`).
