# Облачная проверка source-пакета подготовки

[Подпункт](../README.md) · [План](../preparation-plan.md).

**Дата UTC:** 2026-10-10. **Основа:** 6e070a5. Проверка source Python/NodeVM.

- 18 новых тестов RED missingrecipe →18 GREEN. Исправлена мутация testfixture:
  строковая замена emptyhost первоначально не учитывала class/hittest атрибуты.
- Self-review воспроизвёл nesteddependencies gap:18PASS/1FAIL→19GREEN.
  Архитектурный критик независимо нашёл wrapper layoutfile и CustomUIElement children;
  exactmanifesttree/attrs и top-level dependencycounts исправили все варианты.
- Architecture re-review нашёл src на произвольном Panel:19PASS/1FAIL→20GREEN.
  src теперь допустим только у dependency includes; Panel/Button варианты отклонены.
- Пять read-only направлений review завершены. UX замечание nestedscroll исправлено
  scoped finalCSS: three lists fit-children/squish squish, общий stack scroll.
- Новый generatedlayout сохраняет три originalPanel trees/IDs/plainlabels/disabled
  buttons и9 ordered scripts. VM загружает именно generated dependency paths/tree,
  explicit bind даёт4watchers, actualteamclick меняет один syntheticdraft, dispose
  снимает timers. Definitions load инертен; native API вызовы запрещены fixture.
- 24 suites:542PASS,0FAIL/skip/todo. Это прежние522 +20. Прежние policies probe/HUD
  проверены; foundation28 и HUD19 проходят. Python syntax двух helpers проверен.
- Actual CLI создал build/dota_coach/preparation-source-20261010-01:15resources;
  verify package_verified=true/assets15/xml_resource_links14,
  source2_compiled=false/runtime_verified=false. После parserfix verify повторён.

Изменён shared foundation boundedreader/lazy thirdkind; добавлены exactrecipe/composer,
shell/style/manifest, тесты/docs/индексы. Genericverifier не требовал изменения.
Source implementations не копировались. Compiler/install/bootstrap/реальные данные/
сервер/эффекты/secondowner открыты. Windows/Dota/WorkshopTools не запускались.

Start_skill revision22 сохранён и прочитан обратно; прочие поля сохранены.
requires_publish=true/активация через настройки открыта. Installation/network/secrets/
runtime не менялись. Проверены1368 локальных ссылок и README всех библиотечных папок.
Default CLI также создал свежий15asset output; verify14refs/PASS, старый output сохранён.
