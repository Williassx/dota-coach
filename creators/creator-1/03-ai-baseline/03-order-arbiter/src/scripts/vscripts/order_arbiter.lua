-- C1-03-03: pure single order arbiter (no native calls).
-- Priority: MANUAL (coach, confirmed) > coach order > AI intent.
-- Every intent is validated before it could reach the engine adapter:
-- known orderId only once, current revision only, MANUAL orders only
-- while manual mode holds. The engine adapter itself is an open item.

-- Streaming admission: within one revision, lower priority cannot follow a
-- higher accepted source. A newer revision starts a new decision epoch; this
-- does not arbitrate a batch or cancel an already executed order.
local function validRevision(value)
	return type(value) == "number" and value == value and value >= 0
		and value <= 9007199254740991 and value % 1 == 0
end
local priority = { ai = 1, coach = 2, manual = 3 }

if CD1C303Arbiter == nil then
	CD1C303Arbiter = class({})
end

function CD1C303Arbiter:Init()
	self.seen = {}
	self.lastRevision = 0
	self.lastPriority = 0
end

-- Resolve one validated command. cmd: {orderId, source, revision, ...}.
-- source: "manual" | "coach" | "ai". manualMode: boolean.
-- Returns command + winner, or nil + reason.
function CD1C303Arbiter:Resolve(cmd, manualMode)
	if type(cmd) ~= "table" then
		return nil, "bad-command"
	end
	if type(cmd.orderId) ~= "string" or #cmd.orderId > 128
		or not cmd.orderId:match("%S") or self.seen[cmd.orderId] == true then
		return nil, "duplicate-or-missing-id"
	end
	if not validRevision(cmd.revision) or cmd.revision < self.lastRevision then
		return nil, "stale-revision"
	end
	if cmd.source == "manual" and manualMode ~= true then
		return nil, "manual-outside-manual"
	end
	if cmd.source ~= "manual" and cmd.source ~= "coach"
		and cmd.source ~= "ai" then
		return nil, "unknown-source"
	end
	if type(manualMode) ~= "boolean" then return nil, "bad-manual-mode" end
	if manualMode == true and cmd.source ~= "manual" then
		return nil, "manual-holds-authority"
	end
	local rank = priority[cmd.source]
	if cmd.revision == self.lastRevision and rank < self.lastPriority then
		return nil, "lower-priority"
	end
	self.seen[cmd.orderId] = true
	self.lastRevision = cmd.revision
	self.lastPriority = rank
	return cmd, cmd.source
end
