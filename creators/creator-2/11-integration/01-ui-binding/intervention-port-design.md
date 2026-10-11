# Общая модель для панели ручного запроса

[Подпункт](README.md). Основа: a197706. Исполнитель: создатель 2, самостоятельно.
Пользователь поручил продолжать без рутинных согласований; сервер и Windows открыты.

Цель: панель показывает существующую private Roster/Requests composition, а не
создаёт второй Requests. Подпроект ограничен портом и подключением одной панели;
общий экран, Roster panel и source composition recipe остаются следующими задачами.

Варианты: копирование snapshots между двумя моделями усложняет корреляцию;
передача всего flow расширяет обязанности панели; выбран узкий owned port.

`flow.requestPort()` возвращает один стабильный объект с own data methods
update/select/begin/report/expire/notSent/view/dispose/isDisposed. update/select
делегируют updateControl/selectPlayer, view возвращает flow.view().manual с общим
roster gate. dispose закрывает весь локальный flow, не отменяя серверный запрос.
Порт принадлежит одной панели; исходный flow остаётся у вызывающего интегратора.

`DotaCoachInterventionRequestPanels.bind(root, send, projection?)` сохраняет старую
standalone ветку без третьего аргумента. Для порта применяется существующий
DotaCoachPanelPorts.adopt с проверкой дерева, которая не обращается к model и
не создаёт рекурсию. Используется стандартный capture own methods/receiver.

Публичный refresh синхронизирует таймер ACK с shared model и обновляет экран.
Интегратор обязан вызывать refresh после внешних изменений. Перед отправкой порт
сравнивает canonical JSON view с успешно отрисованной копией. Если они различны,
первое нажатие только обновляет экран; запрос требует нового явного действия.
Проверка выполняется под busy/generation guard. Это локальная согласованность UI,
не проверка подлинности источника, свежести roster или права ввода.

Сравнение повторяется после очистки полей. begin(displayedSignature) в owned port
атомарно сравнивает canonical view перед вызовом flow.begin: проверка дерева может
сама вызвать смену выбора. Старый port.begin() без аргумента сохраняет локальный API;
интегрированная панель всегда передаёт подпись показанного состояния.

Даже если flow был создан с adapterConfigured=true, панель без собственного send
показывает неподключённый переходник и держит кнопку выключенной.

Приёмка: один flow/port, общая selection и gate, captured actor при смене карточки,
ACK/expiry, stale screen без dispatch, внешнее завершение отменяет ACK timer,
закрытие/повторное подключение без старых callbacks и getter reads, отказ duplicate
port без закрытия первого владельца. Старые standalone и source recipes сохраняются.
