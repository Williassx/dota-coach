# План общей сцены наблюдения

[Родитель](README.md) · [Спецификация](match-observation-design.md).
Root работает inline по `superpowers:executing-plans`; критик только после всего блока.

1. Написать Node VM tests с реальными двумя child modules/panels: separate sources,
   invalid isolation, parent hide-beforeDTO, busy guards, all required nodes,
   partial repair, duplicate reservation, dispose callbacks, old/new ownership.
   Получить RED missing binder, затем реализовать один canonical binding и GREEN.
2. Создать inert shell/loader/CSS и fixed recipe в C2-11-02. Добавить packaging tests
   до composer/dispatch: exact mapping/inputs, root ownership/topology/order,
   strict inert XML, raw fingerprints/current-source, output preservation,
   actual packaged VM. Получить RED, реализовать composer на existing policies,
   добавить screen registry и получить targeted GREEN.
3. Добавить Node suite в canonical catalog (Python test — existing packaging suite),
   пройти actual handoff и полный runner. Один финальный критик готового блока;
   исправления через воспроизведение и повторные проверки по необходимости.
4. Обновить API/README/report, отдельный UTC журнал, график, usage и reusable draft.
   Проверить документы/JSON/progress/diff, normal main publication и remote/clean.

Создателя 1/общий контракт не менять. Native/C1/второй человек остаются открытыми.

## Ход исполнения

Шаг 1: 14 RED missing binder → 14 GREEN. Шаг 2: 8 packaging сценариев,
5 unsupported recipe ERROR / 3 guard PASS → 8 GREEN; targeted 154 PASS.
Шаг 3: новый Node suite в каталоге, actual handoff и full 42 / 897 PASS.
Один критик выявил visibility rollback при failed acquisition; regression
15 Node / 14 PASS / 1 FAIL, исправлен claimed/restore guard. Final targeted
155 PASS, свежий handoff после fix, full 42 / 898 PASS. Других findings нет.
Шаг 4: README/API/report/journal/progress/usage/draft обновлены. Обязательные
документные проверки перед публикацией; commit/remote SHA/clean подтверждаются
выводом задачи и историей Git, без отдельного commit ради собственного хеша.
