/* Explicit local camera request only. No origin reads, unit orders or tracking lock. */
var DotaCoachCameraNative = (function () {
    "use strict";
    function integer(value, max) {
        return typeof value === "number" && value >= 0 && value <= max && value % 1 === 0;
    }
    function create() {
        function check(index) {
            try {
                if (!integer(index, 2147483647)) {
                    return { available: false, reason: "Герой выбранного игрока не определён." };
                }
                if (typeof GameUI === "undefined" || typeof GameUI.MoveCameraToEntity !== "function") {
                    return { available: false, reason: "Фокус камеры недоступен в этом клиенте." };
                }
                var player = Game.GetLocalPlayerID();
                if (!integer(player, 63)) {
                    return { available: false, reason: "Локальный участник матча не определён." };
                }
                var team = Players.GetTeam(player);
                if (team !== 2 && team !== 3) {
                    return { available: false, reason: "Команда локального участника не определена." };
                }
                if (Entities.IsValidEntity(index) !== true || Entities.IsRealHero(index) !== true) {
                    return { available: false, reason: "Герой исчез или не поддерживается." };
                }
                if (Entities.GetTeamNumber(index) !== team) {
                    return { available: false, reason: "Фокус доступен только герою своей команды." };
                }
                if (Entities.IsAlive(index) !== true) {
                    return { available: false, reason: "Герой мёртв; фокус недоступен." };
                }
                return { available: true, reason: null };
            } catch (error) {
                return { available: false, reason: "Проверка доступности камеры не выполнена." };
            }
        }
        return {
            check: check,
            focus: function (index) {
                var result = check(index);
                if (!result.available) { return { requested: false, reason: result.reason }; }
                try {
                    GameUI.MoveCameraToEntity(index);
                    return { requested: true, reason: null };
                } catch (error) {
                    return { requested: false,
                        reason: "Запрос фокуса не подтверждён; положение камеры неизвестно." };
                }
            }
        };
    }
    return { create: create };
}());
