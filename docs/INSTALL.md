# Установка модов для Baldur’s Gate 3

Выберите нужные моды. Пакеты устанавливаются независимо друг от друга. Шаги ниже рассчитаны на Windows.

| Мод | Пакет или архив | Требования |
|---|---|---|
| DC Check 1.0.0 | `DCCheck.pak` или `DCCheck-1.0.0.zip` | Дополнительные утилиты не нужны |
| Run Speed 1.0.0 | `RunSpeed.pak` или `RunSpeed-1.0.0.zip` | BG3 Script Extender с API 33 или новее |
| Combat Turn Timer 0.1.0 | `CombatTurnTimer.pak` или `CombatTurnTimer-0.1.0.zip` | BG3 Script Extender с API 33 или новее |
| Passive Check Focus 0.1.0 | `PassiveCheckFocus.pak` или `PassiveCheckFocus-0.1.0.zip` | BG3 Script Extender с API 33 или новее |

DC Check показывает КС в русских и английских диалогах. Run Speed меняет скорость бега отряда вне боя и пошагового режима. Combat Turn Timer автоматически завершает ход по таймеру. Passive Check Focus останавливает движение по клику и переводит камеру на персонажа после пассивной проверки.

DC Check и Run Speed прошли ручную проверку. После уточнения требования к Script Extender сборку Run Speed пока повторно не проверяли в игре. Combat Turn Timer и Passive Check Focus доступны для пробного использования. Ручная проверка этих двух модов, в том числе загрузка сохранений после отключения, ещё впереди. Для пробы используйте отдельное сохранение.

## BG3 Script Extender

1. Закройте игру. Скачайте `BG3SE-Updater-20261012.zip` со страницы [Norbyte/bg3se v33](https://github.com/Norbyte/bg3se/releases/tag/v33). Имя архива и путь сверены 25.11.2026.
2. Извлеките `DWrite.dll` в папку `bin` игры. Стандартный путь Steam `C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3\bin`. Для другой библиотеки откройте Steam → ПКМ по игре → «Управление» → «Просмотреть локальные файлы» → `bin`.
3. При следующем запуске игры подключитесь к интернету, чтобы загрузчик скачал совместимое обновление Script Extender. Для нескольких модов достаточно одной установки Script Extender. [Обновление и совместимость у Norbyte](https://github.com/Norbyte/bg3se/releases)

## Установка `.pak`

1. Закройте игру. В [релизе `mods-2026-11-25`](https://github.com/SunsetSH/BG3-mods/releases/tag/mods-2026-11-25) разверните **Assets** и скачайте нужный `.pak`. Если выбрали ZIP мода, извлеките из него `.pak`.
2. Вставьте `%LOCALAPPDATA%\Larian Studios\Baldur's Gate 3\Mods` в адресную строку Проводника. Создайте папку `Mods`, если её ещё нет, и положите в неё выбранные `.pak`.
3. Запустите игру. В главном меню откройте «Моды» → «Установленные» и включите моды по их названиям из таблицы.
4. Если используете DC Check вместе с модом-переводом, поставьте DC Check ниже перевода в порядке загрузки. Оба мода могут менять одни и те же строки. Подробности есть в разделе совместимости. [DC Check](https://github.com/SunsetSH/BG3-mods/blob/mods-2026-11-25/mods/dc_check/README.md#совместимость).

## Обновление и удаление

- **Обновление.** Закройте игру, замените старый `.pak` новым файлом с тем же именем и проверьте, что мод включён.
- **Удаление.** Выключите мод во вкладке «Установленные», закройте игру и удалите его `.pak` из папки `Mods`. При загрузке сохранения игра может показать окно проверки модов.
- **Script Extender.** Оставьте `DWrite.dll` в `bin`, если Script Extender нужен другим модам. Если он больше не нужен, закройте игру и удалите `DWrite.dll` из `bin`.

## Инструкции отдельных модов

- [DC Check](https://github.com/SunsetSH/BG3-mods/blob/mods-2026-11-25/mods/dc_check/README.md#установка)
- [Run Speed](https://github.com/SunsetSH/BG3-mods/blob/mods-2026-11-25/mods/run_speed/README.md#установка)
- [Combat Turn Timer](https://github.com/SunsetSH/BG3-mods/blob/mods-2026-11-25/mods/combat_turn_timer/README.md#установка)
- [Passive Check Focus](https://github.com/SunsetSH/BG3-mods/blob/mods-2026-11-25/mods/passive_check_focus/README.md#установка)
