# Пакет мыши с наблюдением целей

[Родитель](README.md) · [Recipe](../mouse-targeting-manifest.json) ·
[API](../../01-ui-binding/notes/mouse-targeting.md) · [Отчёт](../reports/cloud-mouse-targeting-package.md).

Из корня: `python3 creators/creator-2/10-user-testing/01-install-guide/tools/prepare_ui_handoff.py --screen mouse-targeting`.
Fixed kind panorama_source_mouse_targeting: 7 resources/6 XML links/7 IDs.
Standalone mouse-proposal остаётся5/4. Это альтернативные manifests, не overlay.
Canonical files принадлежат своим библиотекам, copies только generated output.

Canonical двухскриптовый mouse XML проверяется existing standalone validator.
Лишь generated scripts добавляют Targets в начало и MouseTargeting binding в конец,
сохраняют root/6plain labels. Raw source sha256 в comment; verify recomposes current
sources, включая whitespace changes. Exact mapping/graph/DTD/link/output guards
сохранены. Helper не устанавливает и не запускает игру, outputs immutable.

В правильном native контексте explicit bind MouseProposalRoot по API с now/maxAgeMs;
clock должен быть реальным локальным источником milliseconds. Оба alternative layouts
inert: auto-bind/handlers/bridge отсутствуют. VM не доказывает native clock/обзор,
identity/hittest/input authorization/lease/gameplay/AI return или приёмку владельца.
