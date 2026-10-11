# Source-пакет мыши с наблюдением целей

[Родитель](README.md) · [API binding](../01-ui-binding/notes/mouse-targeting.md).
Root inline; готовая связка опубликована, здесь только fixed source composition.

Новый альтернативный kind panorama_source_mouse_targeting, 7 assets/6 links:
пять canonical resources standalone mouse плюс existing Targets и targeting binder.
Source XML остаётся exact 2-script шаблоном; только generated layout включает ordered
Targets → MouseProposals → MouseProposalPanel → MouseTargetingPanels. Root и все 6
Labels неизменны, 7 IDs. Raw XML fingerprint в generated comment; current-source
recomposition замечает и whitespace изменения. Ни layout copy, ни game install.

Reuse standalone prepare/validate_layout + shared parser; old kind/default policy
не расширять. Exact mapping/schema/unique sources, no events/extra resources, every
output reachable. Inert loader/explicit bind(clock TTL), no bootstrap/clock/native.
Handoff screen mouse-targeting, now 11 alternatives; standalone mouse-proposal
остается5/4. Bundle hashes/source metadata не подтверждают runtime, auth или lease.
