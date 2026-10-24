# Отчёт по этапу 0 — минимальное окружение разработки

Дата: 2026-10-24. Ветка: `stage-0` (от `main` 731ad12). Сессия: Claude Code 2.1.310, Fable 5.1; механическая работа — субагенты Sonnet 5.5.
Все утверждения ниже сверены с выводом инструментов этой сессии; где вывода нет — стоит `[допущение]`.

## Вердикт этапа: PARTLY PROVEN

Доказано локально: проверки проекта зелёные одной командой, контракты слоёв держатся, зависимости без уязвимостей и с совместимыми лицензиями, хуки агента работают вживую, установка по README проходит на чистом контейнере Ubuntu, замеры для трёх ADR воспроизводимы скриптами в репозитории, смоук `claude plugin eval` работает. Не доказано: CI на трёх ОС (ветка не отправлена на GitHub — жду вашего решения), установка на чистых Windows и macOS, deny-правило в свежей сессии, пилот плагинов (только набор задач и смоук, как и требовал бриф).

## Что сделано и чем подтверждено

| Требование брифа | Что есть | Доказательство |
|---|---|---|
| AGENTS.md — единственный источник; CLAUDE.md только подключает | `AGENTS.md` (корень, 10 правил), `src/sportorg_ng/AGENTS.md`, `CLAUDE.md` = `@AGENTS.md` + слой Claude Code, `docs/agents/environments.md` (Codex и другие) | файлы в репозитории |
| Проверки — команды проекта, pre-commit, CI | `scripts/check.py` (format, lint, types, imports, tests), `.pre-commit-config.yaml` (быстрые на commit, тесты на push, через `uvx pre-commit`), `.github/workflows/ci.yml` | `uv run python scripts/check.py --keep-going`: `ok format / lint / types / imports / tests`, 23 passed, ~5 с |
| import-linter | 3 контракта: ядро чистое; никто не импортирует ui; ядро и адаптеры не зависят от национальных пакетов | `Contracts: 3 kept, 0 broken` |
| CI: Windows, Linux, macOS, нижняя версия Python | матрица 3 ОС × {3.14, 3.15} + job `clean-install` (контейнер `ubuntu:24.04`, шаги README дословно) | **не запускался** — требует push |
| Backlog.md — реестр задач | `backlog/` инициализирован CLI 1.54.0; 7 milestones (этапы 0–6), 8 задач с критериями приёмки | `backlog task list --plain`: TASK-1…TASK-8 |
| Артефакты — обычные файлы | `docs/evidence/stage-0/` (матрица Python, замеры тайпчекеров, кандидаты из истории, инвентарь плагинов, факты по Codex и Claude Code, замер окружений, чистая установка, смоук eval), `docs/adr/0001–0005`, `docs/risks.md`, `docs/data-request.md`, `docs/sources/` | файлы |
| Legacy только для чтения; исполнение из клона | правило 1 AGENTS.md; `scripts/legacy_clone.py` (закреплённый коммит 30d849dd); deny `Edit(//c/Users/ank/Prog/Orient/_other/**)`; хук-страж | страж заблокировал мою же команду `mkdir` под legacy-путём и команду с `cd` в legacy (вывод `PreToolUse:Bash hook error … read-only`); 23 теста, из них 17 на страж |
| Установка по README на чистой машине | контейнер `ubuntu:24.04` без uv/python/git: установка uv, `uv sync` 21 с, `check.py` — все 5 шагов ok, 23 passed, `uv audit` чисто; то же в образе devcontainer (`uv sync` 18 с, все шаги ok) | `docs/evidence/stage-0/clean-install-ubuntu.txt`, `docs/evidence/stage-0/devcontainer-check.txt` (клонирование заменено копией рабочего дерева, т.к. ветка не отправлена; первые прогоны выявили EXE001/EXE002 и неверную форму запуска `check_licenses` — см. «Инциденты») |
| Уязвимости и лицензии | `uv audit` (0.13.1, experimental) + `scripts/check_licenses.py` (pip-licenses, allowlist под GPL-3.0-or-later) | `Found no known vulnerabilities … in 19 packages`; `checked 16 packages; problems: 0` |
| Реестр рисков | `docs/risks.md`: 15 рисков, каждый с этапом проверки и видом доказательства | файл |
| Запрос данных | `docs/data-request.md`: 13 позиций, статус у всех «нет», кроме истории git (получено) | файл |

### Решения с данными (ADR)
- **ADR-0001 Python**: разработка 3.14, нижняя граница 3.14, в CI лента 3.15 как ранний сигнал. Данные: матрица 62 пакетов с PyPI (колёса cp315 есть у PySide6 6.12, cryptography, orjson, ruff, mypy, basedpyright, ty…; нет у pyyaml 6.0.3, hidapi, nuitka); на 3.15 `uv add` упал на сборке pyyaml с требованием MSVC. EOL: 3.14 → 2030-10, 3.15 → 2031-10.
- **ADR-0002 тайпчекер**: basedpyright 1.40.2, режим `all`. Данные: 17 файлов-ловушек × 6 инструментов на legacy (177 файлов): basedpyright 15/17, mypy 14/17, pyrefly 12, zuban 12 (AGPL), pyright 10, ty 8 (но в 10 раз быстрее). Один файл: basedpyright 1,19 с, mypy 1,54 с, ty 0,13 с.
- **ADR-0003 среда**: на Windows агентная работа в WSL2 с репозиторием на ext4; отдельный нативный клон для GUI; devcontainer как воспроизводимый эквивалент. Данные: холодный `uv sync` NTFS 37 с, WSL ext4 10,5 с, WSL /mnt/c 75 с, Docker bind 83 с, Docker внутри 11 с; у Claude Code нет песочницы на нативной Windows; `python3` на этой машине — заглушка Microsoft Store.
- **ADR-0004 мелкие выборы**: собственный `scripts/check.py` вместо poe/nox/just; pre-commit через `uvx`; `uv audit`; pip-licenses; GitHub Actions с закреплённым `setup-uv@v10.3.2` (плавающего `v10` нет — проверено API); `uv_build`.
- **ADR-0005 слой агентов**: Backlog.md — единственный статус; планы Superpowers в `docs/plans/`, спецификации в `docs/specs/`; code-modernization — только анализ и верификация, его `MODERNIZATION_BRIEF.md` не используется; хуки; deny-правило; пилот.

### Слой Claude Code
- Хуки (`.claude/settings.json` → `scripts/hooks/`): страж PreToolUse (deny записи в legacy, ask для `tests/golden/**`), PostToolUse ruff + basedpyright по файлу (1,8–2,0 с), Stop — быстрые тесты затронутых пакетов. Все три сработали в этой сессии на моих собственных правках (хук после правки поймал RUF043 и форматирование в тесте).
- Пилот плагинов: `evals/` — смоук без инструментов (score 1.00, 4 с, $0.00), смоук с плагином в двух руках (with/without обе 1.00, плагин code-modernization 1.0.0 загружен, $0,0019/$0,0012), 7 задач из истории legacy (c1–c4 — фиксы с содержательными тестами, f1–f3 — фичи с тестами как спецификацией) со scaffold-скриптами и грейдерами. Полный прогон — задача TASK-2, только с вашего согласия и `--max-cost-usd`.
- Superpowers и code-modernization: инвентарь артефактов в `docs/evidence/stage-0/plugins-inventory.md`; пересечения с Backlog.md (чекбоксы планов, `MODERNIZATION_BRIEF.md`, леджер `.superpowers/sdd`) разрешены в ADR-0005.

### Другие среды
Codex CLI 0.164: читает AGENTS.md (корневой и вложенные), скиллы в `.agents/skills`, хуки `.codex/hooks.json`, MCP, профили разрешений с `deny` (beta), нативная песочница Windows; Superpowers ставится из маркетплейса Codex. Таблица эквивалентов — `docs/agents/environments.md`; хуки для Codex не настроены (TASK-3, нужен пользователь Codex для проверки).

## Находки и инциденты (важно для правил проекта)
1. **Относительные пути в `permissions.deny` не работают.** `Edit(../_deny_probe/**)` не заблокировал правку; `Edit(//c/Users/ank/Prog/Orient/_deny_probe/**)` заблокировал («File is in a directory that is denied by your permission settings»). Правило в `settings.json` теперь абсолютное и привязано к этой машине; другим мейнтейнерам — свой путь в `settings.local.json`. Повторить в свежей сессии — TASK-1.
2. **Сломанный venv блокирует все инструменты, если хук зависит от venv.** Субагент замера запустил из WSL `uv sync` в основном checkout (унаследованный cwd); `.venv` стал линуксовым, страж (`uv run --no-sync`) падал, и Bash/PowerShell/Edit/Write были заблокированы до вашего вмешательства. Исправлено: страж запускается `uv run --no-project`; правило «один checkout — один тулчейн» записано в AGENTS.md и ADR-0003.
3. **Текстовый страж ловит собственные команды.** Маркер `/_other/` блокировал правку настроек; сужен до `pysport-legacy`. Страж остаётся best-effort, правило — в AGENTS.md.
4. **Windows не видит EXE001/EXE002.** В контейнере ruff нашёл shebang без исполняемого бита (`bench_typecheckers.py`) — на Windows это правило молчит. Shebang убран; лента Linux в CI ловит такое.
5. **Классификатор авто-режима** отклонил: межсессионное сообщение соседней сессии, `rm -rf` вне проекта, правку `permissions.deny` через Bash. Остался файл `../_deny_probe/probe.txt` — удалите вручную.
6. `claude plugin eval` читает кейсы из каталога плагина, если цель — установленный плагин; для кейсов проекта цель `.`, а плагин копируется в `tools/plugins/` (junction отвергается, копия внутри `evals/` — тоже). Скрипт `scripts/pilot_setup.py`.
7. В контейнере `scripts/check_licenses.py` упал с `ModuleNotFoundError: scripts` — скрипт импортирует `scripts._json`, а запуск файлом не ставит корень репозитория в `sys.path` (локально я его после переписывания не перезапускал). Исправлено на `python -m scripts.check_licenses` в AGENTS.md и CI; урок — любой скрипт с импортом `scripts.*` запускается только модулем.

## Что не сделано или PARTLY
- CI не запускался: ветка не отправлена. Рекомендую отправить `stage-0` (не `main`), проверить матрицу и `clean-install`, затем решать про merge.
- Чистая установка проверена только на Ubuntu (контейнер); Windows и macOS — TASK-4.
- Deny-правило в свежей сессии — TASK-1; хуки Codex — TASK-3; пилот — TASK-2.
- Devcontainer проверен только сборкой образа и прогоном проверок внутри (не из VS Code).
- Замеры окружений — одна машина; macOS не измерялся.

## Вопросы и решения для вас (варианты, моя рекомендация первой)
1. **Лицензия проекта**: (а) GPL-3.0-or-later — можно переносить шаблоны/данные legacy, allowlist уже под неё; (б) permissive (MIT/Apache) — ничего из legacy не копировать, только воспроизводить поведение. Рекомендую (а).
2. **Персональные данные корпуса**: (а) корпус вне репозитория, в репозитории — скрипт анонимизации и хэши; (б) анонимизированный корпус в репозитории. Рекомендую (а) до решения о псевдонимизации детей.
3. **Push ветки `stage-0` для запуска CI**: (а) разрешить push ветки сейчас; (б) вы отправляете сами. Рекомендую (а).
4. **Пилот плагинов**: согласие на полный прогон из WSL2 с потолком, предлагаю `--max-cost-usd 25` (7 кейсов × 3 прогона × 2 руки, Sonnet). Или отложить до этапа 1.
5. **Python 3.14 как версия разработки** (ADR-0001) — подтвердить или настоять на 3.15 с риском сборки pyyaml из исходников.
6. **code-modernization в настройках проекта**: оставить включённым (нужен Git Bash и `python3` → на Windows фактически только WSL) или включать локально по мере пилота.
7. **Абсолютный путь в deny-правиле** с вашим именем пользователя в коммите — приемлемо, или перенести в `settings.local.json` и оставить в репозитории только документацию?

## Запрос данных
`docs/data-request.md` — 13 позиций. Без п. 1–4 этап 2 не начнётся; без п. 7 (тексты правил) этап 3 даст пустые ячейки матрицы.
