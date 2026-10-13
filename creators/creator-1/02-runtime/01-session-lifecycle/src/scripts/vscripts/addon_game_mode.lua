-- C1-02-01: server session lifecycle (single activation, clean stop).
-- Design: creators/creator-1/02-runtime/01-session-lifecycle/design.md
-- Facts: creators/creator-1/02-runtime/01-session-lifecycle/notes/lifecycle.md
-- Boundaries: no player-ownership logic (open item of C1-01-03);
--             no unit cache; no timers beyond the single state Think.

if CD1C201Lifecycle == nil then
	CD1C201Lifecycle = class({})
end

function Precache( context )
	print( "D1C201 precache (no custom resources)" )
end

function Activate()
	if _G.D1C201_ACTIVE == true then
		print( "D1C201 double-activate ignored" )
		return
	end
	_G.D1C201_ACTIVE = true
	GameRules.D1C201 = CD1C201Lifecycle()
	GameRules.D1C201:InitGameMode()
end

function CD1C201Lifecycle:InitGameMode()
	self.phaseSeen = {}
	self.stopped = false
	print( "D1C201 activated" )
	-- Exactly one Think registration per process (see static tests).
	GameRules:GetGameModeEntity():SetThink( "OnThink", self, "D1C201Think", 1 )
end

function CD1C201Lifecycle:OnThink()
	local state = GameRules:State_Get()
	if self.stopped then
		-- After the stop decision no further ticks are allowed.
		print( "D1C201 tick-after-stop" )
		return nil
	end
	-- One log entry per rules-state at most.
	if self.phaseSeen[state] ~= true and state ~= DOTA_GAMERULES_STATE_GAME_IN_PROGRESS then
		self.phaseSeen[state] = true
		print( "D1C201 phase ", state )
	end
	if state == DOTA_GAMERULES_STATE_POST_GAME then
		print( "D1C201 stop" )
		self.stopped = true
		return nil
	end
	return 1
end
