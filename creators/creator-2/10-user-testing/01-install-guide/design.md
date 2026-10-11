# Проверенный source handoff для локального Codex

[Подпункт](README.md). C2 результат: одна команда создаёт/проверяет выбранный
source пакет существующими helpers и записывает отдельный неизменяемый отчёт
передачи. Установка/компиляция/запуск ещё не выполняются. Исполнитель работает
самостоятельно; Windows канал из этой среды отсутствует.

tools/prepare_ui_handoff.py: fixed --screen choices probe/hud/preparation/
intervention/intervention-screen/voice-text, default probe. Единственные recipes
остаются в C2 foundation/packaging. Existing build CLI создаёт новый output;
generic verifier повторно проверяет source bytes/graph. Опциональный --bundle
только проверяет существующий пакет. Весь report расположен рядом с bundle,
под build/dota_coach, exclusive create; existing files/Steam не меняются.

Отчёт связывает screen/kind/recipe/bundle/source digests, verification и фактическую
платформу/точный Git root+HEAD/dirty. Unknown metadata остаётся null, не выдумывается.
Все native destination/installation/compile/runtime/microphone/effect/other-owner
пункты null/false/not_run. Report вне bundle, чтобы generic integrity не ослаблять.
Read-only input `--bundle` не превращается в разрешение перезаписать companion.

Canonical notes/install-guide.md — маршрут локальному Codex: сначала существующий
bounded workspace audit, затем source handoff, фактические пути/отдельный addon,
нативная foundation приёмка, explicit component bind и evidence. Только ранее
проверенные cloud команды; Windows/Dota действия обозначаются непроверенными.
Нет ручного задания пользователю или непроверенной команды запуска игры.
