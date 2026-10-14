-- C1-02-03: pure event-log builder (no native clock calls).
-- Notes: creators/creator-1/02-runtime/03-time-events/notes/event-format.md
-- Boundaries: the real game-clock source and pause behaviour are open native
-- questions; callers pass clock explicitly (game time when proven, wall otherwise).
-- The log never reuses entries from a past match: fresh instance per activation,
-- sequence strictly increases, pause entries never consume intervention time.

if CD1C203EventLog == nil then
	CD1C203EventLog = class({})
end

local function copy(value, seen)
	if type(value) ~= "table" then
		local kind = type(value)
		if kind == "number" and (value ~= value or value == math.huge or value == -math.huge) then return nil, false end
		if kind ~= "nil" and kind ~= "string" and kind ~= "number" and kind ~= "boolean" then return nil, false end
		return value, true
	end
	if getmetatable(value) ~= nil then return nil, false end
	seen = seen or {}
	if seen[value] then return nil, false end
	seen[value] = true
	local result = {}
	for key, item in pairs(value) do
		if type(key) ~= "string" and type(key) ~= "number" then return nil, false end
		local cloned, ok = copy(item, seen)
		if not ok then return nil, false end
		result[key] = cloned
	end
	seen[value] = nil
	return result, true
end

function CD1C203EventLog:Init()
	self.entries = {}
	self.seq = 0
	self.orderLinks = {}
	self.lastClock = nil
end

-- Append one entry. clock: explicit string/number from caller. etype: string.
-- actorRef: entity number or nil. payload: table or nil.
-- Returns seq on success, nil + reason on rejection.
function CD1C203EventLog:Append(clock, etype, actorRef, payload)
	if type(clock) ~= "number" or clock ~= clock or clock < 0 or clock == math.huge
		or (self.lastClock ~= nil and clock < self.lastClock) then return nil, "bad-clock" end
	if type(etype) ~= "string" or etype == "" then
		return nil, "bad-type"
	end
	if actorRef ~= nil and type(actorRef) ~= "number" then
		return nil, "bad-actor"
	end
	local owned, ok = copy(payload)
	if not ok then return nil, "bad-payload" end
	self.lastClock = clock
	self.seq = self.seq + 1
	local entry = {
		seq = self.seq,
		clock = clock,
		type = etype,
		actorRef = actorRef,
		payload = owned,
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
		out[#out + 1] = copy(self.entries[seq])
	end
	return out
end

function CD1C203EventLog:Get(seq)
	return copy(self.entries[seq])
end
