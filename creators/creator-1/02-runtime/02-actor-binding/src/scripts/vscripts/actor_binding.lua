-- C1-02-02: pure actor-binding map (no native calls).
-- Design: creators/creator-1/02-runtime/02-actor-binding/design.md
-- Facts: creators/creator-1/02-runtime/02-actor-binding/notes/actor-binding.md
-- Boundaries: native seat-hero creation and engine ownership APIs are
-- open native questions (r9/r10); this module only tracks the logical triple
-- (project-player-id <-> seat <-> entity) with explicit revision guards.
-- Orders against a stale revision/entity must be rejected by callers.

if CD1C202Binding == nil then
	CD1C202Binding = class({})
end

function CD1C202Binding:Init()
	self.bindings = {}
	self.revision = 0
end

-- Bind a stable project player id to a seat/entity pair.
-- Returns new revision on success, nil + reason on rejection.
function CD1C202Binding:Bind(projectId, seat, entity)
	if type(projectId) ~= "string" or projectId == "" then
		return nil, "bad-project-id"
	end
	if type(seat) ~= "number" or type(entity) ~= "number" then
		return nil, "bad-seat-or-entity"
	end
	-- One seat/entity serves one project id at a time.
	for pid, b in pairs(self.bindings) do
		if pid ~= projectId and (b.seat == seat or b.entity == entity) then
			return nil, "seat-or-entity-taken"
		end
	end
	self.revision = self.revision + 1
	self.bindings[projectId] = { seat = seat, entity = entity, revision = self.revision }
	return self.revision
end

-- Resolve the current binding for a project id (nil if none).
function CD1C202Binding:Resolve(projectId)
	return self.bindings[projectId]
end

-- Check whether an order targets the current binding.
-- Stale revision or entity mismatch => rejected (true = accepted).
function CD1C202Binding:Accepts(projectId, entity, revision)
	local b = self.bindings[projectId]
	if b == nil then
		return false
	end
	if b.entity ~= entity then
		return false
	end
	if b.revision ~= revision then
		return false
	end
	return true
end

-- Drop a binding (replace/death/reconnect path clears first).
-- Returns true if something was removed.
function CD1C202Binding:Unbind(projectId)
	if self.bindings[projectId] == nil then
		return false
	end
	self.bindings[projectId] = nil
	self.revision = self.revision + 1
	return true
end
