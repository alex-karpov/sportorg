# Промпт для независимой проверки этапа 1 (свежая сессия)

Скопируйте текст ниже в новую сессию, открытую в корне репозитория `sportorg`, ветка `stage-1`.
Отчёт, который проверяется, — `docs/reports/stage-1.md`.

---

Ты независимо проверяешь этап 1 «археология legacy» проекта sportorg_ng: отчёт `docs/reports/stage-1.md` и критерии задачи TASK-7 (`backlog task view 7 --plain`). Правила — `AGENTS.md`. Отчёту не верь: каждое число воспроизводи командой и сравнивай.

## Правила проверки
- **Legacy только читать.** `.legacy/` — только для чтения: не пиши туда, не разблокируй и не запускай legacy. Канарейки делай только в изменяемой копии `.legacy-run/`, её создаёт `scripts.legacy_clone`. В конце верни копию в исходное состояние той же командой с `--force`.
- **Ничего не чини.** Найденное запиши в итог.
- **Не коммить и не пушь.** В конце рабочее дерево должно быть чистым: `git status --short`, без неотслеживаемых точек монтирования песочницы.
- **Сеть не нужна,** если на машине есть кэш `~/.cache/sportorg-stage1/` (PyPI, OSV, crates.io, GitHub; `MANIFEST.json` с SHA-256).
  - Без кэша направления W3 и W4 воспроизводятся только после `uv run python -m scripts.archaeology.fetch …`. Это сетевые запросы, на них нужно согласие мейнтейнера.
  - Ключи запросов перечислены в `docs/evidence/stage-1/dependencies/commands.txt` и `defects/commands.txt`.
  - Свежие записи OSV могут отличаться от снимка 2026-10-25. Такое отличие — не ошибка этапа, но его нужно записать.
- **Песочница Claude Code.** В ней добавь `PRE_COMMIT_HOME=$TMPDIR/pre-commit` (если что-то коммитишь, но коммитить не нужно) и `UV_TOOL_DIR=$TMPDIR/uv-tools` (для `tool_runs`).
- **Итог.** На каждый пункт: PROVEN / PARTLY / NOT PROVEN, с выводом команды и кодом выхода.

## 1. Окружение
```
uv sync
uv run python -m scripts.legacy fetch
uv run python -m scripts.legacy verify          # ok: pysport@b548c35ba18f, templates@cd953823beb3 locked
uv run python scripts/check.py                  # ok format / lint / types / imports / tests
git log --oneline main..stage-1                 # коммиты этапа, последние — исправления по первой независимой проверке
```

## 2. Все числа воспроизводятся
Перезапусти каждый скрипт поверх его evidence. Если `git diff` пуст, все числа направления совпали байт в байт.
```
export PYTHONDONTWRITEBYTECODE=1
uv run python -m scripts.archaeology.hypotheses   --out docs/evidence/stage-1/hypotheses
uv run python -m scripts.archaeology.inventory    --out docs/evidence/stage-1/inventory
uv run python -m scripts.archaeology.structure    --out docs/evidence/stage-1/structure
uv run python -m scripts.archaeology.dependencies --out docs/evidence/stage-1/dependencies
uv run python -m scripts.archaeology.defects      --out docs/evidence/stage-1/defects
uv run python -m scripts.archaeology.formats      --out docs/evidence/stage-1/formats
uv run python -m scripts.archaeology.os_ru        --out docs/evidence/stage-1/os-ru
uv run python -m scripts.archaeology.tool_bench candidates --out docs/evidence/stage-1/tools
git diff --exit-code docs/evidence/stage-1      # должен быть пуст
uv run python -m scripts.legacy verify
```
`tool_runs.py` (замеры для ADR-0007) скачивает инструменты через `uvx`, поэтому ему нужен PyPI. Без сети его пропусти, а сравни только `bench.json`/`bench.md`. `timings.json` по определению недетерминирован.

Где лежит каждое число отчёта. Напечатай его командой `uv run python -c "import json; print(json.load(open('<файл>'))<ключ>)"`:

| Число в отчёте | Файл | Ключ |
|---|---|---|
| H1: 2910 строк, 218 коммитов, ранг 1 | `hypotheses/hypotheses.json` | `['H1']['numbers']` |
| H2: 78 / 62 / 16 / 77, вердикт «подтверждена» по `sportorg/` | `hypotheses/hypotheses.json` | `['H2']['numbers']`, `['H2']['verdict']` |
| H3: 12 модулей, 29 импортов; только `QtCore` 8 / 18; интерфейс 4 / 11; пакет `sportorg.gui` 3 / 3 | `hypotheses/hypotheses.json` | `['H3']['numbers']` |
| H4: 7 / 7 / 7 / 3 | `hypotheses/hypotheses.json` | `['H4']['numbers']` |
| H5: домен, 10 членов, 2 определения | `hypotheses/hypotheses.json` | `['H5']['numbers']` |
| H6: маркеры, версии в lock, 60 файлов PySide2 | `hypotheses/hypotheses.json` | `['H6']['numbers']` |
| Меню: 102 узла, 82 действия, 2 класса без пункта | `inventory/menu.json` | `['counts']` |
| Шаблоны 62 + 8 | `inventory/templates.json` | `['templates_repo']`, `['pysport']` (длины списков) |
| 220 файлов, 2333 функции, 33 086 SLOC, ρ 0,64, топ-10 | `structure/summary.json` | `['hotspots']` |
| Рёбра 603 / 588 / 15 | `structure/summary.json` | `['imports']` |
| V1 3 + 1 локальный, V3 3; import-linter 4 пары | `structure/summary.json` | `['violations']['counts']`, `['violations']['linter']` |
| 282 находки vulture, 109 с `name_in_string` | `structure/summary.json` | `['dead_code']` |
| Пакеты, лицензии, OSV 227, перекрёстные проверки | `dependencies/summary.json` | весь объект; `['crosscheck']` |
| 1142 / 176 / 168 | `defects/counts.json` | `['counts']` |
| Классы: ui 37, other 44, device 16, calc 15, import-export 15, …; правило: путь 62, ключевое слово 58, функции `memory.py` 4, остаток 44 | `defects/counts.json` | `['counts']['class_totals_product']`, `['counts']['class_decided_by_rule_product']` |
| 124 функции, 184 вызова, 291 значение; строка `sportorg.modules.backup.sfr_results_board.dump` с `delimiter="\t"` | `formats/formats.json` | `['summary']`, `['rows']` |
| 923 находки, по правилам | `os-ru/summary.json` | `['counts']` |
| Полнота против `git grep` | `os-ru/recall.json` | весь объект |
| ADR-0007: функции и ρ, рёбра, vulture, история, `sys.platform` | `tools/bench.json` | `['N1']`, `['N2']`, `['N3']`, `['N6']`, `['N8']`. N4 и N5 (OSV) — в `dependencies/crosscheck.json`; у N7 (issues через `gh api`) замера нет, только проверка лимита в ADR-0007 |

## 3. Теги `file:line`
```
uv run python -m scripts.archaeology.verify_locs --evidence docs/evidence/stage-1 --sample 15 --seed <своё число>
```
Ожидается `tags: 2902; problems: 0`. Возьми своё значение seed и сверь 15 напечатанных строк с тем, что утверждает соответствующая строка evidence: тот ли это класс, импорт, вызов, значение.

## 4. Выборочные проверки и классификация агента: перепроверь часть независимо
Файлы `*.agent.md` — суждения агента основной сессии, человек их не проверял. Две независимые проверки агентом прошли 2026-10-25 (раздел «Независимые проверки» отчёта); их поправки помечены в файлах датой. Проверь заново, не опираясь на них.
- **`defects/sample-check-2.agent.md`** (классификатор после решения В5).
  - Выбери 10 строк, например через одну.
  - Прочитай `git -C .legacy/pysport show <sha>` и поставь свою метку «исправление/нет» и класс по критериям из начала файла.
  - Посчитай совпадение с метками файла.
  - Проверь арифметику раздела «Result»:
    - точность 23/25;
    - оценка полноты ≈ 46 % по долям 176/966 и интервал 23–76 % из двух интервалов Клоппера — Пирсона по 97,5 % (23/25 и 5/25);
    - объединение с первой выборкой без повторов: 45/47 и 7/50, ≈ 56 % (35–78 %);
    - совпадение классов 8/23.
  - Проверь, что столбцы «predicted» совпадают с текущим `defects/commits.json`.
- **`defects/sample-check-1.agent.md`** — первая выборка, против прежнего классификатора. Её столбцы «predicted» устарели, так и должно быть. Проверь только арифметику: 24/25, ≈ 69 % и интервал 33–96 % с учётом точности.
- **`structure/dead-code-sample-check.agent.md`.**
  - Выбери 10 строк.
  - Проверь метки через `git -C .legacy/pysport grep -n -w <имя>` и `git -C .legacy/templates grep -n -w <имя>`, а для FP-convention — через вызовы `getattr` в `sportorg/gui/dialogs/dialog.py`.
  - Проверь раздел о `WdbOnlineSenderDialog`: `git -C .legacy/pysport grep -n -w WdbOnlineSenderDialog b548c35` и `git -C .legacy/pysport log --oneline -S"WdbOnlineSenderDialog" b548c35`.
- **`os-ru/classification.agent.md`.** Это классификация всех находок, а не выборка.
  - Проверь покрытие: число находок по ОС (OS01–OS05) плюс находки с `core: true` в `os-ru/hits.json` должно равняться 686, и каждый тег должен стоять ровно в одной группе.
  - Проверь по коду категории групп O5, O8, O11 и O19 и находку 6 (O8, расхождение Р8).
- **`dependencies/licence-sources.agent.md`.**
  - Строки с пометкой «re-verified» сверь с кэшем: `pypi/sportident==1.2.8.json` (`info.license`, классификаторы, `urls[].digests.sha256`), `crates/unicode-ident==1.0.24.json`, а также с `git -C .legacy/pysport show b548c35:Cargo.lock`.
  - Строки «review session» без сети не проверить, их нужно перечислить как непроверенные. Если загрузки сессии разбора ещё лежат в `/tmp/claude-1000/si` и `/tmp/claude-1000/u`, сверь их хеши с файлом и проверь по ним, что сможешь.
- **Воспроизводимость выборок.** Они воспроизводятся командами, записанными в начале каждого файла выборочной проверки (`scripts.archaeology.sample`). Запусти их и сравни, что список совпадает.

## 5. Канарейки: скрипты реагируют на изменение данных
Скрипты читают legacy как `<закреплённый коммит>:<путь>`. Переменная `ARCHAEOLOGY_LEGACY_BASE=.legacy-run` направляет их на изменяемую копию, а `git replace` подменяет в этой копии закреплённый коммит. Каждую канарейку начинай со свежих копий:
```
uv run python -m scripts.legacy_clone --force
uv run python -m scripts.legacy_clone --name templates --force
R=.legacy-run/pysport; PIN=$(git -C $R rev-parse HEAD)
export ARCHAEOLOGY_LEGACY_BASE=.legacy-run PYTHONDONTWRITEBYTECODE=1
```

1. **H1: memory.py +1 строка.**
   ```
   echo "# canary" >> $R/sportorg/models/memory.py && git -C $R add -A
   git -C $R replace $PIN $(git -C $R commit-tree $(git -C $R write-tree) -p $PIN^ -m canary)
   uv run python -m scripts.archaeology.hypotheses --out $TMPDIR/canary-h1
   ```
   Ожидается: `['H1']['numbers']` даёт `lines` 2911 и `commits` 219, вердикт `partly`.
2. **Дефекты: исправление переписано в `docs:`.**
   ```
   F=$(git -C $R rev-parse 2988024)
   git -C $R replace $F $(git -C $R commit-tree $F^{tree} -p $F^ -m "docs: canary")
   uv run python -m scripts.archaeology.defects --out $TMPDIR/canary-def
   ```
   Ожидается: `['counts']['fix_commits']` 175 (было 176), `product_defects` 167.
3. **Меню: убран пункт File > Save** (строки 77–82 `menu.py`).
   ```
   sed -i '77,82d' $R/sportorg/gui/menu/menu.py && git -C $R add -A
   git -C $R replace $PIN $(git -C $R commit-tree $(git -C $R write-tree) -p $PIN^ -m canary)
   uv run python -m scripts.archaeology.inventory --out $TMPDIR/canary-menu
   ```
   Ожидается: `['counts']['actions']` 81, `unused_classes` 3.
4. **Тег `file:line`.**
   - Скопируй `docs/evidence/stage-1/hypotheses` в `$TMPDIR/canary-tags`.
   - В копии `hypotheses.md` замени `memory.py:1-2910` на `memory.py:1-2999`.
   - Запусти `verify_locs --evidence $TMPDIR/canary-tags`.
   - Ожидается одна проблема `line 2999 out of range` и код выхода 1.
5. **Форматы и ОС/РФ: в memory.py добавлены ветка `sys.platform` и запись в cp1251.**
   ```
   printf '\n\nif sys.platform == "win32":  # canary\n    open("canary.csv", "w", encoding="cp1251").close()\n' >> $R/sportorg/models/memory.py && git -C $R add -A
   git -C $R replace $PIN $(git -C $R commit-tree $(git -C $R write-tree) -p $PIN^ -m canary)
   uv run python -m scripts.archaeology.formats --out $TMPDIR/canary-fmt
   uv run python -m scripts.archaeology.os_ru --out $TMPDIR/canary-osru
   ```
   Ожидается: `formats.json` `['summary']` — `functions` 125, `io_calls` 185, `values` 294 (было 124 / 184 / 291); `os-ru/summary.json` `['counts']` — `OS01.core.code` 0 → 1, `RU04.core.string` 1 → 2, остальное без изменений.

После канареек:
```
uv run python -m scripts.legacy_clone --force && uv run python -m scripts.legacy_clone --name templates --force
unset ARCHAEOLOGY_LEGACY_BASE
uv run python -m scripts.legacy verify
```

## 6. Личные данные (правило 8)
```
grep -rnE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}' docs/evidence/stage-1 docs/reports/stage-1.md | grep -v 'pysport@\|templates@'
grep -rnoE '\b[А-ЯЁ][а-яё]{2,}\b' docs/evidence/stage-1 | sort | uniq -c | sort -rn | head -30
grep -rnoE '[А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+|«[А-ЯЁ][а-яё]+»' docs/reports docs/*.md docs/evidence/stage-1
```
- Первая команда должна быть пустой.
- Во второй не должно быть имён людей.
- Третья ищет пары слов с заглавной буквы и одиночные слова в кавычках в документах для мейнтейнера. Названия разделов в кавычках допустимы, имён людей быть не должно.
- Проверь, что в `defects/` нет тем коммитов и заголовков issues и PR, а в evidence нигде нет авторов коммитов.

## 7. Итог
- Напиши итог по пунктам 1–6 и по каждому из шести критериев TASK-7 с вердиктом.
- Отдельно перечисли расхождения с отчётом.
- Отметь, верно ли отчёт описывает, что не доказано.
- Итог передай мейнтейнеру. Файлы в репозиторий не пиши.
