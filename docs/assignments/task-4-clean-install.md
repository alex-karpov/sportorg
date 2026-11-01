# Задание: установка по README на чистой Windows и чистом macOS (Backlog TASK-4)

Кому: двум добровольцам, одному с Windows 11, другому с macOS. Можно и одному, если есть оба.
Время: около 30 минут на одну ОС, большая часть уходит на загрузки.

## Зачем
README обещает, что проект ставится с нуля несколькими командами. На Linux это проверяет CI в
чистом контейнере Ubuntu (`docs/evidence/stage-0/clean-install-ubuntu.txt`). Машины CI для Windows
и macOS не чистые: на них уже стоят git, curl и Python. Поэтому нужен один честный прогон на
машине, где ничего этого нет. Каждый шаг, которого нет в README, — находка, её допишем в README.

Выполняйте шаги README буквально, в том порядке, в каком они там написаны (версия README на ветке
`main`, https://github.com/alex-karpov/sportorg). Если шаг не сработал, не ищите обход сразу.
Сначала запишите, что произошло, потом то, что помогло.

## Windows 11

### Какая машина подходит
На машине не должно быть `uv`, Python, Git и клона проекта. Подходящие варианты:
- новая виртуальная машина с Windows 11 (Hyper-V, VirtualBox, VMware Workstation, Parallels и т. п.);
- «Песочница Windows» (Windows Sandbox) в Windows 11 Pro/Enterprise: она каждый раз запускается
  чистой, но после закрытия всё стирается, поэтому журнал скопируйте из неё до закрытия;
- только что переустановленный компьютер.

Новая учётная запись на обычном компьютере не годится: Python и Git ставятся на всю систему.

### Шаги
1. Откройте PowerShell и включите запись сеанса:
   ```
   Start-Transcript -Path $HOME\Desktop\clean-install-windows.txt
   ```
2. Запишите, что за машина и что на ней уже есть. Ошибки «не найдено» здесь ожидаемы и нужны:
   ```
   Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture
   $PSVersionTable.PSVersion
   uv --version; python --version; py --version; git --version
   ```
3. Установите Git for Windows по ссылке из README с настройками по умолчанию. В журнал отметьте:
   `"== installed Git for Windows <версия> with defaults"`.
4. `Stop-Transcript`. Закройте PowerShell, откройте новое окно и продолжите запись в тот же файл:
   ```
   Start-Transcript -Path $HOME\Desktop\clean-install-windows.txt -Append
   ```
5. Выполните команды раздела «Windows (PowerShell)» из README. Когда README велит закрыть окно,
   повторите шаг 4.
6. В конце выполните `git log -1 --format=%H` (в папке `sportorg`, куда привёл README) и `Stop-Transcript`.

## macOS

### Какая машина подходит
На машине не должно быть `uv`, Python, Xcode Command Line Tools, Homebrew и клона проекта.
Подходящие варианты:
- новая виртуальная машина с macOS (UTM, Parallels, VMware Fusion и т. п.);
- только что переустановленный компьютер.

Новая учётная запись на обычном компьютере не годится: инструменты Xcode и Homebrew ставятся на
всю систему.

В журнал попадёт архитектура (`uname -m`). Нам полезны обе, Apple Silicon (`arm64`) и Intel
(`x86_64`): CI проверяет только `arm64` (ADR-0004, строка 8).

### Шаги
1. Откройте «Терминал» и включите запись сеанса:
   ```
   script ~/Desktop/clean-install-macos.txt
   ```
2. Запишите, что за машина и что на ней уже есть:
   ```
   sw_vers; uname -m
   command -v uv python3 git curl
   xcode-select -p
   ```
   Не запускайте здесь `git` или `python3` без `command -v`: на чистом macOS это заглушки, которые
   сами предлагают установить инструменты Xcode, и порядок шагов README нарушится.
3. Выполните пункт macOS раздела Prerequisites (`xcode-select --install`) и дождитесь конца
   установки в открывшемся окне.
4. Выполните команды раздела «Linux and macOS» из README.
5. В конце выполните `git log -1 --format=%H` (в папке `sportorg`, куда привёл README), затем `exit` (запись остановится).

## Что прислать мейнтейнеру
- Файл журнала: `clean-install-windows.txt` или `clean-install-macos.txt`.
- Коротко по-русски, в письме: какие шаги не сработали с первого раза, что вы сделали сверх README и
  сколько примерно заняла установка.

Перед отправкой просмотрите журнал. В заголовке `Start-Transcript` есть имя пользователя и
компьютера, а в путях — имя учётной записи. Их можно заменить на `USER` и `HOST`, остальное не
меняйте. Последняя строка `uv run python scripts/check.py` должна показать итог проверок. Если
проверки упали, журнал всё равно нужен: это и есть результат.
