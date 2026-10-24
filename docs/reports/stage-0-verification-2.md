# Независимая проверка этапа 0, второй раунд: итог

Дата: 2026-10-25. Отдельная сессия Claude Code в WSL2 по `docs/reports/stage-0-verification-prompt.md`; текст ниже — её итог, переданный мейнтейнером. Изменения: имя пользователя в одной цитате заменено на `USER` (`docs/evidence/stage-0/README.md`), у таблиц убраны выравнивающие пробелы. Сырые выводы этой сессии в репозиторий не сохранялись, её временные каталоги удалены. Что сделано по расхождениям — `docs/reports/stage-0.md`, раздел «Повторная проверка (второй раунд)».

**Общий вердикт: PARTLY PROVEN.** Исправления по находкам первой проверки (Н1–Н10) подтверждены моими прогонами. Окружение работает: проверки зелёные, канарейки ловятся, legacy защищён, CI и README в Ubuntu работают. Нашлись четыре новых расхождения (раздел ниже). Остаются непроверенными чистая установка на Windows и macOS (TASK-4) и хуки Codex (TASK-3).

Среда: WSL2 Ubuntu на ext4, HEAD `9935b2c` (ветка `stage-0`), uv 0.13.5. Команды `uv` упирались в песочницу (`~/.cache/uv`: Read-only file system), поэтому они запускались вне её. Рабочее дерево в конце проверки чистое (`tracked-changes: 0`), клоны legacy тоже. Неотслеживаемые файлы вроде `.bashrc` в `git status` видны только внутри песочницы: это её точки монтирования.

## По пунктам

**1. AGENTS.md / CLAUDE.md — PROVEN.** Первая строка `CLAUDE.md` — `@AGENTS.md`. Дословных повторов правил нет, есть три частичных пересечения:
- «WSL2 для агентной работы на Windows» есть в разделе Environment файла AGENTS.md и в последнем пункте CLAUDE.md;
- «планы привязаны к задаче» есть в правиле 6 и в пункте про Superpowers;
- описание хуков в CLAUDE.md пересказывает правила 1 и 5 как механизм.

Ещё одно мелкое расхождение: CLAUDE.md предлагает ставить `code-modernization@claude-plugins-official`, а локальный `settings.local.json` включает `code-modernization@anthropic-plugin-directory`.

**2. check.py — PROVEN.** `uv sync` → exit 0. `check.py --keep-going` → `ok format / lint / types / imports / tests`, `Contracts: 3 kept, 0 broken`, `99 passed`, exit 0.

**3. Канарейки — PROVEN.** Делал на клоне в скретчпаде, после каждой откат, `git status` пуст. Все четыре дали exit 1:

| Канарейка | Что поймало |
| --- | --- |
| (а) `import os` в `core/` | lint-imports: `sportorg_ng.core is not allowed to import os`, а также ruff PTH109 |
| (б) функция без аннотаций | ruff ANN201/ANN001 и basedpyright, 6 ошибок |
| (в) `# type: ignore` без кода | ruff PGH003 и basedpyright `reportIgnoreCommentWithoutRule` |
| (г) сломанный тест | `1 failed, 99 passed` |

**4. Pre-commit — PROVEN, с оговоркой.**
- Оба прогона (`--all-files` и `--hook-stage pre-push`): все хуки `Passed`, exit 0.
- Отличия от `check.py`:
  - basedpyright проверяет только изменённые файлы;
  - lint-imports запускается только при изменении `src/` или `pyproject.toml`;
  - добавлен `uv lock --check`;
  - тесты идут только на push.
- Голый `uvx pre-commit --version` вывел `pre-commit 4.7.0`, exit 0. Он взял `/usr/bin/python3` (3.14), потому что 3.15 не установлен.
- Для сравнения запустил `uvx --python 3.15 pre-commit`: на Linux pyyaml **собрался из исходников**, и команда завершилась успешно. Значит, утверждение ADR-0001/0004 «голый uvx падает» верно только там, где нет компилятора (Windows без MSVC). Скачанный при этом CPython 3.15.1 я удалил.

**5. CI — PROVEN.**
- Матрица {ubuntu, windows, macos} × {3.14, 3.15}; 3.14 — нижняя граница из `requires-python`.
- Лента 3.15 не блокирует merge (`continue-on-error`).
- Синхронизация идёт с `--no-build`.
- SHA действий сверил через `gh api`: checkout v5.0.1 → `93cb6ef…`, setup-uv v10.3.2 → `07a047e…`.
- `clean-install` идёт по шагам README в том же порядке.
- Прогон 40120556412 для HEAD 9935b2c: итог `success`, 6 джобов зелёные. `macos-latest / py3.15` упал на `grimp==3.17 … marked as --no-build but has no binary distribution` — так и задумано.
- Мелочь: `uv sync` в `clean-install` идёт без `--no-build`, дословно как в README.

**6. Backlog.md — PARTLY PROVEN.**
- В WSL CLI не запускается (`node: not found`). Пришлось вызывать Windows-версию 1.54.0 через `cmd.exe` + `pushd`.
- Задач In Progress нет. В m-0 «1/5 done»; в To Do остаются TASK-3, 4, 5, 6.
- Критерии TASK-3, 4, 5 проверяемы. У TASK-6 критерии #1 и #4 («updated», «recorded in the docs named in the notes») проверяемы слабо.
- В описании TASK-1 устаревшее «Open: verify in WSL2…» при статусе Done; имя файла задачи — со старым заголовком.
- Второго реестра нет: чекбоксов вне `backlog/` нет, кроме двух строк в `docs/evidence`.

**7. Legacy только для чтения — PROVEN по всем проверкам (а)–(е).** Про `unlock` — ниже, в расхождениях.
- **(а)** Путь к legacy задаёт только `scripts/legacy.py` (`LEGACY_DIRNAME`, `checkout_dir`). `git grep` находит только маркер в `_common.py:28` и тесты.
- **(б)** `verify` → `ok: pysport@b548c35ba18f, templates@cd953823beb3 locked`, exit 0. HEAD обоих клонов совпадает с `legacy.toml`.
  - Анонимно, без учётных данных: оба репозитория `private= False`, закреплённые коммиты скачиваются через `fetch --depth 1`.
  - В обоих репозиториях пин совпадает с `master` (`identical`).
  - `test_legacy.py`: 7 passed.
- **(в)** Абсолютных путей в `settings.json` нет. Edit по `.legacy/pysport/README.md` дал точный отказ: `File is in a directory that is denied by your permission settings.` Файл не изменился.
- **(г)** Страж (JSON подавал из файлов): все пять ожидаемых `deny` получены, четыре команды чтения дали пустой вывод. Edit через `src/../.legacy/…` → `deny`. Некорректный JSON → пустой вывод, rc=0.
- **(д)** Файловый слой:

| Попытки | WSL2 ext4 (и tmpfs) | Windows, только атрибут read-only | Windows + deny ACE |
| --- | --- | --- | --- |
| Заблокировано | 9 из 10 | 5 из 14 | 14 из 14 |
| Прошло | `chmod u+w` + дозапись | `sed -i`, `cp`, `mv`, `rm`, `rm -rf`, `git rm`, `chmod`, `Remove-Item -Force`, `-Recurse` | — |

  Числа совпадают с ADR-0006. Временные каталоги в `~` и `%TEMP%` удалены.
- **(е)** `legacy_clone --dest` создал клон на `b548c35…`, запись в него работает, `--force` пересоздаёт его (тестовый файл исчез). Мелочь: без `--force` скрипт сообщает «already at» даже при грязной копии.

**8. Хуки — PROVEN, с оговоркой.**
- Все три хука запускают только модули проекта.
- `main()` стража ловит любое исключение: если в данных упомянут legacy, отвечает `ask`, иначе молчит; Python-часть всегда завершается с кодом 0.
- После Write файла с ошибкой типов в `src/` PostToolUse сообщил: `error: Type "Literal['not an int']" is not assignable to declared type "int" (reportAssignmentType)`. Файл удалён.
- Оговорка про отказ самого `uv` — в расхождениях ниже.

**9. Мутации стража — PROVEN, 6 из 6 убиты.** Повторил с очисткой `__pycache__` и `-B`, учитывая ловушку с `.pyc` из прошлой проверки. Число упавших тестов:

| Мутация | Упало тестов |
| --- | --- |
| `main()` возвращает 1 | 7 |
| `main()` ничего не печатает | 2 |
| из `SHELL_TOOLS` убран `PowerShell` | 6 |
| `_cd` не меняет `in_legacy` | 3 |
| `_split` не делит по `;` | 3 |
| `is_legacy_path` без `resolve` | 1 |

**10. Уязвимости и лицензии — PROVEN.**
- `uv audit`: `no known vulnerabilities … in 16 packages`, exit 0.
- `check_licenses`: exit 0, 0 runtime пакетов.
- `test_check_licenses.py`: 17 passed.
- `GPL-2.0-only` → `denied`; `Limited use license` → `unknown`, а для runtime это ошибка.
- Обе команды есть в CI (`ci.yml:33,35`).
- `git hash-object LICENSE` = `f288702d…`, совпадает с gnu.org; `cmp` → identical. pyproject, README и ADR-0004 согласованы.
- Устарело: docstring `check_licenses.py` всё ещё называет лицензию «GPL-3.0-or-later (provisional)».

**11. ADR — PARTLY PROVEN.**
- По форме все шесть ADR в порядке: альтернативы (или объяснение, почему одна), данные со скриптами, условие пересмотра, статус.
- `bench_typecheckers --tools ty` дал `results.json`, `results.md`, `fixtures-ty.txt`, `legacy-ty.txt` во временном каталоге. ty ловит 8 из 17, как в ADR-0002. `git status docs/evidence` пуст, клон legacy чистый.
- Но в ADR есть фактические ошибки — см. расхождения 1 и 2.

**12. risks.md и data-request.md — PROVEN.**
- У всех 16 рисков есть этап проверки и вид доказательства.
- У всех 13 позиций запроса есть «зачем», «в каком виде» и «чем заменить». Правило о персональных данных записано.
- Скан на e-mail и телефоны в отслеживаемых файлах ничего не нашёл.
- Устарело: пункт 13 и R8 (подробно — расхождение 4).

**13. README в `ubuntu:24.04` — PROVEN.** Пользователь WSL не в группе `docker`, поэтому запускал через Docker Desktop (`docker.exe`, 29.8.2).
- Отклонения от README: (1) сначала поставил `sudo`, как в CI; (2) после клона переключился на `stage-0` (`main` = 731ad12, `stage-0` = 9935b2c).
- Результат: uv 0.13.5, `uv sync` сам скачал CPython 3.14.9, `check.py` — 5 шагов ok, 99 passed.

**14. Решения мейнтейнера — PARTLY PROVEN.**
- Применено:
  - `enabledPlugins` = только superpowers;
  - раздел «Decision rule (draft…)» помечен «until then it is not in force»;
  - место хранения корпуса записано в общем виде: «вне репозитория, в приватном хранилище мейнтейнера»;
  - ADR-0001 confirmed; ADR-0006 описывает два репозитория; GPL-3.0-only.
- Проверочный `git grep` находит только `USER`, `WDAGUtilityAccount` и `x`. Комментарий о замене есть в `docs/evidence/stage-0/README.md:7`.
- Почему PARTLY: в `docs/data-request.md`, пункт 13, по-прежнему «решено с оговоркой: GPL-3.0-or-later». Имя пользователя осталось в двух местах `docs/evidence` не в виде пути: `probe-fsmode-windows.md:22` («deny ACE for USER») и регулярное выражение в `verification/scripts/extra_capture.sh:19`.

**15. Другие среды — PROVEN.** `docs/agents/environments.md` даёт эквиваленты для Codex. Конкретного агента потребовали только 7(в) и 8: они по определению проверяют слой Claude Code. Остальное — обычные команды. Отдельно: CLI Backlog.md не работает в WSL2 без node, хотя это рекомендуемая среда.

## Расхождения с `docs/reports/stage-0.md` и ADR

1. **Лицензия legacy.** Отчёт (стр. 99) и ADR-0004 утверждают, что «or any later version» есть только в `huichang.py`. На деле её содержат ещё `sportorg/libs/sfr/sfrreader.py`, `sportiduino/sportiduino.py` и `srpid/srpid.py`. Кроме того, в окне «О программе» показан полный текст GPL, и образец уведомления из раздела «How to Apply» там заполнен как «SportOrg, Copyright (C) 2018 SportOrg team … either version 3 … or (at your option) any later version» `[код: .legacy/pysport/sportorg/gui/dialogs/about.py:720-726]`. Это касается решения о лицензии и TASK-10. По правилу 9 это решает мейнтейнер; я ничего не исправлял.
2. **`unlock` проходит мимо стража.** Правило 1 говорит «Never unlock», но `uv run python -m scripts.legacy unlock` страж пропускает (пустой вывод). Отчёт (стр. 138) и строка «Owner restoring write access» в таблице ADR-0006 упоминают только `chmod`/`attrib`/`icacls`.
3. **Страж может закрыться наглухо.** ADR-0003/0005/0006 и отчёт говорят, что хук «всегда завершается с кодом 0». Это верно только для Python-части. Когда не работает сам `uv` (кеш только для чтения), команда хука завершилась с кодом **2**. По документации Claude Code код 2 в PreToolUse блокирует инструмент; вживую это не воспроизводилось, поэтому `[допущение]`. Это тот же сценарий отказа «закрыто», что и инцидент этапа 0.
4. **Мелкие устаревшие места:**
   - пункт 13 data-request и docstring `check_licenses.py` — про GPL-3.0-or-later;
   - R8 ссылается на `pysport@30d849d`;
   - в ADR-0006 осталось «(open, below)» по уже решённому вопросу;
   - отчёт (стр. 225) пишет, что для песочницы в WSL не хватает `socat`, а в этой сессии песочница работала;
   - TASK-1, расхождение с Backlog — см. п. 6.

С первой проверкой (`stage-0-verification.md`) всё сходится: Н1–Н4 и Н7–Н9 сам перепроверил и подтвердил. Н5 и Н6 видел только записанными в ADR, замеры не повторял. По Н10 структура ADR теперь в порядке.

## Что не проверено
- **macOS** и **чистая Windows по README** (TASK-4): машины macOS нет, Windows Sandbox я не запускал.
- **Агентная проба** `probe_legacy_protection.py agent` (платная, `claude -p`): не повторял. Живьём проверил только прямой путь Edit.
- **`ask` для golden-файлов**: их пока нет. **Stop-хук** живьём не наблюдал.
- **Codex** (нет в среде), **devcontainer** (не собирал), **красный путь CI** (ничего не отправлял).
- **Замеры ADR-0003 и матрица ADR-0001** не перезапускались, ADR-0002 перезапущен только для ty.
- **`docs/evidence`** по существу не читал. Видел только попутные строки из моих `grep`.

Побочные эффекты откатаны. Есть одна оговорка: однажды я случайно сделал `cd` в `.legacy/pysport` (только чтение, рабочий каталог вернул). Записей в legacy нет, `verify` ok.
