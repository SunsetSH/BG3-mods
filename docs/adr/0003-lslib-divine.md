# 0003. LSLib (Divine CLI) для работы с `.pak`

Дата: 2026-11-23. Статус: принято.

## Контекст

Нужно распаковывать `.pak` игры, конвертировать `.lsf ↔ .lsx` и собирать `.pak` мода. Варианты: LSLib (Norbyte/lslib, де-факто стандарт сообщества, активно обновляется: v1.20.4 от 2026-01-24), официальный BG3 Toolkit от Larian, BG3 Modder's Multitool (обёртка над LSLib с GUI).

## Решение

LSLib v1.20.4, `ExportTool-v1.20.4.zip`, консольный `Divine.exe`. Скачивается `scripts/setup_tools.py` в `tools/lslib/` (вне git), SHA256 закреплён (`5e02368f...190e`, взят из GitHub release). Требует .NET 8 Desktop Runtime.

## Последствия

- Сборка воспроизводима и запускается из CLI без GUI.
- Divine молча пропускает файлы, если в пути есть папка на точку: см. `docs/NOTES.md`, обход в `scripts/pack.py`.
- Обновление LSLib: поменять `LSLIB_VERSION` и `LSLIB_SHA256`, удалить `tools/lslib`, прогнать `pack.py`.
- Официальный Toolkit может понадобиться для публикации на mod.io: это открытая задача в PLAN.
