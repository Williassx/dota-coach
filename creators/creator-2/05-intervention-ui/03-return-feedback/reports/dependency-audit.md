# Аудит зависимостей отмены и возврата ИИ

[Родитель](README.md) · [Спецификация](../design.md).
2026-10-11, Linux cloud; read-only проверка опубликованного репозитория после a6ef50b.

C1-04-01, C1-04-02, C1-04-03 имеют README со статусом «запланировано»; в этих
папках нет реализации сервера. Requests model C2-05-01 отслеживает запрос локально:
ACK/accepted и mode-observed не дают input authority/lease; local expiry сохраняет
unknown. Targets снимает недоступное наблюдение, а MouseTargeting снимает proposal.
Ни один из этих источников не подтверждает остановку действия или возобновление ИИ.

Доступные tools повторно проверены: remote Windows shell отсутствует. Read current
Codex terminal вернул «No app terminal session is attached to this thread yet».
Windows клон/Dota/Workshop Tools подтверждены пользователем, но это не канал запуска.
Не проводились native build/gameplay/lease/cancel/AI return; пользовательских данных
и creator1/shared contracts не меняли. Не попросили пользователя выполнять команды.

Подготовлены design и подробный implementation plan. Реализация cancel/lease/return
adapter зависит от настоящего серверного контракта; не добавлен fake transport.
Native checklist остаётся полностью открытым, общий graph21.6% не увеличен документами.
Рутинные вопросы не задавались, критик для планирования не запускался.

## Обновление 12 октября 2026, Windows

Локальный shell/Workshop Tools/native TEST scene теперь доступны; прежний cloud refusal остаётся историческим. C1-04-01/02/03 повторно прочитаны, в каталогах по-прежнему только README, реализации contract/server нет. Existing request/mouse API smoke не подтверждают cancel/lease/AI return. C2-05-03 implementation gate требует настоящего C1 contract; fake transport не добавлен. Независимые [Windows source checks](../../../11-integration/03-end-to-end/reports/windows-portability-2026-10-12.md) выполнены без изменения серверного отдела.
