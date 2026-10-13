-- C1-02-02: pure actor-binding map (no native calls).
-- Design: creators/creator-1/02-runtime/02-actor-binding/design.md
-- Facts: creators/creator-1/02-runtime/02-actor-binding/notes/actor-binding.md
-- Boundaries: native seat-hero creation and engine ownership APIs are
-- open native questions (r9/r10); this module only tracks the logical triple
-- (project-player-id <-> seat <-> entity) plus the trusted owner value,
-- with explicit revision guards. Orders against a stale revision, a wrong
-- entity, a mismatched owner or a dead binding must be rejected by callers.
-- Death, respawn and reconnect are handled as pure generation steps;
-- the engine half of each event stays an open native item.

if CD1C202Binding == nil then
	CD1C202Binding = class({})
end

function CD1C202Binding:Init()
	self.bindings = {}
	self.revision = 0
end

-- Bind a stable project player id to a seat/entity pair with owner.
-- owner: trusted owner value (number) or nil when not yet established.
-- Returns new revision on success, nil + reason on rejection.
function CD1C202Binding:Bind(projectId, seat, entity, owner)
	if type(projectId) ~= "string" or projectId == "" then
		return nil, "bad-project-id"
	end
	if type(seat) ~= "number" or type(entity) ~= "number" then
		return nil, "bad-seat-or-entity"
	end
	if owner ~= nil and type(owner) ~= "number" then
		return nil, "bad-owner"
	end
	-- One seat/entity serves one project id at a time.
	for pid, b in pairs(self.bindings) do
		if pid ~= projectId and (b.seat == seat or b.entity == entity) then
			return nil, "seat-or-entity-taken"
		end
	end
	self.revision = self.revision + 1
	self.bindings[projectId] = { seat = seat, entity = entity,
		owner = owner, alive = true, revision = self.revision }
	return self.revision
end

-- Resolve the current binding for a project id (nil if none).
function CD1C202Binding:Resolve(projectId)
	return self.bindings[projectId]
end

-- Check whether an order targets the current live binding.
function CD1C202Binding:Accepts(projectId, entity, revision)
	local b = self.bindings[projectId]
	if b == nil then
		return false
	end
	if b.alive ~= true then
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

-- Verify the owner from a trusted event against the binding.
-- A foreign owner or an unknown binding is rejected openly.
function CD1C202Binding:CheckOwner(projectId, trustedOwner)
	local b = self.bindings[projectId]
	if b == nil then
		return false
	end
	if b.owner == nil or trustedOwner == nil then
		return false
	end
	return b.owner == trustedOwner
end

-- Record a death for the bound entity: orders stop until respawn.
function CD1C202Binding:OnDeath(entity)
	for _, b in pairs(self.bindings) do
		if b.entity == entity and b.alive == true then
			b.alive = false
			self.revision = self.revision + 1
			return true
		end
	end
	return false
end

-- Respawn requires an explicit re-bind to the new entity: the old
-- revision never comes back to life.
function CD1C202Binding:OnRespawn(projectId, newEntity, owner)
	local b = self.bindings[projectId]
	if b == nil then
		return nil, "unknown-binding"
	end
	if b.alive == true then
		return nil, "not-dead"
	end
	if type(newEntity) ~= "number" then
		return nil, "bad-entity"
	end
	for pid, other in pairs(self.bindings) do
		if pid ~= projectId and other.entity == newEntity then
			return nil, "seat-or-entity-taken"
		end
	end
	self.revision = self.revision + 1
	b.entity = newEntity
	b.owner = owner
	b.alive = true
	b.revision = self.revision
	return self.revision
end

-- Reconnect revalidates the seat: a moved seat is a foreign assignment.
function CD1C202Binding:OnReconnect(projectId, seat)
	local b = self.bindings[projectId]
	if b == nil then
		return nil, "unknown-binding"
	end
	if b.seat ~= seat then
		return nil, "seat-moved"
	end
	return true
end

-- Drop a binding (replace path clears first).
-- Returns true if something was removed.
function CD1C202Binding:Unbind(projectId)
	if self.bindings[projectId] == nil then
		return false
	end
	self.bindings[projectId] = nil
	self.revision = self.revision + 1
	return true
end
