-- C1-04-03: pure generation guards (no native calls).
-- Every timer and completion belongs to a (generation, action) pair:
-- a stale event from a past generation or a replaced action is dropped
-- and can never finish a new intervention. Death, target loss,
-- disconnect and hero replacement all bump the generation first, so
-- resurrection never replays an old order. Pause handling needs the
-- proven game clock (open item of C1-02-03) and stays open here too.

if CD1C403Guards == nil then
	CD1C403Guards = class({})
end

function CD1C403Guards:Init()
	self.generation = 0
	self.action = nil
end

-- Start a new guarded action; bumps the generation.
function CD1C403Guards:Begin(action)
	if type(action) ~= "string" or action == "" then
		return nil, "bad-action"
	end
	self.generation = self.generation + 1
	self.action = action
	return self.generation
end

-- Any interrupting event (death, loss, disconnect, replace) bumps first.
function CD1C403Guards:Interrupt(kind)
	if kind ~= "death" and kind ~= "loss" and kind ~= "disconnect"
		and kind ~= "replace" and kind ~= "pause" then
		return nil, "bad-kind"
	end
	self.generation = self.generation + 1
	self.action = nil
	return self.generation
end

-- Accept an event only for the current (generation, action) pair.
function CD1C403Guards:Accepts(generation, action)
	if generation ~= self.generation then
		return false
	end
	if self.action == nil or action ~= self.action then
		return false
	end
	return true
end
