-- TEST-only addon entrypoint; installed as addon_game_mode.lua by its fixture.
-- Sender comes only from native source-entity/player equality, never payload data.
local diagnostic_ping = require("diagnostic_ping")
local registered = false

local function integer(value)
    return type(value) == "number" and value == value and value >= 0
        and value <= 2147483647 and value % 1 == 0
end

local function trace(source_index, entity, player_id, native_match, metadata, result)
    local source = integer(source_index) and tostring(source_index) or "-"
    local player = integer(player_id) and tostring(player_id) or "-"
    print("DCPING_SERVER sourceindex=" .. source .. " entity=" .. type(entity)
        .. " player=" .. player .. " native-match=" .. tostring(native_match)
        .. " metadata=" .. metadata .. " result=" .. result)
end

local function on_request(source_index, payload)
    local entity, player_id, player = nil, nil, nil
    local verified = false
    if integer(source_index) then
        local resolved = pcall(function()
            entity = EntIndexToHScript(source_index)
            if entity == nil or type(entity.GetPlayerID) ~= "function" then return end
            player_id = entity:GetPlayerID()
            if not integer(player_id) then return end
            player = PlayerResource:GetPlayer(player_id)
            verified = player ~= nil and player == entity
        end)
        verified = resolved and verified
    end
    if not verified then
        trace(source_index, entity, player_id, false, "uninspected", "drop_unknown_sender")
        return
    end
    local wire = payload
    local metadata = "uninspected"
    if type(payload) == "table" then
        local engine_player_id = rawget(payload, "PlayerID")
        if engine_player_id == nil then
            metadata = "absent"
        else
            local matches_native = integer(engine_player_id) and engine_player_id == player_id
            metadata = matches_native and "matching_native" or "mismatch"
            -- Strip only matching engine metadata. Mismatch stays an extra wire
            -- field: rejected to the verified sender, never used as a recipient.
            if matches_native and getmetatable(payload) == nil then
                wire = {}
                for key, value in pairs(payload) do
                    if key ~= "PlayerID" then wire[key] = value end
                end
            end
        end
    end
    local reply = diagnostic_ping.evaluate(wire)
    if reply == nil then
        trace(source_index, entity, player_id, true, metadata, "drop_unusable_id")
        return
    end
    local sent = pcall(function()
        CustomGameEventManager:Send_ServerToPlayer(player, "dota_coach_probe_result", reply)
    end)
    trace(source_index, entity, player_id, true, metadata, sent and (reply.status .. ":" .. reply.reason) or "send_failed")
end

function Precache(context)
    -- No diagnostic assets, heroes or units are created.
end

function Activate()
    if registered then return end
    local installed = pcall(function()
        CustomGameEventManager:RegisterListener("dota_coach_probe_request", on_request)
    end)
    registered = installed
    trace(nil, nil, nil, false, "uninspected", installed and "activated" or "register_failed")
end
