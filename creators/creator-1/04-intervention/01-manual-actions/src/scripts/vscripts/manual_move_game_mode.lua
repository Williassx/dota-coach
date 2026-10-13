-- Isolated one-hero synthetic scene. No effect on require; native APIs in Activate.
local Controller=require('manual_move_controller')
local registered=false
local controller=nil
local owner,owner_player,hero=nil,nil,nil
local generation=0
local issuing=false
local filter_ready=false
local ai_direction=1
local last_alive=false
local function index(v) return type(v)=='number' and v==v and v>=0 and v<=2147483647 and v%1==0 end
local function observe()
    if PlayerResource:GetPlayer(owner)~=owner_player then return {valid=false} end
    local h=PlayerResource:GetSelectedHeroEntity(owner)
    if h==nil or h:IsNull() or not h:IsRealHero() or h:GetPlayerOwnerID()~=owner
        or h:GetTeamNumber()~=PlayerResource:GetTeam(owner) or not filter_ready then return {valid=false} end
    local live=h:IsAlive()
    if h~=hero or (live and not last_alive) then generation=generation+1;hero=h end
    last_alive=live
    local p=h:GetAbsOrigin()
    return {valid=true,entity_index=h:entindex(),generation=generation,alive=live,x=p.x,y=p.y,z=p.z}
end
local function valid_position(x,y,z)
    local p=Vector(x,y,z)
    return GridNav:IsTraversable(p) and not GridNav:IsBlocked(p)
end
local function order(kind,position)
    local o=observe()
    if not o.valid or not o.alive or GameRules:IsGamePaused() then return false end
    issuing=true
    local ok=pcall(function() ExecuteOrderFromTable({UnitIndex=o.entity_index,OrderType=kind,Position=position,Queue=false}) end)
    issuing=false
    if ok then
        print('DCMOVE order='..tostring(kind)..' entity='..o.entity_index..' generation='..o.generation..' x='..o.x..' y='..o.y..' game='..GameRules:GetGameTime())
    end
    return ok
end
local function stop() return order(DOTA_UNIT_ORDER_STOP,nil) end
local function move(x,y,z)
    if not valid_position(x,y,z) then return false end
    return order(DOTA_UNIT_ORDER_MOVE_TO_POSITION,Vector(x,y,z))
end
local function ai(o)
    local fresh=observe()
    if not fresh.valid or not fresh.alive or fresh.entity_index~=o.entity_index or fresh.generation~=o.generation then return false end
    local offsets={{300*ai_direction,0},{0,300*ai_direction},{-300*ai_direction,0},{0,-300*ai_direction}}
    for _,delta in ipairs(offsets) do
        local x,y=fresh.x+delta[1],fresh.y+delta[2]
        if valid_position(x,y,fresh.z) then ai_direction=-ai_direction;return move(x,y,fresh.z) end
    end
    return false
end
local function sender(source)
    if not index(source) then return nil end
    local ok,player,id=pcall(function()
        local p=EntIndexToHScript(source)
        if p==nil or type(p.GetPlayerID)~='function' then return nil end
        local id=p:GetPlayerID()
        if not index(id) or PlayerResource:GetPlayer(id)~=p then return nil end
        return p,id
    end)
    if not ok or player==nil then return nil end
    return player,id
end
local function emit(id,s)
    local p=PlayerResource:GetPlayer(id)
    if p~=owner_player then return end
    local wire={};for k,v in pairs(s) do wire[k]=v end
    -- Native custom events transported Lua true as numeric1 in runr2.
    wire.alive=s.alive and 1 or 0
    CustomGameEventManager:Send_ServerToPlayer(p,'dota_coach_manual_state',wire)
    print('DCMOVE state mode='..s.mode..' transition='..s.transition..' reason='..s.reason..' generation='..s.generation..' epoch='..s.epoch..' revision='..s.revision..' remaining='..s.remaining..' ai='..s.ai_order_count..' manual='..s.manual_order_count..' game='..s.server_time)
end
local function request(source,payload)
    local player,id=sender(source)
    if not player then print('DCMOVE sender=unverified drop=true');return end
    if controller==nil then
        owner=id;owner_player=player
        local session='native_'..tostring(math.floor(Time()*1000))..'_'..tostring(RandomInt(1,2147483647))
        controller=Controller.new({owner=owner,session_id=session,actor_id='TEST_synthetic_1',
            clock=function() return math.max(0,GameRules:GetGameTime()) end,
            paused=function() return GameRules:IsGamePaused() end,
            connected=function()
                return PlayerResource:GetPlayer(owner)==owner_player
                    and DOTA_CONNECTION_STATE_CONNECTED~=nil
                    and PlayerResource:GetConnectionState(owner)==DOTA_CONNECTION_STATE_CONNECTED
            end,observe=observe,move=move,stop=stop,ai=ai,valid_position=valid_position,emit=emit})
    end
    if id~=owner then return end
    local wire=payload
    if type(payload)=='table' and getmetatable(payload)==nil and rawget(payload,'PlayerID')==id then
        wire={};for k,v in pairs(payload) do if k~='PlayerID' then wire[k]=v end end
    end
    controller:handle(id,wire)
end
function Precache(context) end
function Activate()
    if registered then return end
    local mode=GameRules:GetGameModeEntity()
    -- Scene-local timing only; preserve global/native user preferences.
    GameRules:SetHeroSelectionTime(10)
    GameRules:SetStrategyTime(0)
    GameRules:SetShowcaseTime(0)
    GameRules:SetPreGameTime(3)
    local installed=pcall(function()
        mode:SetExecuteOrderFilter(function(_,data)
            if hero==nil or hero:IsNull() then return true end
            for _,unit in pairs(data.units or {}) do
                if tonumber(unit)==hero:entindex() then return issuing end
            end
            return true
        end,mode)
    end)
    filter_ready=installed
    CustomGameEventManager:RegisterListener('dota_coach_manual_request',request)
    mode:SetThink(function()
        if controller then
            if GameRules:State_Get()>=DOTA_GAMERULES_STATE_POST_GAME then controller:close();return nil end
            if GameRules:State_Get()==DOTA_GAMERULES_STATE_GAME_IN_PROGRESS then controller:tick() end
        end
        return .1
    end,'CoachManualMoveThink',.1)
    registered=true
    print('DCMOVE activated filter='..tostring(filter_ready)..' synthetic=true')
end
