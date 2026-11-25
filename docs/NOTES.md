# Нюансы: общие

Данные ниже проверены на игре с Patch 8 Hotfix 10 (последний `Patch8_HotFix10.pak` в `Data`), LSLib v1.20.4, 2026-11-23.

Нюансы отдельного мода лежат рядом с ним: [DC Check](../mods/dc_check/NOTES.md), [Run Speed](../mods/run_speed/NOTES.md), [Combat Turn Timer](../mods/combat_turn_timer/NOTES.md), [Passive Check Focus](../mods/passive_check_focus/NOTES.md).

## Сборка и LSLib

- **Divine пропускает пути с точкой.** Если в абсолютном пути есть папка на `.` (репозиторий лежит в `H:\.pet\`), `create-package` пишет «Package created successfully» и создаёт пустой пакет на 48 байт. Поэтому `scripts/pack.py` копирует `pak/` мода во временную папку и сверяет список файлов в пакете. Распаковка, `convert-resources` и `convert-loca` работают и с такими путями.
- **LSLib пишет один диалог обрезанным.** `END_BrainBattle_FinalDecision_Nested_EvilShadowheart` (кат-сцена финала, без проверок) после `convert-resources` обрывается на атрибуте `CinematicNodeContext`. Генератор пропускает такие файлы с предупреждением и путём.
- **Формат `meta.lsx`.** Взят с установленного мода BetterTooltips (версия файла 4.8.0.10, строки `LSString`). `Version64` = `major<<55 | minor<<47 | revision<<31 | build`. 0.1.0.0 = `140737488355328`, 1.0.0.0 = `36028797018963968`. Версия мода хранится только в `meta.lsx` (`ModuleInfo` и `PublishVersion`), `tests/test_mods.py` сверяет их, `pack.py` берёт её для имени zip. Заготовку пишет `src/bg3_mods/scaffold.py#build_meta`: ElementTree пишет пустые узлы как `<node id="x" />`, игре это не мешает.
- **uv после установки через winget** появляется в PATH только в новом терминале. До этого: `%LOCALAPPDATA%\Microsoft\WinGet\Links\uv.exe`.

## Игра и моды

- **Где мод хранит тексты.** Моды с mod.io кладут их в `Mods/<папка>/Localization/<Язык>/<имя>.loca.xml` (XML без конвертации в `.loca`). Fixed Russian translation так же поставляет гендерные файлы: `Localization/Russian/Gender/Female/russian.loca.xml` и т.д. Мы повторяем имена файлов игры.
- **Моды пользователя** ставятся через mod.io (имена вида `name_uuid-xxxx.pak` в `%LOCALAPPDATA%\Larian Studios\Baldur's Gate 3\Mods`). Стоят ImpUI и BetterTooltips: они правят XAML, но не локализацию.
- **Osiris-имена для боя и пошагового режима** (из `Gustav.pak` → `Mods/*/Story/RawFiles/Goals`): события `EnteredCombat(obj, combat)`, `LeftCombat`, `EnteredForceTurnBased(obj)`, `LeftForceTurnBased`; запросы `IsInCombat(obj, out)`, `IsInForceTurnBasedMode(obj, out)`, `IsPartyMember(obj, includeSummons, out)`; база `DB_PartyMembers(char)`.
- **Папка для `.pak`** одна для всех модов: `%LOCALAPPDATA%\Larian Studios\Baldur's Gate 3\Mods`. Script Extender ставится иначе: `DWrite.dll` из `BG3SE-Updater-<дата>.zip` (релизы `Norbyte/bg3se`, v33 от 2026-10-12) в `Baldurs Gate 3\bin`. Источник: текст релиза v33.
- **Версия загрузчика и версия API Script Extender.** Тег `v33` относится к архиву загрузчика с резервной версией Script Extender. Рабочую версию загрузчик обновляет при запуске игры. Минимум для мода задаёт `RequiredVersion` в `ScriptExtender/Config.json`. [FAQ Norbyte](https://github.com/Norbyte/bg3se/releases)
