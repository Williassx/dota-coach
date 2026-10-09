# План подготовки фокуса камеры

> Исполнитель: superpowers:executing-plans; пять критиков read-only. Автономное
> продолжение поручено пользователем до остановки.

**Цель:** явная кнопка фокуса героя своей команды без слежения/переключения управления.
**Спецификация:** [design.md](design.md).
**Архитектура:** native gateway проверяет доступную сущность; Panorama adapter
показывает выбранного и отдельный результат запроса. Нет транспорта по умолчанию.
**Стек:** ES5 Panorama, node:test/vm Node18+, XML/CSS.

## Ограничения и ревью

- Только этот подпункт/индексы/журнал, прежние UI и foundation не меняются.
- Вызов GameUI.MoveCameraToEntity только своим живым realhero при playerID>=0/team2|3.
- Не использовать координаты/маркеры/постоянное слежение/приказы и не читать origin.
- Без явного gateway/цели нет действия; результат requested не равен arrival.
- Exact input/result copies, closed/generation после чтения и единственный owner root.

## 1. Проверки до кода

**Создать:** tests/camera.test.cjs.
**Новые source:** src/panorama/scripts/custom_game/camera_native.js, camera_panel.js.

- [x] RED native: no startup motion, живой realhero своей команды, dead/opponent/
  stale entity/spectator/API failure, повторная проверка, forbidden APIs.
- [x] RED панели: no gateway/target, setTarget без motion, явный клик/requested,
  выбранная/исходная цель результата, recheck/death, stale click/refresh/dispose,
  invalid input/result, plain text, render/bind failure, getter disposal/rebind.
- [x] Выполнить тесты, подтвердить ожидаемый missing source RED.

## 2. Минимальная реализация

- [x] Реализовать Native.create/check/focus по API/точным полям спецификации.
- [x] Реализовать Panels.bind/setTarget/refresh/dispose/isDisposed с поколением,
  независимыми копиями, guard до/после чтения и единственным owner root.
- [x] GREEN новой suite; добавить XML/CSS без demo/bootstrap/автоматического bind.

```sh
node --test creators/creator-2/03-map-view/02-camera-overlays/tests/camera.test.cjs
```

## 3. Ревью и публикация

- [x] Пять read-only критиков; подтверждённые дефекты воспроизвести/исправить.
- [x] Повторить project baseline, проверить XML/resources/IDs, ES5 и локальные ссылки.
- [x] Создать README каталогов/notes/camera.md/reports/cloud-camera.md,
  обновить статусы/индексы/журнал; сохранить проверенную команду start_skill.

Публикация: обычный fast-forward main с проверкой SHA/чистого дерева.
Нативный фокус/карта, entity mapping, hittest/маркеры/общий HUD остаются открытыми.
