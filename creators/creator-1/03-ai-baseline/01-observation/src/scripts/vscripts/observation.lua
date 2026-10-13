-- C1-03-01: pure observation projection (no native calls).
-- Allowed knowledge only: own units plus currently visible targets.
-- Hidden positions and future events never enter the projection; callers
-- must filter before constructing entries, and this module drops anything
-- flagged hidden or future defensively.
-- Choice is a pure function of (projection, seed): the same allowed
-- observation and seed always yield the same choice; hidden state cannot
-- influence it because it is never stored.

if CD1C301Observation == nil then
	CD1C301Observation = class({})
end

function CD1C301Observation:Init()
	self.revision = 0
end

-- Keep only entries that are explicitly visible now.
-- Each candidate: {id=number, visible=boolean, hidden=boolean?, future=boolean?}.
-- Returns the kept list; hidden or future entries are dropped.
function CD1C301Observation:FilterVisible(candidates)
	local kept = {}
	if type(candidates) ~= "table" then
		return kept
	end
	for _, c in ipairs(candidates) do
		if type(c) == "table" and c.visible == true
			and c.hidden ~= true and c.future ~= true then
			kept[#kept + 1] = c
		end
	end
	return kept
end

-- Build one projection revision from own units and pre-filtered visible targets.
-- Returns the projection table, or nil + reason on bad input.
function CD1C301Observation:BuildProjection(ownUnits, visibleTargets)
	if type(ownUnits) ~= "table" or type(visibleTargets) ~= "table" then
		return nil, "bad-input"
	end
	for _, t in ipairs(visibleTargets) do
		if type(t) ~= "table" or t.visible ~= true
			or t.hidden == true or t.future == true then
			return nil, "forbidden-target"
		end
	end
	self.revision = self.revision + 1
	return { own = ownUnits, visible = visibleTargets, revision = self.revision }
end

-- Deterministic choice from a projection and a numeric seed.
-- Returns target id, or nil when no visible target exists.
function CD1C301Observation:Choose(projection, seed)
	if type(projection) ~= "table" or type(projection.visible) ~= "table" then
		return nil
	end
	if #projection.visible == 0 or type(seed) ~= "number" then
		return nil
	end
	local index = (math.floor(math.abs(seed)) % #projection.visible) + 1
	return projection.visible[index].id
end
