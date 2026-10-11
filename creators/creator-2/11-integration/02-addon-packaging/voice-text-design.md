# Source-пакет local text preview

[Подпункт](README.md). Владелец C2; база b555a3b. Следующий самостоятельный
результат — fixed recipe панели C2-06-03 с двумя canonical JS dependencies.

Шестой kind `panorama_source_voice_text`: ровно6 source→target пар,5 resource links,
один inert Hud loader, voice_text.xml/CSS и Roster→VoiceText→Panel. Нет композиции
или копирования module source в другую библиотеку; output — byte copies в новой
папке build/dota_coach. Existing bounded path/source/output checks и generic
verifier сохраняются. Нельзя расширять пять старых kinds новой TextEntry policy.

Dedicated validator tools/voice_text_layout.py использует existing parse/dependencies
из intervention_screen_layout.py. parse принимает только trusted optional extra
tag attributes; default остаётся strict. Для voice разрешается только leaf TextEntry
с id/enabled=false/text; точные nine IDs и parent topology. Manifest helper для
точного root→Panel→Hud loader общий, пятый kind тоже использует его.
Recipe fixed, raw source byte validation, dependency order и full resource reach.

Проверка context: фактический packaged XML→JSON node tree, actual three JS definitions
в одном Node VM, explicit bind/update, TextEntry input/click→local proposal A, cleanup.
Нельзя считать VM нативной compilation/геометрией/hittest/ASR или игровым действием.
Пакет альтернативен предыдущим manifests; общий runtime/переходы не реализуются.
