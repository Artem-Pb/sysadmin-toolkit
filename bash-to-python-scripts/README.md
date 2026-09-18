# bash-to-python-scripts

Набор bash-скриптов, накопленных за время учёбы/работы (macOS, git,
school21), переписанный на Python 3 стандартной библиотекой — без
внешних зависимостей.

Оригинальные `.sh` файлы не менялись и не переносились сюда — эта
папка содержит только независимые Python-версии с сохранённой логикой
и docstring-описанием назначения каждого скрипта.

Реальные пути, имена и URL внутренних репозиториев из оригиналов
заменены на аргументы командной строки / плейсхолдеры — секретов и
хардкодов здесь нет.

## Скрипты

| Скрипт | Назначение | Как запустить |
|---|---|---|
| [check_mac_resources.py](check_mac_resources.py) | Проверяет CPU/RAM/диск на macOS и даёт рекомендацию `--cpu`/`--memory` для запуска Colima | `python3 check_mac_resources.py` |
| [collect_c_source_files.py](collect_c_source_files.py) | Собирает все `.c`/`.h` файлы папки в один текстовый файл для ревью/дебага | `python3 collect_c_source_files.py [папка] -o all_code.txt` |
| [collect_markdown_files.py](collect_markdown_files.py) | Собирает все `.md` файлы из домашней директории в один отчёт со сводкой по папкам | `python3 collect_markdown_files.py --root ~ -o all-md.md` |
| [capture_training_screenshots.py](capture_training_screenshots.py) | Периодически делает скриншоты экрана и складывает их в папку — сбор датасета для обучения нейросети | `python3 capture_training_screenshots.py --output-dir ./dataset --interval 2 --count 100` |
| [check_file_exists.py](check_file_exists.py) | Интерактивно спрашивает путь к файлу и сообщает, существует ли он | `python3 check_file_exists.py` |
| [merge_git_repos.py](merge_git_repos.py) | Сливает все ветки одного git-репозитория в другой и пушит результат | `python3 merge_git_repos.py --target <url> --source <url>` |
| [clone_and_copy_repos.py](clone_and_copy_repos.py) | Клонирует список репозиториев из файла, чистит служебные файлы и копирует их как `Project1`, `Project2`, ... без `.git` | `python3 clone_and_copy_repos.py --repo-list repos.txt --dest ~/Archive` |
| [greet_user.py](greet_user.py) | Учебный скрипт-приветствие (переменные окружения, ввод, дата) | `python3 greet_user.py` |
| [search_string_in_c_files.py](search_string_in_c_files.py) | Ищет подстроку во всех `.c` файлах папки, печатает прогресс и сохраняет отчёт с номерами строк | `python3 search_string_in_c_files.py "printf"` |
| [rename_c_files_to_txt.py](rename_c_files_to_txt.py) | Переименовывает все `.c`/`.h` файлы в `.txt` | `python3 rename_c_files_to_txt.py [папка]` |
| [remove_file_from_branches.py](remove_file_from_branches.py) | Удаляет указанный файл из всех веток git (кроме main), коммитит и пушит | `python3 remove_file_from_branches.py --file README.md --dry-run` |
| [check_sites_reachable.py](check_sites_reachable.py) | Проверяет доступность списка сайтов через ping | `python3 check_sites_reachable.py google.com ya.ru` |
| [get_user_ip.py](get_user_ip.py) | Печатает строку `пользователь@локальный_ip` | `python3 get_user_ip.py` |
| [create_c_stub_files.py](create_c_stub_files.py) | Парсит исходник, находит объявления функций (`int`/`void`) и создаёт пустые `.c`/`_test.c` заготовки | `python3 create_c_stub_files.py source.c` |

## Требования

Python 3.10+, только стандартная библиотека. Внешние зависимости не
используются.

## Примечание о безопасности

Скрипты, работающие с git (`merge_git_repos.py`,
`clone_and_copy_repos.py`, `remove_file_from_branches.py`), выполняют
`push` в удалённые репозитории — URL репозиториев передаются
аргументами, ничего не захардкожено. Перед запуском на реальных данных
проверяйте аргументы и, где есть `--dry-run`, используйте его первым.
