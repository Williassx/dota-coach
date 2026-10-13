-- C1-02-03: pure event-log builder (no native clock calls).
-- Notes: creators/creator-1/02-runtime/03-time-events/notes/event-format.md
-- Boundaries: the real game-clock source and pause behaviour are open native
-- questions; callers pass clock explicitly (game time when proven, wall otherwise).
-- The log never reuses entries from a past match: fresh instance per activation,
-- sequence strictly increases, pause entries never consume intervention time.

if CD1C203EventLog == nil then
	CD1C203EventLog = class({})
end

function CD1C203EventLog:Init()
	self.entries = {}
	self.seq = 0
end

-- Append one entry. clock: explicit string/number from caller. etype: string.
-- actorRef: entity number or nil. payload: table or nil.
-- Returns seq on success, nil + reason on rejection.
function CD1C203EventLog:Append(clock, etype, actorRef, payload)
	if type(etype) ~= "string" or etype == "" then
		return nil, "bad-type"
	end
	if actorRef ~= nil and type(actorRef) ~= "number" then
		return nil, "bad-actor"
	end
	self.seq = self.seq + 1
	local entry = {
		seq = self.seq,
		clock = clock,
		type = etype,
		actorRef = actorRef,
		payload = payload,
	}
	self.entries[self.seq] = entry
	return self.seq
end

function CD1C203EventLog:Count()
	return self.seq
end

function CD1C203EventLog:Get(seq)
	return self.entries[seq]
end
