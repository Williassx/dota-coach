# C2-03-02: диагностика возврата камеры

Ведущий76/C2, root107/114/173/174/175. Реализация одним исполнителем; один
итоговый reused critic после результата. Новых процессов ради каталога не нужно.

Исходный факт: previous smoke requested=true, distanceXY4520.37 через1,5s и
исходная позиция позднее. Ни причина, ни отсутствие краткого прибытия не доказаны.
Применяются systematic-debugging, brainstorming и writing-plans: цель — разделить
передачу запроса, transient movement и действие native ввода, без изменения продукта.

Выбрана дополнительная TEST-only driver variant существующего15output builder,
а не изменение gateway/производственной панели или повтор прежнего единственного
замера. FixedHUD13 и default camera fixture сохраняются. Вариант принимает только
точные camera/motion; произвольный source/path запрещён до writes.

После native guard собственного живого realhero записывать lookAt/cameraPosition,
ownOrigin, курсор, кнопки мыши, размеры/scale панели и clamped world→screen projection.
20baseline samples, ровно один programmatic Activated, 80post samples, Schedule0.2s.
Фактический Date.now elapsed сохраняется; частота Schedule не обещает точного clock.
Не читать чужие origins. Clamped projection не доказывает видимость объекта.

Гипотеза H1: внеокновой/краевой указатель может вызывать native edge pan после
краткого запроса. На первом запуске только read-only измерения и console find
camera cvars; не менять cursor, preferences, cvars, camera target/lock/position.
H1 не объявлять установленной причиной только по корреляции. Если нужны условия
с изменением одной переменной, отдельно зафиксировать дизайн/rollback до действия.

Диагностический near threshold64worldunits относится только к sampled distanceXY
этой сцены, не к полному критерию карты/реального игрока/масштабирования. При любой
дистанции сохранить previous failed sample и не переписать исторический отчёт.
Кадры baseline/early/settled/returned осмотреть. Quit только own PID+exactUTCticks.

Runtime m3 установил native clamped projection triple [0.5,0.45477646589279175,0];
исходная гипотеза length2 оказалась неподтверждённой. Final driver сохраняет raw3,
третий компонент не интерпретирует. OwnOrigin/lookAt/cameraPosition3 и cursor2
прошли последовательные reads до этого failed поля; последующая100sample серия
должна подтвердить их формы в данной установке. Failed m2/m3 сохраняются отдельно.
