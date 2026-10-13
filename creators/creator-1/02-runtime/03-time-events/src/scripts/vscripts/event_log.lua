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
	self.orderLinks = {}
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

-- Link an entry to a command: orders, modes and observed actions meet here.
-- Returns true, or nil + reason when the entry is unknown.
function CD1C203EventLog:LinkOrder(orderId, seq)
	if type(orderId) ~= "string" or orderId == "" then
		return nil, "bad-order"
	end
	if self.entries[seq] == nil then
		return nil, "unknown-seq"
	end
	if self.orderLinks[orderId] == nil then
		self.orderLinks[orderId] = {}
	end
	self.orderLinks[orderId][#self.orderLinks[orderId] + 1] = seq
	return true
end

-- Tag an entry with the mode it was observed in (AI or MANUAL).
function CD1C203EventLog:TagMode(seq, mode)
	if self.entries[seq] == nil then
		return nil, "unknown-seq"
	end
	if mode ~= "AI" and mode ~= "MANUAL" then
		return nil, "bad-mode"
	end
	self.entries[seq].mode = mode
	return true
end

-- All entries linked to one command, in link order.
function CD1C203EventLog:GetByOrder(orderId)
	local seqs = self.orderLinks[orderId]
	if seqs == nil then
		return {}
	end
	local out = {}
	for _, seq in ipairs(seqs) do
		out[#out + 1] = self.entries[seq]
	end
	return out
end

function CD1C203EventLog:Get(seq)
	return self.entries[seq]
end
