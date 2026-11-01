# Задание: хуки Codex для проекта (Backlog TASK-3)

Кому: пользователю OpenAI Codex CLI (любая ОС; нативная Windows особенно полезна).
Время: около 30 минут на часть A и 15 минут на часть B. Части выполняются в разные дни: между ними
мы настраиваем хук по присланным данным.

## Зачем
В Claude Code после каждой правки Python-файла запускается хук. Он проверяет файл тремя шагами
`scripts/check.py`: формат, линтер и типы (`scripts/hooks/post_edit.py`). Агент видит ошибки сразу,
а не в конце работы. В Codex тоже есть хуки (`.codex/hooks.json`, событие `PostToolUse`), но Codex
правит файлы инструментом `apply_patch`. По документации Codex текст правки приходит в хук в поле
`tool_input.command`. Есть ли там пути файлов и в каком виде, документация не говорит
(learn.chatgpt.com/docs/hooks, проверено 2026-11-01). Поэтому сначала нужен настоящий пример того,
что Codex передаёт хуку.

## Часть A. Записать, что Codex передаёт хуку

1. Установите среду проекта по `README.md` (разделы Prerequisites и Install) и убедитесь, что
   `uv run python scripts/check.py` проходит.
2. Запишите версии: `codex --version`, ОС и её версию.
3. В корне клона создайте папку `.codex` и в ней два файла. В git их не добавляйте.

   `.codex/probe_hook.py`:
   ```python
   import json
   import sys
   from pathlib import Path

   raw = sys.stdin.read()
   try:
       line = json.dumps(json.loads(raw), ensure_ascii=False)
   except ValueError:
       line = json.dumps({"unparsed": raw}, ensure_ascii=False)
   with Path(__file__).with_name("hook-payloads.jsonl").open("a", encoding="utf-8") as out:
       out.write(line + "\n")
   ```

   `.codex/hooks.json`:
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {"matcher": "apply_patch", "hooks": [{"type": "command", "command": "uv run --no-project --python 3.14 python .codex/probe_hook.py", "timeout": 30}]}
       ],
       "PostToolUse": [
         {"matcher": "apply_patch", "hooks": [{"type": "command", "command": "uv run --no-project --python 3.14 python .codex/probe_hook.py", "timeout": 30}]}
       ],
       "Stop": [
         {"hooks": [{"type": "command", "command": "uv run --no-project --python 3.14 python .codex/probe_hook.py", "timeout": 30}]}
       ]
     }
   }
   ```
   Хук только дописывает полученный JSON в `.codex/hook-payloads.jsonl` и ничего не блокирует.
4. Запустите `codex` из корня клона. Codex спросит, доверять ли проекту: доверьте. Затем откройте
   `/hooks` и одобрите три хука. Без этого шага локальные хуки не запускаются.
5. Попросите Codex дословно:
   > Create the file `scripts/_probe.py` with the line `x = 1`. Then change it to `x = 2`.
   > Then rename it to `scripts/_probe2.py`. Then delete it. Use apply_patch for every step.

   Так в журнал попадут все виды правок: создание, изменение, переименование и удаление.
6. Выйдите из Codex и проверьте, что `.codex/hook-payloads.jsonl` не пуст и в нём есть строки с
   `"hook_event_name": "PostToolUse"`.
7. **Если файла нет или в нём нет `PostToolUse`, хук не сработал. Почините его**, сами или с
   помощью Codex, и повторите шаги 4–6. Что обычно мешает: другой формат `hooks.json` в вашей
   версии Codex, другое имя в `matcher`, команда, которую оболочка Windows понимает иначе (для
   Windows есть поле `commandWindows`). Справка: `/hooks` в Codex и
   https://learn.chatgpt.com/docs/hooks.
8. Если вы на Windows, запишите, какой оболочкой Codex запускал команду (cmd или PowerShell),
   если это видно в `/hooks` или на экране.

**Что прислать мейнтейнеру:** файл `.codex/hook-payloads.jsonl`, версию Codex и ОС. Если пришлось
чинить, приложите итоговые `.codex/hooks.json` и `.codex/probe_hook.py` и одну строку о том, что
было не так. Перед отправкой просмотрите файл журнала: в поле `transcript_path` и в путях может
быть имя вашей учётной записи. Его можно заменить на `USER`, остальное не меняйте. Потом удалите
`.codex/`, чтобы она не мешала части B.

## Часть B. Проверить готовый хук

Выполняется после того, как в репозитории появится `.codex/hooks.json` (мейнтейнер сообщит ветку).

1. `git pull`, затем `uv sync`.
2. Запустите `codex` из корня клона и одобрите новые хуки в `/hooks`.
3. Попросите Codex:
   > Add the line `import os` right after the last import line of `scripts/check.py` using
   > apply_patch, show me the hook output, then revert the change.
4. Ожидается, что после правки хук сообщит ошибку линтера, среди прочего `F401` (неиспользуемый
   импорт), и Codex увидит её как сообщение хука. После отката ошибок нет.
5. Скопируйте с экрана Codex весь текст от вашей просьбы до отката включительно.
6. В конце `git status` должен быть чистым. Если нет, выполните `git checkout -- scripts/check.py`.

**Если хук не сработал или сработал не так, почините его** и пришлите исправление: pull request в
https://github.com/alex-karpov/sportorg или файл `git diff` (`git diff > codex-hooks.diff`).
Исправление можно поручить Codex: он читает `AGENTS.md` проекта сам. Условия:
- общая логика хука живёт в `scripts/hooks/` и работает для обоих агентов. В `.codex/hooks.json`
  только вызов. Ни одного правила, которого нет в `AGENTS.md`, в хуке быть не должно;
- `uv run python scripts/check.py` проходит. Его вывод приложите к PR или к письму;
- в исправленном хуке шаги 3–6 этой части проходят. Текст с экрана Codex приложите;
- код, комментарии и сообщение коммита на английском, коммит в стиле Conventional Commits
  (`fix(hooks): …`).

**Что прислать мейнтейнеру:** скопированный текст, версию Codex и ОС, а если пришлось чинить, то
ссылку на PR или файл `codex-hooks.diff`.
