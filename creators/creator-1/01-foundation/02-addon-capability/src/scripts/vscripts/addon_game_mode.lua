-- C1-01-02 probe: minimal server scene, one standard hero, move/attack orders.
-- Design: creators/creator-1/01-foundation/02-addon-capability/design.md
-- Static checks: creators/creator-1/01-foundation/02-addon-capability/tests/
-- Boundaries: server-only facts; UI is C2-01-02, order contract is C1-01-03.
-- r2: periodic target health logging to confirm the attack fact in the log.

if CD1C102GameMode == nil then
	CD1C102GameMode = class({})
end

-- One standard engine hero, no content files.
local HERO_NAME = "npc_dota_hero_sniper"

-- Fixed close-spawn locations (radiant sanctuary area of the template map).
local HERO_SPAWN = Vector(-600, -400, 0)
local TARGET_SPAWN = Vector(-400, -600, 0)

-- Only these two order types are used in this probe (see tests).
local ORDERS = {
	MOVE = DOTA_UNIT_ORDER_MOVE_TO_POSITION,
	ATTACK = DOTA_UNIT_ORDER_ATTACK_TARGET,
}

function Precache( context )
	-- The probe uses only engine-provided hero units; nothing to precache.
	print( "D1C102 precache (no custom resources)" )
end

function Activate()
	GameRules.D1C102 = CD1C102GameMode()
	GameRules.D1C102:InitGameMode()
end

function CD1C102GameMode:InitGameMode()
	self.heroIndex = nil
	self.targetIndex = nil
	self.lastPosX = nil
	self.lastPosY = nil
	self.tick = 0
	print( "D1C102 activated" )
	GameRules:GetGameModeEntity():SetThink( "OnThink", self, "D1C102Think", 1 )
end

-- Evaluate the state of the probe units.
function CD1C102GameMode:OnThink()
	if GameRules:State_Get() == DOTA_GAMERULES_STATE_GAME_IN_PROGRESS then
		if self.heroIndex == nil then
			self:CreateUnits()
		else
			self:Observe()
		end
	elseif GameRules:State_Get() >= DOTA_GAMERULES_STATE_POST_GAME then
		return nil
	end
	return 1
end

function CD1C102GameMode:CreateUnits()
	-- Single standard hero (server-owned, no player yet) and its attack target.
	self.heroIndex = CreateUnitByName(
		HERO_NAME, HERO_SPAWN, true, nil, nil, DOTA_TEAM_GOODGUYS )
	self.targetIndex = CreateUnitByName(
		HERO_NAME, TARGET_SPAWN, true, nil, nil, DOTA_TEAM_BADGUYS )
	print( "D1C102 created hero=", self.heroIndex, "target=", self.targetIndex )
	print( "D1C102 identity hero=", self.heroIndex:GetUnitName(),
		"target=", self.targetIndex:GetUnitName() )
	-- r4: r3 fact — SetControllableByPlayer alone did not change owner (-1 → -1).
	-- Assign ownership through the player entity, then log both checks.
	print( "D1C102 control owner-before=", self.heroIndex:GetPlayerOwnerID() )
	local hPlayer = PlayerResource:GetPlayer( 0 )
	if hPlayer == nil then
		print( "D1C102 control player-missing seat=0" )
	else
		self.heroIndex:SetOwner( hPlayer )
		self.heroIndex:SetControllableByPlayer( 0, true )
	end
	print( "D1C102 control owner-after=", self.heroIndex:GetPlayerOwnerID() )
	self:OrderMove()
end

function CD1C102GameMode:OrderMove()
	ExecuteOrderFromTable( {
		UnitIndex = self.heroIndex,
		OrderType = ORDERS.MOVE,
		Position = HERO_SPAWN + Vector( 200, 200, 0 ),
		Queue = false,
	} )
	print( "D1C102 order move issued to", self.heroIndex )
end

function CD1C102GameMode:OrderAttack()
	ExecuteOrderFromTable( {
		UnitIndex = self.heroIndex,
		OrderType = ORDERS.ATTACK,
		TargetIndex = self.targetIndex,
		Queue = false,
	} )
	print( "D1C102 order attack issued to", self.heroIndex )
end

function CD1C102GameMode:Observe()
	local origin = self.heroIndex:GetAbsOrigin()
	self.tick = self.tick + 1
	-- Position and health fact every 5 ticks: proves move execution and
	-- damage from the attack order (or not). No spam every tick.
	if self.tick % 5 == 0 then
		print( "D1C102 state origin=", origin.x, origin.y, origin.z,
			"lastPosX=", self.lastPosX, "tick=", self.tick )
		local hAttackTarget = self.heroIndex:GetAttackTarget()
		print( "D1C102 health target=", self.targetIndex:GetHealth(),
			"max=", self.targetIndex:GetMaxHealth(),
			"heroAttacking=", self.heroIndex:IsAttacking(),
			"heroAttackTarget=", hAttackTarget and hAttackTarget == self.targetIndex,
			"range=", self.heroIndex:GetRangeToUnit( self.targetIndex ) )
	end
	-- One-time attack order after an observed movement tick; only the two
	-- allowed order types, no repeat spam and no unit recreation.
	if self.lastPosX ~= nil and origin.x ~= self.lastPosX then
		self:OrderAttack()
	end
	self.lastPosX = origin.x
	self.lastPosY = origin.y
end
