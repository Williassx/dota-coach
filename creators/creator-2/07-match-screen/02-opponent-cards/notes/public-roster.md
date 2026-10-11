# Публичный состав: API и подключение

[Родитель](README.md) · [Спецификация](../design.md).

В отдельной сцене загрузить XML и явно вызвать
`DotaCoachOpponentPanels.bind(root)`, где root — `OpponentRosterRoot`.
Это инструкция будущему интегратору, а не готовый bootstrap.
Определения не читают game API и не выполняют автоматического bind.

Методы binding:

| Метод | Результат |
| --- | --- |
| `update({revision,players})` | bool: accepted источник и успешное отображение |
| `refresh()` | bool: повторный показ текущей проекции, без чтения нового источника |
| `view()` | copied состояние; null во время незакрытой занятой операции |
| `dispose()` | закрыть private модель, скрыть root, стереть тексты, освободить владение |
| `isDisposed()` | проверить дерево на явном вызове и вернуть closed |

До update и после отказа ready=false. Valid empty players=[] — ready=true,
ноль известных игроков, пять unknown slots. playerName/heroName=null означают
неизвестное; число0 не является именем. Тексты plain, html=false даже для строки
с символами разметки. canIssue=false; API выбора/приказа нет.

Один instance принадлежит одному источнику/сцене. У revision нет значения
server epoch. После invalid/stale/equal-conflict источник закрывается, accepted
highwater сохраняется; восстановление требует строго более новой valid revision.
При смене источника dispose и новый bind с новой моделью, без переноса highwater.
Идентичный повтор разрешён только пока ready=true и ordered rows те же.

DTO содержит ровно revision/players; каждая из0..5 dense rows — ровно
id/playerName/heroName. Own enumerable data fields, без accessor/symbol/лишних
полей. Координаты/health/items отклоняются до чтения их значений. Клиент не может
установить, законно ли само предоставленное имя: разрешённую публичную проекцию
должна готовить C1-09-02. evidence=supplied_public_roster,
sourceAuthorizationConfirmed=false остаются обязательными.

Все17 Labels, strip и пять card Panels обязательны, в том числе пустые slots.
Hide/missing/replacement/invalid tree закрывает binding на update/refresh/view/
isDisposed. Наблюдателя нет; интегратор обязан доставлять обновления и dispose.
Root ownership резервируется до discovery и не передаётся во время cleanup.
Старая closed API не читает snapshots и не пишет в свежий binding.

Отдельная source-панель включена в [фиксированный пакет](../../../11-integration/02-addon-packaging/notes/opponent-roster-package.md)
и handoff selector `opponent-roster`. Общий HUD пока не подключён.
Нативная компиляция/читаемость/hittest, серверные права, реальный public roster
и проверка второго владельца не проведены.
