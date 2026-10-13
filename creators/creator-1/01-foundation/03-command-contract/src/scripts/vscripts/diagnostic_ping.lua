-- Candidate diagnostic protocol only. Pure; no engine, orders or authorization.
local diagnostic_ping = {}

local function usable_id(value)
    return type(value) == "string" and #value > 0 and #value <= 64
        and not value:find("^%s") and not value:find("%s$")
        and not value:find("[%z\1-\31\127]")
end

local function response(id, status, reason)
    return {protocol_version = 1, request_id = id, status = status, reason = reason}
end

function diagnostic_ping.evaluate(payload)
    if type(payload) ~= "table" then return nil end
    local id = rawget(payload, "request_id")
    if not usable_id(id) then return nil end
    if getmetatable(payload) ~= nil then return response(id, "rejected", "invalid_request") end
    local count = 0
    for key in pairs(payload) do
        count = count + 1
        if key ~= "protocol_version" and key ~= "request_id" then
            return response(id, "rejected", "invalid_request")
        end
    end
    if count ~= 2 then return response(id, "rejected", "invalid_request") end
    local version = rawget(payload, "protocol_version")
    if type(version) ~= "number" or version ~= version or version == math.huge
        or version == -math.huge or version <= 0 or version % 1 ~= 0 then
        return response(id, "rejected", "invalid_request")
    end
    if version ~= 1 then return response(id, "rejected", "unsupported_version") end
    return response(id, "ok", "none")
end

return diagnostic_ping
