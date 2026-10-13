# Реестр current UI/media

[JSONpaths/hashes/evidence](../reports/assets-register-2026-10-13.json) ·
[Report](../reports/assets-register-2026-10-13.md) · [Credits](credits.md).

| Категория | Scope | Происхождение/ограничение |
|---|---:|---|
| C2src XML/CSS/JS |83|Исходники библиотеки C2 по WORKFLOW; код, нелицензированныйграфическийпакет |
| Literal file resources |98|ВнутренниессылкинаJS/CSS/XML, unique source match; не полнаяruntime tracing |
| Diagnostic report PNG |102|Материалыпроверок, per-file report references вJSON; acquisitionневыдумывается при отсутствииevidence |
| Generated progress SVG |1|update_progress.py/progress.json; диаграммадокументации |
| Generated concept PNG |1|docs/visual-concept.md документируетgenerator/fictitiousnames иmap7.40reference |

Rawhelperinventory06:29UTC/HEAD5b4d5fa включал98media; currentHEADdd01f0b добавил
6native resettracePNG. Root сверяет104media/83source/98references иснимокprogress
после одногоотмеченногодействия. Старыеprovenanceclaimsнепереименованы вnewaudit.
Статусправ каждогоэлемента `not_assessed`, author/ownership невыводятсяизhash илиGit.

Ниconcept, ниreportPNG, ниSVGprogress невыбраныдляruntimefixedrecipes. В10source
manifest recipes пакетуютсяcode layouts/scripts/styles, явныхmedia assets нет.
Engine/font/hero/map/audio implicitresources не обследованы этимregexinventory;
transitive/native assets и будущиеdynamic URLs открыты. Нетдоказательствотсутствия
всехвнешнихресурсовво времяgame runtime.

Ignoredbuild содержитTTS/captureaudio/model/deps/compiledmaps; он не входитвреестр
trackedproductmedia и не считаетсялицензированнымreleasepayload. C1библиотека/
Steaminstallation/remoteassets/releaseусловия исследуютсяотдельнымивладельцами.
