# План локальной истории

Основание: [design](design.md). Один автор файлов — создатель 2.

1. Написать Node VM тесты с настоящей моделью Orders: lifecycle stages, задержанный
   первый снимок, смена карточки/эпохи, correlation, terminal stability, bounded history,
   скопированные данные, malformed/getter/reentrant/dispose. Зафиксировать RED.
2. Реализовать единственный `orders_timeline_state.js`, получить GREEN.
3. Добавить suite в canonical каталог C2-11-03; выполнить целевой и полный прогон.
4. После завершения подпроекта один reused final critic. Записать evidence и открытые
   panel/native/server/second-owner этапы, обновить журнал и график библиотеки.
5. Обновить актуальный cloud draft без изменения остальных полей, проверить
   обязательные проверки документов/графика/Git и опубликовать normal push.
