# Native text preview acceptance fixture

[Подпункт](README.md). Ведущая роль76 — разработчик панели тренера создателя2;
область — отдельная тестовая сцена existing VoicePanels и её сборка/evidence.
Существующие design/implementation-plan задают поведение. Пользователь поручил
автономное продолжение; новые механики и production bootstrap не проектируются.

Native compiler обнаружил запрет id у корневого Panel. Canonical XML получает
анонимный внешний Panel с прежним VoiceTextRoot внутри; strict6/5 package policy
проверяет точную новую topology. Public binding scope — внутренний VoiceTextRoot.

Fixed panorama_source_voice_text остаётся6ресурсов/5ссылок, inert. Отдельный
builder читает эту exact recipe через existing guarded policy, копирует5canonical
ресурсов, добавляет test Hud manifest/driver и derived layout:8outputs. Исходный
voice_text.xml остаётся неизменённым. Test driver explicitly bind, uses labelled
synthetic roster and public preview/updateRoster/dispose; без C1/ASR/microphone,
GameEvents, отправки, native mouse callback или имитации настоящего нажатия.

В derived layout TEST label остаётся отдельным sibling к VoiceTextRoot, чтобы
dispose скрывал только проверяемую панель. Смена состава очищает введённый текст
и предложение. Старый handle после dispose не читает DTO; fresh bind принимает
только новый snapshot. Native screenshots проверяют реальный TextEntry/labels,
а вызов preview не доказывает физический ввод или hittest.

Приёмка: exact unchanged canonical hashes; strict non-executable test manifest;
guard refusal before writes; compilation without failures; native phase assertions
и снимки bound/ready/ambiguous/reset/disposed/rebound; owned client завершён.
Отдельный отчёт сохраняет границы native evidence и не превращает source flags
в runtime approval. Второй создатель и полноценный голос остаются открытыми.
