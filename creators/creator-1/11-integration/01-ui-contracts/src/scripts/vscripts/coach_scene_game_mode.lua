-- One TEST hero: actual observation/policy/arbiter/journal plus readonly roster.
require('observation')
require('synthetic_policy')
require('order_arbiter')
require('event_log')
local Native=require('manual_move_game_mode')
local Roster=require('roster_confirmation')
local original_activate=Activate
local registered=false
local current_mode='INACTIVE'
local decision_revision=0
local roster_owner,roster_player,roster_session=nil,nil,nil
local roster_revision=0
local function instance(definition)
 local object=setmetatable({}, {__index=definition});object:Init();return object
end
local observation=instance(CD1C301Observation)
local policy=instance(CD1C302Synthetic)
local arbiter=instance(CD1C303Arbiter)
local journal=instance(CD1C203EventLog)
local function copy(t)
 local out={};for k,v in pairs(t)do out[k]=type(v)=='table' and copy(v) or v end;return out
end
local function decide_ai(o)
 -- Deliberately only our current allowed point; no enemy/hidden/future channel.
 local allowed={x=o.x,y=o.y,z=o.z,entity_index=o.entity_index,generation=o.generation,alive=o.alive}
 local projection=observation:BuildProjection({allowed},observation:FilterVisible({}))
 if projection==nil then return nil end
 local intent=policy:Decide(projection)
 if intent==nil or intent.synthetic~=true or intent.kind~='move' then return nil end
 decision_revision=decision_revision+1
 local command={orderId='TEST_ai_'..decision_revision,source='ai',revision=decision_revision,choice=copy(intent)}
 local admitted=arbiter:Resolve(command,current_mode=='MANUAL')
 if admitted==nil then return nil end
 local seq=journal:Append(math.max(0,GameRules:GetGameTime()),'ai_intent_admitted',o.entity_index,copy(command))
 if seq==nil then return nil end
 journal:LinkOrder(command.orderId,seq)
 print('DCCOACH decision source=ai synthetic=true revision='..decision_revision..' seq='..seq)
 return {x=admitted.choice.position[1],y=admitted.choice.position[2],z=admitted.choice.position[3]}
end
local function on_snapshot(s)
 local owned=copy(s)
 current_mode=owned.mode
 if current_mode=='MANUAL' and owned.request_status=='accepted' then
  decision_revision=decision_revision+1
  local accepted=arbiter:Resolve({orderId='TEST_manual_snapshot_'..owned.revision,source='manual',revision=decision_revision},true)
  assert(accepted~=nil,'manual source admission failed')
 end
 local seq=journal:Append(owned.server_time,owned.transition,owned.entity_index,owned)
 assert(seq~=nil,'server journal rejected snapshot')
 if owned.request_id~='' then journal:LinkOrder(owned.request_id,seq)end
 if current_mode=='AI' or current_mode=='MANUAL' then journal:TagMode(seq,current_mode)end
 print('DCCOACH journal seq='..seq..' game='..owned.server_time..' transition='..owned.transition..' mode='..current_mode)
end
assert(Native.configure_server_hooks({decide_ai=decide_ai,on_snapshot=on_snapshot}),'server hooks unavailable')
local function usable_id(v)
 return type(v)=='string' and #v>=1 and #v<=64 and not v:find('[^A-Za-z0-9_-]')
end
local function roster_request(source,payload)
 local player,id=Native.resolve_sender(source)
 if player==nil then return end -- no DTO access before native source equality
 if roster_player~=nil and (id~=roster_owner or player~=roster_player)then return end
 if type(payload)~='table' or not usable_id(rawget(payload,'request_id'))then return end
 local wire=payload
 if getmetatable(payload)==nil and rawget(payload,'PlayerID')==id then
  wire={};for k,v in pairs(payload)do if k~='PlayerID'then wire[k]=v end end
 end
 local reason='none'
 if getmetatable(wire)~=nil then reason='invalid_request'
 else
  local n=0;for k in pairs(wire)do if k~='request_id' and k~='protocol_version'then reason='invalid_request'end;n=n+1 end
  if n~=2 then reason='invalid_request'
  elseif reason=='none' and wire.protocol_version~=1 then
   local version=wire.protocol_version
   reason=type(version)=='number' and version==version and version>0 and version<math.huge and version%1==0 and 'unsupported_version' or 'invalid_request'
  end
 end
 if roster_player==nil then
  roster_owner=id;roster_player=player
  roster_session='TEST_roster_'..math.floor(Time()*1000)..'_'..RandomInt(1,2147483647)
 end
 local confirmation=nil
 if reason=='none'then confirmation,reason=Roster.confirm(Roster.default_assignments(),Roster.server_profiles())end
 if roster_revision>=2147483647 then return end
 roster_revision=roster_revision+1
 local wire_reply={protocol_version=1,request_id=rawget(payload,'request_id'),session_id=roster_session,
  revision=roster_revision,status=confirmation and 'confirmed' or 'rejected',reason=reason,
  synthetic=1,assignments=confirmation and copy(confirmation.assignments) or {}}
 if PlayerResource:GetPlayer(roster_owner)~=roster_player then return end
 CustomGameEventManager:Send_ServerToPlayer(roster_player,'dota_coach_roster_state',wire_reply)
 print('DCCOACH roster status='..wire_reply.status..' revision='..roster_revision..' reason='..reason..' synthetic=1')
end
function Activate()
 if registered then return end
 original_activate()
 CustomGameEventManager:RegisterListener('dota_coach_roster_request',roster_request)
 registered=true
end
local function journal_snapshot()
 local out={};for seq=1,journal:Count()do out[seq]=journal:Get(seq)end;return out
end
return {resolve_sender=Native.resolve_sender,journal_snapshot=journal_snapshot}
