-- TEST recipe only. No listener/effect until explicit Activate.
local Scene=require('coach_scene_game_mode')
local original_activate=Activate
local registered=false
local owner_id,owner_player,owner_hero=nil,nil,nil
local kinds={caps=true,report=true,pause=true,unpause=true,kill=true,respawn=true}
local function flag(v)return v and 1 or 0 end
local function usable_id(v)
 return type(v)=='string' and #v>=1 and #v<=64 and not v:find('[^A-Za-z0-9_-]')
end
local function owned(player,id,hero)
 return PlayerResource:GetPlayer(id)==player and PlayerResource:GetSelectedHeroEntity(id)==hero
  and hero~=nil and not hero:IsNull() and hero:IsRealHero() and hero:GetPlayerOwnerID()==id
  and hero:GetTeamNumber()==PlayerResource:GetTeam(id)
end
local function request(source,payload)
 local player,id=Scene.resolve_sender(source)
 if player==nil then return end -- original native sender before any DTO read
 if owner_player~=nil and (player~=owner_player or id~=owner_id)then return end
 local hero=PlayerResource:GetSelectedHeroEntity(id)
 if not owned(player,id,hero)then return end
 if owner_hero~=nil and hero~=owner_hero then return end
 if type(payload)~='table' or not usable_id(rawget(payload,'request_id'))then return end
 local wire=payload
 if getmetatable(payload)==nil and rawget(payload,'PlayerID')==id then
  wire={};for k,v in pairs(payload)do if k~='PlayerID'then wire[k]=v end end
 end
 local status,reason='ok','none'
 local kind=rawget(wire,'kind')
 if getmetatable(wire)~=nil then status,reason='rejected','invalid_request'
 else
  local n=0;for k in pairs(wire)do
   n=n+1;if k~='protocol_version' and k~='request_id' and k~='kind'then status,reason='rejected','invalid_request'end
  end
  if n~=3 or type(kind)~='string' or not kinds[kind]then status,reason='rejected','invalid_request'
  elseif status=='ok' and rawget(wire,'protocol_version')~=1 then
   local v=rawget(wire,'protocol_version')
   status,reason='rejected',(type(v)=='number' and v==v and v>0 and v<math.huge and v%1==0)and 'unsupported_version' or 'invalid_request'
  end
 end
 -- Capability inspection precedes all mutating calls; no speculative effects.
 local pause=type(PauseGame)=='function'
 local kill=type(hero.ForceKill)=='function'
 local respawn=type(hero.RespawnHero)=='function'
 if status=='ok' then
  owner_id,owner_player,owner_hero=id,player,hero
  local action=nil
  if kind=='pause' or kind=='unpause'then
   if not pause then status,reason='unsupported','capability_unavailable'
   else action=function()PauseGame(kind=='pause')end end
  elseif kind=='kill' or kind=='respawn'then
   if (kind=='kill' and not kill)or(kind=='respawn' and not respawn)then status,reason='unsupported','capability_unavailable'
   elseif GameRules:IsGamePaused()then status,reason='rejected','paused'
   elseif kind=='kill' and not hero:IsAlive()then status,reason='rejected','already_dead'
   elseif kind=='respawn' and hero:IsAlive()then status,reason='rejected','already_alive'
   elseif kind=='kill'then action=function()hero:ForceKill(false)end
   else action=function()hero:RespawnHero(false,false)end end
  end
  if action~=nil then
   if not owned(player,id,hero)then return end
   local ok=pcall(action);if not ok then status,reason='rejected','native_effect_failed'end
  end
 end
 if not owned(player,id,hero)then return end
 local reply={protocol_version=1,request_id=rawget(payload,'request_id'),kind=type(kind)=='string' and kind or '',
  status=status,reason=reason,game_time=GameRules:GetGameTime(),wall_time=Time(),
  paused=flag(GameRules:IsGamePaused()),alive=flag(hero:IsAlive()),entity_index=hero:entindex(),
  cap_pause=flag(pause),cap_kill=flag(kill),cap_respawn=flag(respawn)}
 CustomGameEventManager:Send_ServerToPlayer(player,'dota_coach_scene_test_state',reply)
 print('DCCOACH TEST lifecycle kind='..reply.kind..' status='..status..' reason='..reason..' game='..reply.game_time..' wall='..reply.wall_time)
end
function Activate()
 if registered then return end
 original_activate()
 CustomGameEventManager:RegisterListener('dota_coach_scene_test',request)
 registered=true
end
