-- C1-04-01: pure manual-mode state machine (no native calls).
-- States: AI -> REQUESTED -> MANUAL -> AI (cancel, timeout or release).
-- Entering MANUAL cancels the current action and the AI queue (pure flags;
-- the engine half is an open native item). A manual order to the same hero
-- carries the manual revision so a stale AI order cannot override it;
-- integration with the order arbiter (C1-03-03) is open.
-- Server confirmation of the MANUAL transition arrives via Confirm(true);
-- Confirm(false) or Confirm without REQUESTED is rejected.

if CD1C401Manual == nil then
	CD1C401Manual = class({})
end

function CD1C401Manual:Init()
	self.state = "AI"
	self.manualRevision = 0
	self.aiQueueCancelled = false
	self.currentActionCancelled = false
end

-- Coach requests manual control of one bound actor.
function CD1C401Manual:Request(actorEntity)
	if self.state ~= "AI" then
		return nil, "not-in-ai"
	end
	if type(actorEntity) ~= "number" then
		return nil, "bad-actor"
	end
	self.state = "REQUESTED"
	self.actor = actorEntity
	return true
end

-- Server confirms (or refuses) the transition into MANUAL.
function CD1C401Manual:Confirm(serverConfirmed)
	if self.state ~= "REQUESTED" then
		return nil, "no-request"
	end
	if serverConfirmed ~= true then
		self.state = "AI"
		return nil, "server-refused"
	end
	self.state = "MANUAL"
	self.manualRevision = self.manualRevision + 1
	self.aiQueueCancelled = true
	self.currentActionCancelled = true
	return self.manualRevision
end

-- Leave MANUAL: reason is "cancel", "timeout" or "release".
function CD1C401Manual:Leave(reason)
	if self.state ~= "MANUAL" then
		return nil, "not-manual"
	end
	if reason ~= "cancel" and reason ~= "timeout" and reason ~= "release" then
		return nil, "bad-reason"
	end
	self.state = "AI"
	self.actor = nil
	self.aiQueueCancelled = false
	self.currentActionCancelled = false
	return true
end

function CD1C401Manual:IsManual()
	return self.state == "MANUAL"
end
