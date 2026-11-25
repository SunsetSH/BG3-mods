# Моды для Baldur’s Gate 3

Сборник модов для диалогов, передвижения и боя. Можно установить любой мод отдельно. Инструкция рассчитана на Windows.

[Скачать моды на GitHub](https://github.com/SunsetSH/BG3-mods/releases) · [Инструкция по установке](docs/INSTALL.md)

## Моды

| Мод | Что делает | Script Extender | Проверка в игре |
|---|---|---|---|
| [DC Check](mods/dc_check/README.md) | Показывает сложность проверки до выбора ответа в диалоге. Например, `[УБЕЖДЕНИЕ] (КС 15)`. | Не нужен | Пройдена |
| [Run Speed](mods/run_speed/README.md) | Меняет скорость бега отряда вне боя и пошагового режима. В сворачиваемом окне можно выбрать от 0,5× до 10×. | API 33+ | Пройдена до уточнения требования к Script Extender |
| [Combat Turn Timer](mods/combat_turn_timer/README.md) | Отсчитывает от 5 до 300 секунд на ход и завершает его по истечении времени. | API 33+ | Ожидается, версия 0.1.0 |
| [Passive Check Focus](mods/passive_check_focus/README.md) | При пассивной проверке отменяет движение по клику и переводит камеру на бросившего персонажа. | API 33+ | Ожидается, версия 0.1.0 |

DC Check добавляет КС в русские и английские диалоги. Run Speed и Combat Turn Timer подстраивают язык окна под язык игры.

## Быстрая установка

1. Откройте [Releases](https://github.com/SunsetSH/BG3-mods/releases) и в разделе **Assets** скачайте `.pak` выбранного мода. Если скачали ZIP, извлеките из него `.pak`.
2. Для Run Speed, Combat Turn Timer и Passive Check Focus предварительно установите [BG3 Script Extender по инструкции](docs/INSTALL.md#bg3-script-extender).
3. Закройте игру и скопируйте `.pak` в `%LOCALAPPDATA%\Larian Studios\Baldur's Gate 3\Mods`. Вставьте путь в адресную строку Проводника. Если папки `Mods` ещё нет, создайте её.
4. Запустите игру. В главном меню откройте «Моды» → «Установленные» и включите мод.

Обновление, удаление и порядок загрузки DC Check с переводами описаны в [полной инструкции](docs/INSTALL.md).

## Для разработчиков

В репозитории лежат исходники модов и инструменты распаковки данных игры, генерации локализации, проверки и сборки `.pak`. Локальные сборки лежат в `paks/`.

### Стек

| Что | Версия | Зачем |
|---|---|---|
| Python | 3.15 | скрипты сборки и генерации данных модов |
| uv | 0.13 | окружение и зависимости |
| ruff | 0.17 | линтер и форматтер |
| mypy | 2.4 (strict) | проверка типов |
| pytest | 9.2 | тесты |
| LSLib / Divine CLI | v1.20.4 | распаковка и упаковка `.pak`, конвертация `.lsf ↔ .lsx` |
| .NET Desktop Runtime | 8.0 | нужен LSLib |

Почему так: [ADR 0002](docs/adr/0002-python-uv-toolchain.md), [0003](docs/adr/0003-lslib-divine.md), [0006](docs/adr/0006-multi-mod-repository.md).

### Быстрый старт сборки

```sh
winget install -e --id Microsoft.DotNet.DesktopRuntime.8
winget install -e --id astral-sh.uv
uv sync                                       # Python 3.15 и dev-зависимости
uv run python scripts/setup_tools.py          # LSLib в tools/lslib, SHA256 проверяется
git config core.hooksPath .githooks
uv run python scripts/check.py                # полная проверка всех модов
uv run python scripts/dc_check_generate.py    # шаг генерации, только у DC Check
uv run python scripts/pack.py <мод>           # paks/<Pak>.pak и build/<Pak>-<версия>.zip
```

Игра не в стандартной папке Steam: задайте `BG3_DIR` (папка с `bin` и `Data`).

### Новый мод

```sh
uv run python scripts/new_mod.py <slug> <PakName> "<Имя в игре>" "<English description>"
```

Скрипт создаёт `mods/<slug>/` с новым UUID, `meta.lsx` версии 0.1.0, `README.md` и `TESTING.md` по шаблону. Пока в них остаётся `ЗАПОЛНИТЬ`, `check.py` и `pack.py` падают. Правила: [ADR 0006](docs/adr/0006-multi-mod-repository.md).

## Карта проекта

| Путь | Ответственность |
|---|---|
| `mods/<slug>/pak/` | исходники мода, ровно то, что попадает в `.pak` |
| `paks/` | собранные `.pak` всех модов и готовые утилиты, если они нужны интерфейсу мода. Исходники, ZIP-архивы релизов, документация и временные файлы хранятся вне неё |
| `mods/<slug>/pak/Mods/<Pak>_<UUID>/meta.lsx` | имя, UUID, версия мода (единственный источник версии) |
| `mods/<slug>/pak/Mods/<Pak>_<UUID>/ScriptExtender/` | настройки Script Extender и серверный, клиентский и общий Lua-код мода |
| `mods/<slug>/README.md` | для игрока: возможности, установка с утилитами, совместимость, устройство |
| `mods/<slug>/TESTING.md` | ручная проверка мода в игре |
| `mods/<slug>/NOTES.md` | нюансы данных и движка, найденные для этого мода |
| `src/bg3_mods/paths.py` | папки репозитория, путь к игре, папка модов игрока |
| `src/bg3_mods/divine.py` | вызовы Divine CLI |
| `src/bg3_mods/mods.py` | поиск модов в `mods/`, общие проверки (папка, UUID, версия, SE, раздел «Установка»), генерируемые части |
| `src/bg3_mods/meta.py` | чтение `meta.lsx`, `Version64` ↔ строка версии |
| `src/bg3_mods/scaffold.py` | `meta.lsx` и шаблоны документов нового мода |
| `src/bg3_mods/gamedata.py` | распаковка данных игры в `unpacked/` и конвертация в `.lsx`/`.xml` с кэшем, общим для всех модов |
| `src/bg3_mods/templates/` | шаблоны `README.md` и `TESTING.md` нового мода |
| `src/bg3_mods/lsx.py` | разбор XML игры, `GameDataError` |
| `src/bg3_mods/loca.py` | чтение и запись `.loca.xml`, имена файлов, наложение перевода |
| `src/bg3_mods/script_extender.py` | статичная проверка `ScriptExtender/` мода: `Config.json`, `Ext.Require` |
| `src/bg3_mods/<slug>/` | код конкретного мода (сейчас `dc_check/`, см. его README) |
| `scripts/check.py` | полная проверка: ruff, формат, mypy, pytest |
| `scripts/pack.py` | сборка `.pak` любого мода, проверка содержимого, zip для загрузки |
| `scripts/new_mod.py` | заготовка нового мода |
| `scripts/<slug>_*.py` | скрипты конкретного мода (`dc_check_generate.py`) |
| `scripts/unpack_game.py` | распаковка `.pak` игры в `unpacked/` для исследования |
| `scripts/setup_tools.py` | загрузка LSLib нужной версии |
| `tests/` | pytest, зеркалит `src/` (`tests/<slug>/` с `__init__.py` для кода мода); `tests/fixtures/` маленькие файлы в формате игры |
| `docs/PLAN.md` | задачи: инфраструктура и раздел на каждый мод |
| `docs/INSTALL.md` | установка, обновление и удаление модов из общего релиза |
| `docs/adr/` | принятые решения, сквозная нумерация |
| `docs/NOTES.md` | общие нюансы: LSLib, `meta.lsx`, установка модов |
| `.githooks/` | проверки перед коммитом |
| `tools/`, `unpacked/`, `build/` | вне git: LSLib, данные игры и ZIP-архивы для релиза |

## Где искать

| Задача | Где |
|---|---|
| Добавить мод | `scripts/new_mod.py`, правила в [ADR 0006](docs/adr/0006-multi-mod-repository.md) |
| Поменять версию мода | `Version64` в `ModuleInfo` и `PublishVersion` его `meta.lsx`; формула `src/bg3_mods/meta.py#version64` |
| Мод с генерируемыми файлами | `src/bg3_mods/mods.py#GENERATED`, папка в `.gitignore` |
| Что проверяется у каждого мода | `src/bg3_mods/mods.py#mod_problems`, `#installation_problems`, `tests/test_mods.py` |
| Шаблон README и TESTING нового мода | `src/bg3_mods/templates/`, подстановка в `src/bg3_mods/scaffold.py#_render` |
| Текст метки DC, термин DC/КС | `src/bg3_mods/dc_check/labels.py#TERMS`, `#format_label` |
| Добавить язык в DC Check | `src/bg3_mods/dc_check/sources.py#LANGUAGE_SOURCES`, `src/bg3_mods/dc_check/labels.py#TERMS` |
| Какие проверки помечает DC Check | `src/bg3_mods/dc_check/dialogs.py#RollOption.has_dc`, `src/bg3_mods/dc_check/labels.py#handle_dcs` |
| Пределы и поля скорости Run Speed | `mods/run_speed/pak/Mods/RunSpeed_<UUID>/ScriptExtender/Lua/Shared/Speed.lua` |
| Лимит хода, отсчёт и окно Combat Turn Timer | [Устройство Combat Turn Timer](mods/combat_turn_timer/README.md#устройство) |
| Фильтр бросков, отмена движения и камера Passive Check Focus | [Устройство Passive Check Focus](mods/passive_check_focus/README.md#устройство) |
| Обновить LSLib | `scripts/setup_tools.py#LSLIB_VERSION`, `#LSLIB_SHA256` |
| Путь к игре | `src/bg3_mods/paths.py#game_data_dir` |
| Команды Divine | `src/bg3_mods/divine.py#pack_command`, `#extract_command`, `#list_command` |
| Куда сборщик сохраняет готовые моды | `paks/`, пути заданы в `src/bg3_mods/paths.py` |
| Значения DC по актам | `unpacked/Shared/Public/Shared*/DifficultyClasses/`, `unpacked/Gustav/Public/GustavDev/DifficultyClasses/` (после `dc_check_generate.py`) |
| Шаблон варианта ответа в UI | `unpacked/Game/Public/Game/GUI/Library/DialogueTemplates.xaml` |

## Лицензия

MIT, см. [LICENSE](LICENSE).
