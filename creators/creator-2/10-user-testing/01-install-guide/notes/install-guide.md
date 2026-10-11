# Source handoff и будущая нативная приёмка

[Подпункт](../README.md) · [Helper](../tools/README.md).

Это маршрут для агента в локальном клоне `D:\AI\dota2coach`, а не просьба
пользователю выполнять команды. Cloud Linux не подключён к Windows. Здесь
проверены source-команды Python3.12/Node24; запуск на Windows ещё не подтверждён.
Не объявляйте состояние этой инструкции законченной установкой кастомки.

## 1. Проверить фактическую среду

В локальном Codex прочитать AGENTS.md/C2-AGENTS/этот подпункт. Сохранить изменения
пользователя; не подменять другой проект или установку. Использовать существующий
[bounded аудит](../../../01-foundation/01-workspace-audit/notes/windows-start.md)
и зафиксировать Python/Node, Steam/Dota/build_id, Workshop Tools, game/content пути
и настоящий шаблон. Не предполагать, что пути Steam совпадают с папкой Git.

## 2. Подготовить и проверить source-пакет

Из корня репозитория cloud-проверены следующие команды; на Windows агент выбирает
реальный доступный Python launcher, без заявления, что он уже установлен:

```bash
python3 creators/creator-2/10-user-testing/01-install-guide/tools/prepare_ui_handoff.py
python3 creators/creator-2/10-user-testing/01-install-guide/tools/prepare_ui_handoff.py --screen voice-text
python3 creators/creator-2/10-user-testing/01-install-guide/tools/prepare_ui_handoff.py --screen orders-timeline
python3 creators/creator-2/10-user-testing/01-install-guide/tools/prepare_ui_handoff.py --screen opponent-roster
python3 creators/creator-2/10-user-testing/01-install-guide/tools/prepare_ui_handoff.py --screen match-observation
```

Первый вариант готовит probe. Каждый создаёт новую папку в build/dota_coach,
проверяет её единственным verifier и рядом пишет exclusive `.handoff.json`.
Report содержит actual platform/Python/Git root+HEAD/dirty, assets/digests и source
verification. Native destination null, installation=false, nativechecks=not_run.
Report сам не авторизует установку; перед будущим использованием source verification
нужно повторить для текущих исходников. Выходы/отчёты не редактируются вручную.

| --screen | Ресурсы/ссылки | Source-сценарий | Canonical инструкция |
|---|---:|---|---|
| probe | 5/4 | Диагностическая панель | [C2-01-02](../../../01-foundation/02-panorama-capability/notes/panorama-probe.md) |
| hud | 13/12 | HUD/карточки/камера/цели | [C2-11-02](../../../11-integration/02-addon-packaging/notes/build-manifest.md) |
| preparation | 15/14 | Локальные предложения состава/героев/тактики | [Preparation recipe](../../../11-integration/02-addon-packaging/notes/preparation-package.md) |
| intervention | 6/5 | Панель ручного запроса | [Request panel](../../../05-intervention-ui/01-request-ack/notes/request-panel.md) |
| intervention-screen | 13/12 | Карточки/запрос в одном private flow | [Screen binding](../../../11-integration/01-ui-binding/notes/intervention-screen.md) |
| voice-text | 6/5 | Текст→local proposal | [Text preview](../../../06-voice/03-voice-feedback/notes/text-preview.md) |
| orders-timeline | 5/4 | Локальная история приказов | [Timeline](../../../07-match-screen/03-orders-timeline/notes/panel.md) |
| opponent-roster | 5/4 | Публичные имена/герои соперников | [Public roster](../../../07-match-screen/02-opponent-cards/notes/public-roster.md) |
| match-observation | 10/9 | Соперники + история в одной сцене | [Group binding](../../../11-integration/01-ui-binding/notes/match-observation.md) |

Эти manifests альтернативны. Не копировать их поверх друг друга в одну сцену:
автоматического объединения/общего runtime ещё нет. Source files каждой библиотеки
остаются canonical; generated resources всегда создаются отдельно.

## 3. Нативная проверка — пока не выполнена

После фактического аудита агент выбирает отдельный тестовый addon/template и пишет
конкретный план файлов. Существующие addon/game/content изменения сохраняются.
Команды компиляции/запуска закрепляются только по реальному шаблону/API. Сейчас
здесь нет проверенной команды запуска Dota; C1 сервер/диагностическое событие,
общий контракт и игровой bootstrap требуют своей проверки и второго владельца.

По canonical component инструкции выполнить explicit bind с синтетическим snapshot
в правильном контексте; не подставлять отсутствующий транспорт/право ввода.
Сохранить actual build/log/errors, visible labels/button/TextEntry, scale/hittest,
scope cleanup/reload, stale callbacks и ровно одну обработку действия. Voice-text
показывает local предложение и «микрофон не подключён»; не отмечать ASR пройденным.

## 4. Зафиксировать результат отдельно

Journal C2-00-action-log: фактические native commands/пути/build_id/evidence и
непроведённые случаи. Обновить native README checkboxes только по evidence и
приёмке второго человеческого владельца. Critic/source verifier её не заменяют.
Не писать compile/runtime/voice/gameplay=true из наличия файлов или `.handoff.json`.
