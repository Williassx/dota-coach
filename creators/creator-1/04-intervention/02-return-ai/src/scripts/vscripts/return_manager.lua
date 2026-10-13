-- C1-04-02: pure AI-return manager (no native calls).
-- Return path: MANUAL --(cancel|timeout|release)--> REASSESS --> AI.
-- On return the manual action is cancelled and the observation is
-- re-evaluated at a fresh revision; completed return cycles are counted
-- (three live cycles stay an open native item). A mere label change is
-- not a return: state must reach AI with reassessed=true.

if CD1C402Return == nil then
	CD1C402Return = class({})
end

local function validRevision(value)
	return type(value) == "number" and value == value and value >= 0
		and value <= 9007199254740991 and value % 1 == 0
end

function CD1C402Return:Init()
	self.state = "AI"
	self.reassessed = false
	self.completedCycles = 0
	self.lastObservationRevision = 0
	self.manualCancelled = false
end

-- Pure notification from an authoritative caller; no engine confirmation here.
function CD1C402Return:EnterManual(observationRevision)
	if self.state ~= "AI" then return nil, "not-in-ai" end
	if not validRevision(observationRevision)
		or observationRevision < self.lastObservationRevision then
		return nil, "bad-revision"
	end
	self.lastObservationRevision = observationRevision
	self.state = "MANUAL"
	self.reassessed = false
	return true
end

-- Begin the return from MANUAL with an explicit reason.
function CD1C402Return:StartReturn(reason)
	if self.state ~= "MANUAL" then
		return nil, "not-manual"
	end
	if reason ~= "cancel" and reason ~= "timeout" and reason ~= "release" then
		return nil, "bad-reason"
	end
	self.state = "REASSESS"
	self.manualCancelled = true
	self.reassessed = false
	return true
end

-- Finish the return once the observation was re-evaluated.
function CD1C402Return:FinishReturn(observationRevision)
	if self.state ~= "REASSESS" then
		return nil, "no-reassess"
	end
	if not validRevision(observationRevision) then
		return nil, "bad-revision"
	end
	if observationRevision <= self.lastObservationRevision then
		return nil, "stale-observation"
	end
	self.lastObservationRevision = observationRevision
	self.state = "AI"
	self.reassessed = true
	self.manualCancelled = false
	self.completedCycles = self.completedCycles + 1
	return self.completedCycles
end
