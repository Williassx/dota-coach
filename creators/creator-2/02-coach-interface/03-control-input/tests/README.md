# Проверки маршрута ввода

[Подпункт](../README.md) · [Отчёт](../reports/cloud-routing.md)

[input-routing.test.cjs](input-routing.test.cjs) загружает настоящие модели,
адаптеры карточек/приказов и координатор через node:test/vm. Панели, события и
планировщик моделируются; попытки вызова игровых API перехватываются.

Из корня репозитория:

```sh
node --test creators/creator-2/02-coach-interface/03-control-input/tests/input-routing.test.cjs
```

Проверяются адресат, неизвестный режим, gate мёртвой карточки, фоновый снимок,
unknown через смену/удаление выбора, stale callbacks, copied selection, отказ
callback/bind/render/watch, владение root, поздний report и cleanup.
Клики вызывают настоящие обработчики адаптеров; поведение мыши в движке не моделируется.
