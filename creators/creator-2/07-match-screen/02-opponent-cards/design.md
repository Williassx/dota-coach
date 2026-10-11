# Верхний ряд: публичный состав соперника

Пользователь ожидает пять карточек соперника сверху игрового экрана. Основной
исполнитель работает в отделе2 самостоятельно. Этот шаг готовит модель и отдельную
Panorama source-панель; общий HUD и нативная приёмка остаются отдельными этапами.

Варианты: повторно использовать собственные Roster-карточки (там есть mode/availability
и выбор адресата), принимать весь opponent snapshot и фильтровать (слишком широкий
вход), либо принять минимальный публичный DTO. Выбран третий: нет полей боевого
состояния, кнопок выбора, приказов, camera/entity/transport или server contract.

`DotaCoachOpponentRoster.create()` принимает `update({revision,players})` → bool.
revision — local safe integer, players — dense array0..5 exact rows
`{id,playerName,heroName}`. id — уникальная непустая строка≤64 без крайних пробелов/
control characters. playerName/heroName — null либо непустая строка≤64; null означает
«Имя неизвестно»/«Герой неизвестен», не нулевое значение. Дополнительные поля,
включая координаты/health/items/availability, отклоняются без чтения их значений.
DTO — own enumerable data descriptors без getters/symbols; bounds проверяются до
чтения элементов. Названия остаются plain текстом, а не HTML-разметкой.

После первого valid снимка revision монотонна. При готовом составе повтор того же
revision с точно теми же rows допускается без изменений. Конфликт того же revision,
stale/invalid input очищают текущую проекцию и закрывают ready; highwater сохраняется.
После этого нужен строго более новый valid revision. Старый состав не восстанавливается
из ошибочного источника. Empty valid roster — готовый источник с нулём известных
игроков, а не потеря связи. Один instance на источник/сцену, recreate при смене.

`view()` возвращает copied `{ready,revision,players,closed,evidence,sourceAuthorizationConfirmed}`.
Каждая row содержит только id/playerName/heroName + playerText/heroText/informationText/
canIssue=false. informationText — «Боевые данные неизвестны.». evidence —
supplied_public_roster, sourceAuthorizationConfirmed=false: клиент не проверяет
разрешение данных. C1-09-02 обязан дать разрешённую проекцию до интеграции. Здесь
нет утверждения, что hidden враг действительно отфильтрован сервером.

Busy guard предшествует Proxy traps; `view` во время update возвращает null.
Nested update не читает DTO, dispose во время чтения отменяет commit. Dispose
закрывает model и удаляет сохранённые имена/highwater. API не содержит select/send.

`DotaCoachOpponentPanels.bind(root)` создаёт одну private модель, explicit
update/refresh/view/dispose/isDisposed. Root содержит status/hint и пять triples
Name/Hero/Info — plain Labels, initially empty/hidden root. Invalid input очищает
видимое до DTO reads. Strip OpponentCards и пять OpponentCard containers также обязательны; всего24 ID. Все nodes обязательны; required node hide/replace/missing
или invalid root закрывают binding на явном вызове. Busy/generation/ownership
guards защищают reentry/partial bind/нового владельца. Timer/handler/polling нет;
caller отвечает за передачу снимков и dispose. Native appearance/hittest, source
пакет, общий HUD и второй человеческий владелец не подтверждаются VM/XML tests.
