-- C1-03-03: pure single order arbiter (no native calls).
-- Priority: MANUAL (coach, confirmed) > coach order > AI intent.
-- Every intent is validated before it could reach the engine adapter:
-- known orderId only once, current revision only, MANUAL orders only
-- while manual mode holds. The engine adapter itself is an open item.

if CD1C303Arbiter == nil then
	CD1C303Arbiter = class({})
end

function CD1C303Arbiter:Init()
	self.seen = {}
	self.lastRevision = 0
end

-- Resolve one validated command. cmd: {orderId, source, revision, ...}.
-- source: "manual" | "coach" | "ai". manualMode: boolean.
-- Returns command + winner, or nil + reason.
function CD1C303Arbiter:Resolve(cmd, manualMode)
	if type(cmd) ~= "table" then
		return nil, "bad-command"
	end
	if cmd.orderId == nil or self.seen[cmd.orderId] == true then
		return nil, "duplicate-or-missing-id"
	end
	if type(cmd.revision) ~= "number" or cmd.revision < self.lastRevision then
		return nil, "stale-revision"
	end
	if cmd.source == "manual" and manualMode ~= true then
		return nil, "manual-outside-manual"
	end
	if cmd.source ~= "manual" and cmd.source ~= "coach"
		and cmd.source ~= "ai" then
		return nil, "unknown-source"
	end
	self.seen[cmd.orderId] = true
	self.lastRevision = cmd.revision
	return cmd, cmd.source
end
