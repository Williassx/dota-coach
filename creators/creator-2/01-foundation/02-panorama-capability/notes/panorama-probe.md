# Panorama: что найдено и что проверить локально

Открытые источники исследованы 9 октября 2026 года; установленный шаблон,
native runtime и справка API дополнительно проверены 11 октября.

## Проверенные открытые источники

Это материалы сообщества ModDota, не разрешение Valve и не проверка версии пользователя.
Репозитории прочитаны через HTTPS Git в облаке; зависимости и шаблон не установлены.

| Материал | Зафиксированная версия | Наблюдение |
|---|---|---|
| [TypeScriptDeclarations](https://github.com/ModDota/TypeScriptDeclarations/tree/df7722b560d5c616f7b2f6be42480aa5053baec8) | df7722b560d5c616f7b2f6be42480aa5053baec8 | Описания Panorama/Lua генерируются из dota-data |
| [TypeScriptAddonTemplate](https://github.com/ModDota/TypeScriptAddonTemplate/tree/cc021e25d9314015fc2338850ef85593e2ffcbde) | cc021e25d9314015fc2338850ef85593e2ffcbde | XML подключает JS/CSS; кнопка отправляет событие; Lua отвечает конкретному игроку |

Точные ссылки в декларациях:

- [GameEvents](https://github.com/ModDota/TypeScriptDeclarations/blob/df7722b560d5c616f7b2f6be42480aa5053baec8/packages/panorama-types/types/api.d.ts):
  `Subscribe(eventName, callback) → handle`, `Unsubscribe(handle)`,
  `SendCustomGameEventToServer(eventName, payload)`.
- В том же файле: `$.GetContextPanel()`, `$.Schedule(seconds, callback)` и
  `$.CancelScheduled(handle)`. Реальное поведение при паузе/перезагрузке проверяется локально.
- [CustomGameEventManager](https://github.com/ModDota/TypeScriptDeclarations/blob/df7722b560d5c616f7b2f6be42480aa5053baec8/packages/dota-lua-types/types/api.generated.d.ts):
  `RegisterListener` описывает callback `(userId, event)` с PlayerID;
  `Send_ServerToPlayer(player, eventName, payload)` адресует ответ одному клиенту.
  Достоверное определение отправителя и невозможность подмены проверяет создатель 1
  в установленной версии; UI не отправляет PlayerID как полномочие.
- [manifest и HUD](https://github.com/ModDota/TypeScriptAddonTemplate/tree/cc021e25d9314015fc2338850ef85593e2ffcbde/content/panorama/layout/custom_game):
  `CustomUIElement type="Hud"`, XML includes, Button `onactivate`.
- [hud.ts](https://github.com/ModDota/TypeScriptAddonTemplate/blob/cc021e25d9314015fc2338850ef85593e2ffcbde/src/panorama/hud.ts)
  и [GameMode.ts](https://github.com/ModDota/TypeScriptAddonTemplate/blob/cc021e25d9314015fc2338850ef85593e2ffcbde/src/vscripts/GameMode.ts)
  демонстрируют связь. **Не копировать обработчик:** пример дополнительно меняет
  состояние героя модификатором. Для нашего ping нужен ответ без игровой механики.

Шаблон предупреждает о преобразовании boolean в 0/1 и массивов в объекты при
пересылке. В минимальном предложении используются только строки и целое число версии.

## Дополнительные API для подготовленных исходников

В `packages/panorama-types/types/api.d.ts` того же зафиксированного commit
интерфейс GameUI описывает `CustomUIConfig()`. Комментарий типа использует имя Game,
но функция находится именно в интерфейсе GameUI. В `panels.d.ts` найдены
`FindChildTraverse`, `SetPanelEvent("onactivate", callback)`, `ClearPanelEvent`
и `IsValid`; свойства `enabled` и Label.text используются для кнопки/статуса.
События ondelete в списке PanelEvent нет, поэтому оно не предполагается.

## Локальные входы перед установкой и приёмкой

- Результат [аудита](../../01-workspace-audit/notes/workspace-audit.md): фактические
  пути Dota, content/game, доступный шаблон и способ компиляции ресурсов.
- Снимок версии/сборки и выбранного отдельного аддона; существующий аддон не заменять.
- Проверенный способ загрузки manifest, диагностики ошибок и освобождения подписок.
- Ответственный создатель 1 и рассмотренное имя/поля диагностического события.

Нельзя объявлять TypeScript-шаблон установленным штатным шаблоном Valve или переносить
его команды npm на пользовательскую установку без исследования. Команда запуска
сцены фиксируется по реально выбранному шаблону, а не подставляется заранее.

## Журнал приёмки

11 октября 2026, Windows build25845666: карта и UI скомпилированы, локальная
template_map загружена. В native log есть panel_ready/request_sent, видимость
панели/idle-статуса/кнопки подтверждена скриншотом1280×720.
[Отчёт и изображение](../../01-workspace-audit/reports/windows-foundation-2026-10-11.md).
В отдельном Tools прогоне panel_ready подтверждён в 18:11:06 UTC вместе с
проверенным Tools HUD 1280×720 и уникальным живым VConsole echo.
Native справка содержит GameEvents, Schedule/CancelScheduled, CustomUIConfig,
SetPanelEvent/ClearPanelEvent и hittest/hittestchildren; наличие API не доказывает
приёмку сценариев. Захват Windows Computer Use завершился timeout, UI Automation
не показал ProbeButton; нативный клик не выполнен. Hittest, timeout/retry,
reload/dispose и C1 ответ открыты;
первый игровой прогон завершился DXGI-падением. Таблица ниже остаётся общей
приёмкой составных сценариев: видимость сама не закрывает ввод вне панели.

| Сценарий | Сейчас | Что сохранить после Windows-прогона |
|---|---|---|
| Панель/кнопка видны, карта принимает ввод вне панели | Видимость подтверждена; ввод вне панели не проверен | Скриншот1280×720 и native log в Windows-отчёте |
| Запрос → Lua → адресный ответ с тем же ID | Не запускался | Связанные клиентский и серверный журналы |
| Нет обработчика → тайм-аут → новая попытка | Не запускался | ID обоих запросов и результат |
| Старый ответ, другая версия, повторная загрузка | Не запускался | Текущий запрос не закрывается чужим ответом; нет дублей |

В облаке подтверждено чтение источников. На Windows подтверждена видимость панели;
ни один составной нативный сценарий выше полностью не отмечен пройденным.
Подготовлены исходники и поведенческие проверки в модели движка; это отдельный
[облачный результат](../reports/cloud-behavior.md), не строки нативной приёмки выше.
