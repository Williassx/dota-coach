# Предложенные назначения, локальный черновик

[Подпункт](../README.md) · [Дизайн](../design.md).

`DotaCoachHeroRoles.create()` создаёт pure ES5 model. `update({revision,team,proposals})`
принимает атомарную частную UI-проекцию. Team — exact draft C2-04-01 с пятью ids/versions,
complete=true и serverConfirmed=false; proposals — пять соответствующих профилей
с kind/source и до 32 сочетаний heroId/heroName/role/coverage каждый. Схема в дизайне.
Fixtures используют реальный API модели состава, но все имена/предложения тестовые.

`assign(id,heroId,role)` принимает только предоставленное предложение. В стандартном
раннем локальном черновике герои/позиции уникальны; занятой герой или позиция оставляет
прежний выбор. Это предварительная UI-политика, C1 сверит её с режимом игры.
`remove(id)`/`clear()` редактируют назначения, дубли не увеличивают revision.

`view()` возвращает независимые профили/choices/назначения и три предупреждения на
назначение: origin, unconfirmed compatibility, coverage. Kind не определяется по
sourceLabel. Empty choices объясняются до попытки выбора. Никакой hero proficiency,
личности, патча, цифрового сходства или server readiness из этой проекции не следует.

`draft()` при ready возвращает frame revision, assignmentRevision, копию team draft,
assignments{id,profileVersion,heroId,role}, local complete и serverConfirmed=false.
Порядок — team.players; при empty/invalid/disposed null. Frame, team и assignment
counters разные, equality между ними не требуется. Источник ещё должен доказать
актуальность предложений относительно каталога/команды; internal matching её не доказывает.

New frame скрывает старые данные во время decode. High-water раньше body, committed
revision только после полного commit; old/duplicate не читают body/keys. Getter guards
после каждого чтения предотвращают stale/newer/invalid/dispose overwrite. Exact shape
и длины arrays проверены до/после copy. Новый profileVersion/исчезновение предложения
снимают назначение, не выбирают его повторно. Source errors сохраняют объяснение снятия.

AssignmentRevision защищён от MAX_SAFE_INTEGER; overflow closes без wrap. Эта граница
практически недостижима через public API и проверена source review, а не динамически.

```sh
node --test creators/creator-2/04-preparation-ui/02-hero-role-picker/tests/hero-role.test.cjs
```

Нет panel/HUD/network/storage/start/native. C1-07-01, настоящие profiles/heroes/identity,
compatibility/server, нативная приёмка и второй равноправный владелец открыты.

reset() закрывает прежний source context без disposal; highwater сохранён,
committed draft=null, новый frame строго выше. Counter bump только actualremoval.
