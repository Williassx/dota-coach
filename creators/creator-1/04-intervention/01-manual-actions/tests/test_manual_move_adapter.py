"""Execute native adapter with controlled engine ports; not native input proof."""
from pathlib import Path
import unittest
try:
 from lupa.lua51 import LuaRuntime
except ImportError:
 LuaRuntime=None
SOURCE=Path(__file__).resolve().parents[1]/'src/scripts/vscripts'
@unittest.skipIf(LuaRuntime is None,'optional_lua51_runtime_unavailable')
class AdapterTests(unittest.TestCase):
 def setUp(self):
  self.lua=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False)
  self.lua.globals().actual=self.lua.execute((SOURCE/'manual_move_controller.lua').read_text())
  self.lua.execute('''
  package.preload.manual_move_controller=function()return actual end
  emits={};orders={};now=100;filterfail=false;orderfail=false;state=6;paused_flag=false
  DOTA_GAMERULES_STATE_GAME_IN_PROGRESS=6;DOTA_GAMERULES_STATE_POST_GAME=7
  DOTA_CONNECTION_STATE_CONNECTED=2;DOTA_UNIT_ORDER_MOVE_TO_POSITION=1;DOTA_UNIT_ORDER_STOP=4
  Time=function()return 1 end;RandomInt=function()return 1234 end
  Vector=function(x,y,z)return {x=x,y=y,z=z}end
  local p={};function p:GetPlayerID()return 3 end
  foreign={};function foreign:GetPlayerID()return 4 end
  h={};function h:IsNull()return false end;function h:IsRealHero()return true end
  function h:GetPlayerOwnerID()return 3 end;function h:GetTeamNumber()return 2 end
  function h:IsAlive()return true end;function h:GetAbsOrigin()return {x=0,y=0,z=0}end
  function h:entindex()return 42 end
  PlayerResource={};function PlayerResource:GetPlayer(id)if id==3 then return p end end
  function PlayerResource:GetSelectedHeroEntity(id)return h end
  function PlayerResource:GetTeam(id)return 2 end
  function PlayerResource:GetConnectionState(id)return 2 end
  EntIndexToHScript=function(i)if i==1 then return p elseif i==2 then return foreign end end
  GridNav={};function GridNav:IsTraversable(v)return true end;function GridNav:IsBlocked(v)return false end
  mode={};function mode:SetExecuteOrderFilter(f,c)if filterfail then error('no filter')end filter=f;filterctx=c end
  function mode:SetThink(f,n,t)think=f end
  GameRules={};function GameRules:GetGameModeEntity()return mode end
  function GameRules:GetGameTime()return now end;function GameRules:IsGamePaused()return paused_flag end
  function GameRules:State_Get()return state end
  for _,n in ipairs({'SetHeroSelectionTime','SetStrategyTime','SetShowcaseTime','SetPreGameTime'})do GameRules[n]=function()end end
  CustomGameEventManager={};function CustomGameEventManager:RegisterListener(n,f)listener=f end
  function CustomGameEventManager:Send_ServerToPlayer(player,n,s)assert(player==p);emits[#emits+1]=s end
  ExecuteOrderFromTable=function(o)if orderfail then error('failed')end assert(filter(filterctx,{units={['0']=o.UnitIndex}}));orders[#orders+1]=o end
  function sync(id,extra)local r={protocol_version=1,request_id=id or 'sync',kind='sync'};if extra then r.PlayerID=extra end;listener(1,r)end
  ''')
  self.lua.globals().native_module=self.lua.execute((SOURCE/'manual_move_game_mode.lua').read_text())
 def check(self,s):self.lua.execute(s)
 def test_sender_verified_before_payload_and_matching_metadata_only(self):
  self.check('''Activate(); local reads=0;local bad=setmetatable({}, {__index=function()reads=reads+1;error('read')end})
  listener(2,bad);assert(reads==0 and #emits==0)
  sync('good',3);assert(emits[#emits].request_status=='accepted')
  sync('bad',999);assert(emits[#emits].reason=='invalid_request')''')
 def test_server_hooks_configure_once_before_activate_with_owned_copies(self):
  self.check('''
  local snapshot=nil;local decisions=0
  assert(type(native_module.resolve_sender)=='function')
  assert(native_module.configure_server_hooks({decide_ai=function(o)
    decisions=decisions+1;o.x=99999;return {x=300,y=0,z=0}
  end,on_snapshot=function(s)snapshot=s;s.mode='spoof' end}))
  assert(not native_module.configure_server_hooks({decide_ai=function()end,on_snapshot=function()end}))
  Activate();sync();think();assert(decisions==1 and #orders==1)
  assert(emits[#emits].mode=='AI' and snapshot.mode=='spoof')
  assert(not native_module.configure_server_hooks({decide_ai=function()end,on_snapshot=function()end}))
  ''')
 def test_real_controller_to_adapter_to_filter_sequence(self):
  self.check('''Activate();sync();think();assert(#orders==1 and emits[#emits].mode=='AI')
  assert(not filter(filterctx,{units={['0']=42}}));assert(filter(filterctx,{units={['0']=99}}))
  local s=emits[#emits];listener(1,{protocol_version=1,request_id='acquire',kind='acquire',session_id=s.session_id,actor_id=s.actor_id,generation=s.generation,epoch=s.epoch,PlayerID=3})
  assert(emits[#emits].mode=='MANUAL' and #orders==2 and orders[2].OrderType==4)
  s=emits[#emits];listener(1,{protocol_version=1,request_id='move',kind='move',session_id=s.session_id,actor_id=s.actor_id,generation=s.generation,epoch=s.epoch,x=500,y=0,z=0})
  assert(#orders==3 and orders[3].Position.x==500)
  now=105;think();assert(#orders==5 and emits[#emits].transition=='ai_resumed')''')
 def test_filter_failure_keeps_actor_inactive_and_prevents_orders(self):
  self.check("filterfail=true;Activate();sync();think();assert(#orders==0 and emits[#emits].mode=='INACTIVE')")
 def test_order_failure_restores_scoped_filter_and_closes_effects(self):
  self.check("Activate();sync();orderfail=true;think();assert(#orders==0 and emits[#emits].mode=='INACTIVE');assert(not filter(filterctx,{units={['0']=42}}))")
 def test_deferred_cleanup_cannot_stop_hero_of_replaced_player_handle(self):
  self.check('''Activate();sync();think();local s=emits[#emits]
  listener(1,{protocol_version=1,request_id='acquire',kind='acquire',session_id=s.session_id,actor_id=s.actor_id,generation=s.generation,epoch=s.epoch})
  assert(#orders==2);paused_flag=true
  function PlayerResource:GetPlayer(id)return foreign end
  think();paused_flag=false;think();assert(#orders==2)''')
if __name__=='__main__':unittest.main()
