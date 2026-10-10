# План локального координатора HUD

> superpowers:executing-plans, TDD и пять read-only критиков. Пользователь разрешил
> непрерывное автономное продолжение; native/серверные зависимости не выдумывать.

**Спецификация:** [design.md](design.md). **Стек:** ES5, node:test/vm, XML/Python packaging.

## 1. RED

**Создать:** tests/hud-binding.test.cjs; дополнить camera/input routing suites.

- [x] Startup/options/ownership/partialbind/cleanup без native side effects.
- [x] Выбор карточки→order recipient→camera recipient, explicit actions only.
- [x] Unknown/bad/reentrant resolver, teardown до send/report, target expiry.
- [x] Camera.setRecipient и optional routing observer backward compatibility.
- [x] Выполнить expected RED до нового source/расширений.

## 2. Реализация

- [x] coach_hud_binding.js в единственной исходной папке; реюз existing adapters.
- [x] Camera.setRecipient/router observer в исходных модулях, без UI copies.
- [x] GREEN и пять критиков; confirmed defects RED→GREEN.

## 3. Общий source-пакет

- [x] HUD status/include и fixed manifest/policy:13resources/10scripts.
- [x] Уточнить packaging tests, реальный build/verify в новом output.
- [x] Прежние266 сценариев и новые проверки, syntax/XML/link/README.
- [x] Docs/status/action log/start_skill подготовлены.
- [ ] Обычный fast-forward main, SHA/clean tree.

Не добавлять default bootstrap/data/transport, server cancellation или native proof.
