# Независимая проверка этапа 0

Дата: 2026-10-24. Ветка `stage-0`, HEAD `aeb0d35` (совпадает с `origin/stage-0`). Сессия: Claude Code, Opus 5.5,
отдельная от сессии, выполнявшей этап. Метод: по чек-листу `docs/reports/stage-0-verification-prompt.md`
сначала собраны собственные факты (команды запущены в этой сессии, выводы ниже), и только потом прочитан
`docs/reports/stage-0.md` для сравнения. Ничего в проекте не исправлялось: канарейки откатаны, все
эксперименты с изменением файлов — на клонах во временном каталоге. После каждой проверки
`git status --porcelain` был пуст и в репозитории, и в legacy (HEAD `30d849d`). На момент записи отчёта в
репозитории, кроме этого файла, есть неотслеживаемый `scripts/probe_legacy_protection.py` (создан в 21:48 не
этой сессией, судя по docstring — к решению мейнтейнера 7 о `.legacy/`); проверка его не трогала и не оценивала.

Выводы инструментов — в `docs/evidence/stage-0/verification/` (индекс — `README.md` там же), сценарии — в
`docs/evidence/stage-0/verification/scripts/`. Выводы, которые сначала существовали только в журнале сессии,
сняты повторно в 21:53–21:59 на чистом клоне того же коммита `aeb0d35`; поэтому времена в файлах могут
немного отличаться от первых прогонов, на вердикты это не влияет.

## Вердикт: PARTLY PROVEN

Доказано: проверки проекта зелёные одной командой локально, в CI (7/7 джобов), в чистом контейнере Ubuntu,
в devcontainer и в чистой Windows (Windows Sandbox); канарейки ловятся; legacy защищён правилом,
deny-правилом и стражем; хуки Claude Code работают вживую; ADR-0002 воспроизводится точно.

Не доказано или опровергнуто: `pre-commit run --all-files` красный во всех средах; README дословно не
работает ни в Ubuntu, ни в Windows; лента Python 3.15 на macOS зелёная только за счёт сборки `grimp` из
исходников (противоречит ADR-0001); цифры ADR-0003 для нативной Windows не воспроизводятся; тесты стража
не проверяют сам хук (`main()`), PowerShell и отказоустойчивость; macOS и старые Windows не проверялись.

## Чек-лист

### 1. AGENTS.md — единственный источник, CLAUDE.md только подключает — PARTLY PROVEN
Структура верна: `CLAUDE.md` и `src/sportorg_ng/CLAUDE.md` начинаются с `@AGENTS.md`. Повторы правил:
- `CLAUDE.md:10` «Checkboxes in plans are not status; close tasks with `backlog task edit`» = `AGENTS.md:49-50` (правило 6);
- `CLAUDE.md:22-23` (автономные прогоны под WSL2) ≈ `AGENTS.md:32-33`;
- `CLAUDE.md:17` «Hooks only run project commands» ≈ `AGENTS.md:30`;
- `CLAUDE.md:20-21` «Reading legacy is allowed…» частично повторяет правило 1.

Повторы мелкие, но бриф прямо требует «правила не дублируются».

### 2. Проверки качества — PROVEN
`uv sync` → exit 0. `uv run python scripts/check.py --keep-going` → exit 0:
```
== format  27 files already formatted
== lint    All checks passed!
== types   0 errors, 0 warnings, 0 notes
== imports Contracts: 3 kept, 0 broken.
== tests   23 passed in 0.07s
```
Скрипт включает ruff (формат, линт), basedpyright, import-linter, pytest `[код: scripts/check.py:45-59]`.
Сравнения с оракулом пока нет (по брифу — этап 2). Доказательство: `verification/checks-rerun.txt`.

### 3. Канарейки — PROVEN
Каждая создана, прогнан `check.py --keep-going`, удалена; после каждой `git status` пуст.

| канарейка | вывод | итог |
|---|---|---|
| (а) `import os` в `core/` | `sportorg_ng.core is not allowed to import os: sportorg_ng.core.canary_os -> os (l.3)` | `FAIL imports`, exit 1 |
| (б) `def add(a, b)` | ruff `ANN201`, `ANN001`×2; basedpyright 6 ошибок (`reportUnknownParameterType`, `reportMissingParameterType`) | `FAIL lint`, `FAIL types`, exit 1 |
| (в) `x: int = "s"  # type: ignore` | ruff `PGH003`; basedpyright `` `type: ignore` comment must specify a rule (reportIgnoreCommentWithoutRule) `` | `FAIL lint`, `FAIL types`, exit 1 |
| (г) сломанный тест | `1 failed, 23 passed` | `FAIL tests`, exit 1 |
| доп.: лишний `noqa`, лишний `pyright: ignore`, `Any` | `RUF100`, `reportUnnecessaryTypeIgnoreComment`, `ANN401`, `reportExplicitAny` | ловятся |

Доказательство: `verification/checks-rerun.txt` (разделы item 3a–3d, extra).

### 4. Pre-commit — NOT PROVEN
Набор инструментов тот же, что в `check.py` (плюс `uv lock --check`), но результат другой:
- `uvx pre-commit run --all-files` на машине мейнтейнера: `error: Failed to build pyyaml==6.0.3 … Microsoft
  Visual C++ 14.0 or greater is required`, exit 1 — `uvx` выбрал установленный CPython 3.15, а у pyyaml нет
  колеса cp315.
- `uvx --python 3.14 pre-commit run --all-files`: `ruff check … Failed` на 13 файлах
  `scripts/typecheck_fixtures/`, exit 1. Тот же провал — в чистой Windows и в devcontainer.
  Причина: pre-commit передаёт ruff имена файлов, а без `--force-exclude` ruff не применяет к ним
  `extend-exclude` `[код: pyproject.toml:35]`; проверка: `ruff check --force-exclude <fixture>` →
  `No Python files found`. `check.py` передаёт каталоги, поэтому он зелёный.
- Стадия pre-push: `pytest (on push)….Passed`.

В CI pre-commit не запускается, поэтому расхождение там не видно.
Доказательства: `verification/checks-rerun.txt` (разделы item 4), `clean-install-windows.txt`, `devcontainer.txt`.

### 5. CI — PROVEN (с оговоркой по 3.15)
Матрица `[ubuntu, windows, macos] × ["3.14", "3.15"]` + `clean-install` `[код: .github/workflows/ci.yml:17-18]`;
та же команда `uv run --no-sync python scripts/check.py --keep-going` `[код: ci.yml:29]`.
`gh run list --branch stage-0`: 2 прогона, оба `success`; run 40093927242 на `aeb0d35` — 7/7 джобов success,
в логах `ok format/lint/types/imports/tests`, `23 passed`, CPython 3.14.9 и 3.15.1.
Оговорка: в джобе `macos-latest / py3.15` есть `Building grimp==3.17` — см. находку Н1.
Доказательство: `verification/checks-rerun.txt` (раздел item 5).

### 6. Backlog.md — PARTLY PROVEN
`backlog task list --plain`: TASK-1…8, все To Do. `backlog milestone list`: m-0…m-6, m-0 — 0/6.
Критерии TASK-1, 2, 4, 5, 8 сформулированы как доказательства; TASK-7 #1, #3–#5 и TASK-6 #2 называют
артефакт без критерия проверки. Второго реестра нет: единственные чекбоксы вне `backlog/` — цитата формата
Backlog.md в блоке кода (`docs/evidence/stage-0/agent-tooling-facts.md:84-85`); `docs/plans/` и
`docs/specs/` не существуют. Доказательство: `verification/checks-rerun.txt` (раздел item 6).

### 7. Legacy только для чтения — PROVEN (страж — best effort)
- (а) Правило: `AGENTS.md:38-39`.
- (б) Edit файла `_config.yml` в legacy: `File is in a directory that is denied by your permission
  settings.` — отказ самого правила разрешений; абсолютная форма работает в свежей сессии. Legacy после
  попытки чистый.
- (в) Страж: для `rm -rf ../_other/pysport-legacy/x` → `{"permissionDecision": "deny", …}`; для
  `git -C ../_other/pysport-legacy log -1` → пусто. Буквальную команду из чек-листа (`echo '…' | …`)
  заблокировал сам живой страж, поэтому JSON подавался из файла.
- (г) `legacy_clone.py --dest <tmp>/legacy-probe` → `at 30d849dde1f7ebe04599098b3344b72fdb1210fe`, совпадает с
  `AGENTS.md:17`; повторный запуск → `already at …`.

Ограничения стража:
- ложные срабатывания: три мои команды только для чтения отклонены, потому что путь legacy и `cd`/`rm`
  по файлу проекта стояли в одной строке;
- обходы: `python -c "open('../_other/pysport-legacy/x.txt','w')…"` и Edit по пути через junction
  `legacy/sportorg`, которую предписывает `CLAUDE.md`, стражем пропускаются; ловит ли junction
  deny-правило — не проверено;
- тесты стража: из 21 намеренной поломки ловят 13 — см. «Дополнительные проверки».

Доказательства: `verification/checks-rerun.txt` (разделы 7c, 7d), `verification/extra-checks.txt`.

### 8. Хуки Claude Code — PROVEN
- Хуки запускают только команды проекта: `guard`, `post_edit` (шаги из `check.step_command`),
  `stop_tests` (pytest из `check.py`).
- PostToolUse вживую: Write файла с ошибкой типов → `hook_probe.py:5:12 - error: Type "Literal['forty-two']"
  is not assignable to return type "int" (reportReturnType)`.
- Stop вживую: с падающим тестом в `tests/` ход заблокирован — `Tests failed (… pytest -q -x
  tests/test_stop_hook_canary.py) … 1 failed`.
- Golden: запись в `tests/golden/probe.json` → `ask`.
- Задержка PostToolUse (та же команда, 10 запусков на файл, два прогона): медиана 1,01–1,08 с (`src`),
  1,14–1,28 с (`tests`), 1,16–1,26 с (`scripts`), 0,22–0,26 с (не `.py`) — `verification/hook-latency.txt`.
  Заявлено 1,8–2,0 с — заявление с запасом.
- Независимость стража от venv: работает, но не так, как описано. При здоровом `.venv`
  `uv run --no-project --python 3.14` берёт интерпретатор из `.venv` (`sys.prefix = …\sportorg\.venv`);
  при сломанном и при отсутствующем `.venv` (копия во временном каталоге) uv переходит на
  `cpython-3.14` из своего каталога, и `deny` по-прежнему выдаётся. Импорты стража вне stdlib — только `scripts`.

### 9. Уязвимости и лицензии — PROVEN
`uv audit` → `Found no known vulnerabilities and no adverse project statuses in 19 packages`, exit 0.
`uv run python -m scripts.check_licenses` → `checked 16 packages; problems: 0`, exit 0. Обе команды есть в CI
(`ci.yml:31`, `ci.yml:33`) и проходят в логах. То же — в чистой Windows.
Слабые места проверки лицензий: сравнение по подстроке (`GPL-2.0-only` → `ok`, хотя несовместима с
GPL-3.0; `"Limited use license"` → `ok` из-за «mit»); pip-licenses не проверяет себя и свои зависимости
(pip-licenses, prettytable, wcwidth). Доказательства: `verification/checks-rerun.txt` (item 9),
`verification/extra-checks.txt`.

### 10. ADR — PARTLY PROVEN

| ADR | ≥2 альтернатив | данные и скрипт | пересмотр | воспроизведение |
|---|---|---|---|---|
| 0001 | 4 ✓ | `python_support_matrix` ✓ | ✓ | матрица совпадает; **расхождение по 3.15/macOS** (Н1) |
| 0002 | 6 ✓ | `bench_typecheckers` ✓ | ✓ | **точно** |
| 0003 | 5 ✓ | `bench_env.sh` ✓ | ✓ | порядок сред тот же, кратности меньше (Н4) |
| 0004 | в строках 1, 2, 6–8 ✓; в 9–10 один вариант | для большинства строк скриптов нет | **нет** (только строка 6) | — |
| 0005 | только решение 4 | скрипта нет | ✓ | — |

- ADR-0001: `python_support_matrix --out-dir <tmp>` → `ok: 62/62 packages`; сроки поддержки 2029-10-31 /
  2030-10-31 / 2031-10-31; у hidapi для 3.15 «-», у nuitka только классификатор. pyyaml в списке пакетов
  по умолчанию нет; отдельный прогон `--packages pyyaml` → для 3.15 «-». Независимо через резолвер uv
  (`uv pip compile --only-binary :all:`, 23 пакета × {3.14, 3.15} × {win, linux, mac}): 122/138 ок;
  провалы — pyyaml 3.15, pre-commit 3.15 (через pyyaml), hidapi 3.15, nuitka везде (только sdist), как в ADR;
  плюс orjson 3.15 на Linux (Н6). Lock-файл проекта под 3.15 на `aarch64-apple-darwin` не собирается (Н1).
- ADR-0002: повтор на клоне (1 мин 36 с): mypy 14, pyright 10, basedpyright 15, ty 8, pyrefly 12, zuban 12
  из 17; матрица ловушек совпадает с закоммиченной построчно. Время того же порядка: один файл —
  basedpyright 1,04 с, mypy 1,32 с; legacy холодный — 7,02 с и 3,17 с.
- ADR-0001 утверждает, что запуск pre-commit через `uvx` не блокируется отсутствием колёс 3.15 — п. 4 это
  опровергает для машины, где установлен 3.15.
- `pyproject.toml:6` и `README.md:36` отсылают вопрос о лицензии к ADR-0001; он в ADR-0004.
- ADR-0001 и ADR-0004 в статусе `accepted`, хотя отчёт этапа (вопросы 1 и 5) выносит их на решение мейнтейнера.

Доказательства: `verification/python-support-matrix*.md`, `wheels-only-resolution.txt`,
`typecheckers-results.md`, `env-bench.txt` (таблица — в `verification/README.md`).

### 11. risks.md и data-request.md — PARTLY PROVEN
`docs/risks.md`: у всех 15 рисков есть этап проверки и вид доказательства; темы брифа покрыты.
`docs/data-request.md`: у 12 из 13 позиций есть «зачем», «в каком виде», «чем заменить»; у п. 6 замена «—»,
хотя issues/PR только запрошены. Факты сверены: 1341 коммит legacy, `requires-python = ">=3.8.1,<=3.14"`
`[код: ../_other/pysport-legacy/pyproject.toml:6]`.

### 12. Установка по README на чистой машине — PARTLY PROVEN
Ubuntu (`ubuntu:24.04`, Docker 29.8.2):
- шаг 1 дословно → `curl: command not found` (README не называет curl, git, ca-certificates);
- шаг 3 в той же оболочке → `uv: command not found` (README не говорит открыть новый терминал);
- после установки предпосылок и `source ~/.local/bin/env`: `uv sync` exit 0, `check.py` — 5×ok, 23 passed,
  exit 0; `uvx pre-commit install` exit 0.

Windows (Windows Sandbox, `wsb` 0.8.107.0, сборка 10.0.26100.9711 при хосте 10.0.26300.9711; изначально нет
git, python, py, winget, pwsh; есть `curl.exe` и Windows PowerShell 5.1):
- шаг 1 дословно → uv 0.13.5 за 10 с;
- шаг 2 дословно в Windows PowerShell 5.1 → `The token '&&' is not a valid statement separator in this version.`;
  в cmd → `'git' is not recognized`;
- шаг 3 в том же окне → `The term 'uv' is not recognized`;
- после установки Git for Windows 2.56.0.windows.3 и нового окна: клон по README даёт `main` с одними
  `.git` и `docs`, `uv sync` там → exit 2 `No pyproject.toml found`;
- с `--branch stage-0` (HEAD `aeb0d35`): холодный `uv sync` exit 0 (CPython 3.14.9, 20 пакетов),
  `check.py` exit 0 (5×ok, 23 passed; в настоящем окне консоли тоже exit 0), `uvx pre-commit install` exit 0,
  `uv audit` и `check_licenses` exit 0; `uvx pre-commit run --all-files` exit 1 (ruff по ловушкам).

macOS не проверялся. Доказательства: `verification/clean-install-ubuntu.txt`, `clean-install-windows.txt`.

### 13. Другие среды — PARTLY PROVEN
`docs/agents/environments.md` описывает эквиваленты Codex по 7 практикам, ссылка из `AGENTS.md:60`.
`.codex/` нет, хуки Codex не настроены (TASK-3), факты о Codex — из документации, а не из запуска.
Как эквивалент Superpowers указаны правила 3–4 — они не покрывают цепочку brainstorming → план → TDD.
Конкретный агент потребовался только в шагах 7(б) и 8, которые проверяют сам слой Claude Code.

## Дополнительные проверки

| проверка | результат | вердикт |
|---|---|---|
| Тесты стража против 21 намеренной поломки (на копии; `verification/guard-mutants.txt`) | ловят 13/21; выживают: `main()` ничего не печатает; `main()` выходит с 1; падение на некорректном JSON; PowerShell убран из защищаемых инструментов; глагол только в начале строки (`echo; rm …`); удаление `Remove-Item` (ни один тест его не использует); удаление `cd`; удаление `uv sync` (оба прикрыты одним тестом) | PARTLY |
| ADR-0001 через резолвер uv | см. п. 10 | PARTLY |
| Lock-файл и цепочка поставки (`verification/supply-chain.txt`) | `uv lock --check` exit 0; 19 пакетов из реестра + проект, 129 хэшей; действия закреплены тегами (`actions/checkout@v5` → `fbc6f39…`, `setup-uv@v10.3.2` → `07a047e…`), не SHA; плавающего `v10` нет (подтверждает ADR-0004); образы devcontainer — по тегам; `clean-install` ставит последнюю uv через `curl \| sh` | PROVEN, с замечаниями |
| Секреты | gitleaks 8.30.1 по всей истории (3 коммита): `no leaks found` | PROVEN |
| Персональные данные (правило 8; `verification/extra-checks.txt`) | данных участников нет; e-mail нет; имя пользователя мейнтейнера в абсолютных путях в 28 отслеживаемых файлах (открытый вопрос 7 отчёта этапа); кейс c3 подтягивает `tests/data/sfrx_file.sfrx` из legacy при подготовке, в репозиторий не коммитится, содержимое не проверялось | PROVEN |
| Коммит `pyproject.toml` без обновления lock-файла (клон, хуки установлены; `verification/supply-chain.txt`) | `uv.lock is up to date….Failed`, `needs to be updated, but --check was provided`, коммит отклонён; `uv sync --locked` exit 1 | PROVEN |
| Devcontainer, сборка `--no-cache` (`verification/devcontainer.txt`) | uv 0.13.5, пользователь `vscode`, Ubuntu 24.04.3; `uv sync && uvx pre-commit install` ок; `check.py` exit 0; `pre-commit run` exit 1 (ruff по ловушкам) | PROVEN |
| ADR-0003, `bench_env.sh` | таблица ниже | PARTLY |

| среда | холодный `uv sync` | тёплый | pytest | ruff | basedpyright | в ADR-0003 (холодный / basedpyright) |
|---|---|---|---|---|---|---|
| Windows, NTFS (Git Bash, uv 0.13.1) | **21,58** | 0,28 | 0,67 | 0,14 | 1,09 | 37,3 / 1,39 |
| WSL, ext4 (uv 0.13.5) | 10,65 | 0,05 | 0,22 | 0,02 | 0,86 | 10,5 / 1,02 |
| WSL, /mnt/c (uv 0.13.5) | 59,44 | 0,24 | 1,78 | 0,29 | 3,18 | 75,4 / 4,29 |

## Находки для мейнтейнера (по важности)

- **Н1. Лента 3.15 на macOS зелёная только из-за сборки из исходников.** У `grimp 3.17` (зависимость
  import-linter) на PyPI для macOS есть только `cp315t`; `uv pip compile` экспорта lock-файла под
  `3.15 / aarch64-apple-darwin` с `--only-binary :all:` → `grimp==3.17 has no usable wheels`; в CI
  `macos-latest / py3.15` — `Building grimp==3.17`. Противоречит ADR-0001 («never build from source in CI»);
  критерий TASK-5 #1 проверяет только прямые зависимости и такой случай пропустит.
- **Н2. Pre-commit красный во всех средах** (п. 4): `ruff check` по `scripts/typecheck_fixtures/`; на машине
  с установленным 3.15 `uvx pre-commit` не запускается вовсе (pyyaml).
- **Н3. README дословно не работает** (п. 12): нет предпосылок (git; на Linux ещё curl и ca-certificates),
  нет «откройте новый терминал», `&&` не работает в Windows PowerShell 5.1, клонируется `main` без проекта.
- **Н4. Тесты стража не проверяют сам хук**: `main()`, отказоустойчивость (сценарий инцидента этапа 0 —
  ненулевой выход блокирует все инструменты), PowerShell, составные команды.
- **Н5. Цифры ADR-0003 и README для нативной Windows не воспроизводятся**: холодный sync 21,6 с, а не 37 с;
  ext4 быстрее нативной Windows в 2,0 раза (в ADR 3,5), на проверке типов в 1,27 (в ADR 1,4); /mnt/c медленнее
  ext4 в 5,6 раза (в ADR 7). Решение (ext4 быстрее всех) держится. Холодный прогон — по одному разу.
- **Н6. Колесо orjson для cp315 под Linux — только `manylinux_2_39`** (glibc ≥ 2.39: Ubuntu 24.04 — да,
  RHEL 9 — нет); скрипт матрицы засчитывает любой `manylinux`. Важно для ADR о минимальной ОС (этап 4).
- **Н7. Команда воспроизведения ADR-0002 перезаписывает закоммиченные доказательства**: `bench_typecheckers`
  пишет в зашитый `docs/evidence/stage-0/typecheckers/` своего репозитория `[код: scripts/bench_typecheckers.py:45]`,
  `--out` этого не меняет.
- **Н8. Закрепление по тегам, не по SHA** (действия CI, образы devcontainer), uv в `clean-install` не закреплена.
- **Н9. Проверка лицензий по подстроке** пропускает несовместимые лицензии (п. 9).
- **Н10. Нарушения правила 7**: ADR-0004 без условия пересмотра, ADR-0005 без альтернатив и скриптов;
  ссылка на вопрос о лицензии ведёт не в тот ADR.

Задачи в Backlog.md по находкам не заводились — это решение мейнтейнера.

## Расхождения с `docs/reports/stage-0.md`
1. Pre-commit подан как часть зелёного (стр. 8, 15), но прогона нет; он красный (Н2).
2. «Шаги README дословно» (стр. 17, 21): и CI, и проверочные прогоны добавляют предпосылки, правку PATH и
   `--branch`; дословно README падает (Н3).
3. «23 теста, из них 17 на страж» (стр. 20): в `tests/scripts/test_guard.py` их 18.
4. «Статус у всех „нет“, кроме истории git» (стр. 24): у п. 12 тоже «частично».
5. Deny-правило в свежей сессии числится недоказанным (стр. 53) — теперь доказано для абсолютной формы;
   относительная не проверялась.
6. `--no-project` описан как отвязка стража от venv; фактически при здоровом `.venv` используется его
   интерпретатор (п. 8).
7. Не упомянуты ложные срабатывания стража и обходы через Python и через junction `legacy/` (п. 7).
8. «Лента 3.15 зелёная на трёх ОС» — на macOS только со сборкой из исходников (Н1).
9. ADR-0003 и README: «cold `uv sync` is 37 s on NTFS vs 10 s on ext4» — сегодня 21,6 с против 10,7 с (Н5).
10. ADR-0004/0005 не отмечены как нарушающие правило 7; ADR-0001/0004 `accepted` при открытых вопросах.
11. «Чистая установка на Windows не проверена» — теперь проверена в Windows Sandbox, PARTLY (п. 12).
12. Задержка хука 1,8–2,0 с — измерено 1,0–1,3 с (заявление с запасом, не дефект).

Совпадает с отчётом: зелёный CI 7/7, вывод `check.py`, 19 пакетов в аудите, 16 в проверке лицензий,
3 контракта, 15 рисков, 13 позиций запроса, матрица Python, счёт тайпчекеров ADR-0002.
Остаток `../_deny_probe/probe.txt` на месте, как и сказано в отчёте.

## Не проверено и почему
- macOS: нет машины. Старые Windows (10 и ниже): нужна виртуальная машина; по ADR-0003 — этап 2.
- Junction `legacy/sportorg` против deny-правила и годность задач пилота (`evals/legacy-fixes`, красные до
  исправления и зелёные после) — мейнтейнер не выбрал эти проверки.
- Относительная форма deny-правила (TASK-1 #2): нужна правка `settings.local.json` и новая сессия.
- Живой `ask` при правке golden-файла (нужен ответ мейнтейнера), смоук `claude plugin eval` (платный),
  «красный путь» CI (отправка ветки во внешний сервис), Codex (нет в среде), devcontainer из VS Code,
  строки Docker в ADR-0003.

## Оговорки к самой проверке
- Ошибки, найденные при переносе доказательств и исправленные здесь: номера строк CLAUDE.md в первом устном
  отчёте считались по склеенному выводу двух файлов; счёт мутантов был 14/21 — первый пакетный прогон был
  недействителен (мутант той же длины, записанный в ту же секунду, брался из устаревшего `.pyc` предыдущего),
  повтор с `-B` даёт 13/21, а одиночные прогоны спорных мутантов это подтверждают; число файлов с путём к
  домашнему каталогу было 25 — шаблон не учитывал двойной обратный слеш, правильно 28.
- Windows Sandbox: общий лог перестал записываться после заголовка шага 6 (причина не установлена).
  Выводы шагов 6–17 скопированы из песочницы, коды выхода получены повтором тех же команд в той же
  («тёплой») песочнице. `[exit 0]` у неудачного `uv sync` в том же окне — артефакт обёртки `powershell -File`;
  по выводу шаг упал.
- Там же: `check.py`, выведенный в `NUL` из процесса, запущенного через `wsb exec`, падает в `lint-imports`
  (`rich`, `UnicodeEncodeError` в cp1251). В настоящем окне консоли и на основной машине не воспроизводится.
- Замеры — одна машина (Windows 11, 12 CPU), холодные прогоны по одному разу.
- Выводы, которые являются сообщениями самого Claude Code (отказ deny-правила, сообщения хуков PostToolUse
  и Stop), сценарием не воспроизводятся и процитированы в отчёте дословно.
