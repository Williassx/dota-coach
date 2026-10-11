# Отдельный source-пакет предложений мыши

[Родитель](README.md) · [Recipe](../mouse-proposal-manifest.json) ·
[Канонический API](../../../05-intervention-ui/02-mouse-targeting/notes/mouse-panel.md) ·
[Отчёт](../../../05-intervention-ui/02-mouse-targeting/reports/cloud-mouse-panel.md).

`panorama_source_mouse_proposal`: exact 5 files (loader, XML, CSS, model, panel),
4 XML links. Hidden MouseProposalRoot и 6 empty plain Labels, 7 unique IDs,
ordered model→panel. Нет inline events/bootstrap/инсталляции; explicit bind.
Политика использует прежний parser с локальным разрешением Panel.visible;
default policy и остальные девять kinds не расширены.

Из корня: `python3 creators/creator-2/10-user-testing/01-install-guide/tools/prepare_ui_handoff.py --screen mouse-proposal`.
Создаётся новый bundle под build/dota_coach и immutable companion report рядом.
Текущие исходники/целостность проверяются существующими build/verify. Existing output
сохраняется. Manifests альтернативны: не накладывать этот на общий HUD.
Source2/native gameplay/lease и второй владелец ещё не проверены.
