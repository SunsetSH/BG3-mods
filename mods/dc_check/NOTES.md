# Нюансы: DC Check

Данные ниже проверены на игре с Patch 8 Hotfix 10 (последний `Patch8_HotFix10.pak` в `Data`), LSLib v1.20.4, 2026-11-23.

## Данные игры

- **Таблица DC разбита на три файла, а не продублирована.** `Shared.pak` → `Public/Shared/DifficultyClasses/` (акт 1, `HiddenPerception_*`, `Legacy_*`), `Public/SharedDev/DifficultyClasses/` (акты 2 и 3), `Gustav.pak` → `Public/GustavDev/DifficultyClasses/` (`Act3_Impossible`, `HAV_TakingIsobel_GhoulSpiked`). UUID не пересекаются, генератор их объединяет и падает при расхождении чисел. DC в узле уже привязан к акту через UUID (`Act2_Medium` = 14), отдельно акт считать не нужно.
- **Проверка в диалоге это узел `ActiveRoll`** (`Mods/*/Story/DialogsBinary/**/*.lsf` в `Gustav.pak` и `Shared.pak`): `RollType`, `Skill`, `Ability`, `Advantage`, `DifficultyClassID`, тексты в `TaggedTexts/.../TagText@handle` (до 11 вариантов по тегам). `PassiveRoll` не вариант ответа, у него нет текста.
- **Нулевой `DifficultyClassID`** у 128 из 3446 `ActiveRoll`: все атаки (`Melee*Attack`) и часть `RawAbility`. Для них DC не показываем.
- **Два хэндла с разными DC** (5 и 10) в `UND_DuergarLoyalSergeant_FollowUp` и `UND_DuergarCamp_LoyalFollowUp`: метка `(DC 5/10)`. В английской локализации этих двух текстов нет.
- **Патчи не трогают нужные файлы.** `Patch8_HotFix9/10.pak` и `GustavX.pak` не содержат диалогов, `DifficultyClasses` и локализации.
- **В русской игре DC называется «КС»**, не «СЛ»: хэндлы `hd45a9fec...` «КС [1]», `h428c8e9f...` «КС: [1]».
- **«[УБЕЖДЕНИЕ]» рисует UI**, это не часть строки локализации: `DialogueTemplates.xaml`, параметр `Type=Tag` в `CtxAnswer`, формат `[{0}] ` в верхнем регистре. Значит, наша метка в начале текста встаёт сразу после тега.

## Локализация

- **Гендерные варианты есть только в русском.** `Gender/Female/russian.loca` хранит реплики для героини (417 вариантов с проверкой), `Gender/Neutral/russian_X_to_M.loca` ещё 395. В английском эти файлы пустые.
- **Версия хэндла.** В 1 из 3727 хэндлов версия в диалоге и в `.loca` различается; пишем версию из `.loca`.
- **Fixed Russian translation заменяет всю русскую локализацию**, в 1488 текстах с проверкой есть правки. Оба мода задают одни хэндлы, побеждает загруженный позже. Для личной сборки `dc_check_generate.py --base-pak` берёт тексты перевода.
