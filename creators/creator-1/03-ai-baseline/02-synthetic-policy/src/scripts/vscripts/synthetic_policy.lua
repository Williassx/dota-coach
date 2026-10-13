-- C1-03-02: explicitly synthetic move/attack policy (no native calls).
-- This is a TEST stand-in, never a model of a real person: every intent it
-- produces carries synthetic=true. All intents leave through the single
-- Decide() controller entry point; nothing is issued from stray timers.
-- The engine adapter half (executing intents) is an open native item.

if CD1C302Synthetic == nil then
	CD1C302Synthetic = class({})
end

function CD1C302Synthetic:Init()
	self.tick = 0
end

-- Single controller entry: projection (C1-03-01 shape) -> intent or nil.
-- Intent: {synthetic=true, kind="move"|"attack", target=?, position=?}.
function CD1C302Synthetic:Decide(projection)
	if type(projection) ~= "table" or type(projection.visible) ~= "table" then
		return nil
	end
	self.tick = self.tick + 1
	if #projection.visible == 0 then
		return { synthetic = true, kind = "move", position = { 0, 0 } }
	end
	local index = ((self.tick - 1) % #projection.visible) + 1
	return { synthetic = true, kind = "attack",
		target = projection.visible[index].id }
end
