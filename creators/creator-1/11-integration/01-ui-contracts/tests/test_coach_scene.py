"""Execute production scene wrapper with actual modules and engine stubs."""
from pathlib import Path
import importlib.util
import unittest
try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime=None
C1=Path(__file__).resolve().parents[3]
WRAPPER=C1/'11-integration/01-ui-contracts/src/scripts/vscripts/coach_scene_game_mode.lua'
ADAPTER_TEST=C1/'04-intervention/01-manual-actions/tests/test_manual_move_adapter.py'
@unittest.skipIf(LuaRuntime is None,'optional_lua51_runtime_unavailable')
class CoachSceneTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(WRAPPER.is_file(),'production scene wrapper missing')
        spec=importlib.util.spec_from_file_location('owned_manual_adapter_test',ADAPTER_TEST)
        test_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(test_module)
        harness=test_module.AdapterTests();harness.setUp();self.lua=harness.lua
        paths={'observation':'03-ai-baseline/01-observation','synthetic_policy':'03-ai-baseline/02-synthetic-policy','order_arbiter':'03-ai-baseline/03-order-arbiter','event_log':'02-runtime/03-time-events','roster_confirmation':'07-coach-preparation/01-roster-roles'}
        sources={name:(C1/path/'src/scripts/vscripts'/f'{name}.lua').read_text(encoding='utf-8') for name,path in paths.items()}
        self.lua.globals().module_sources=self.lua.table_from(sources)
        self.lua.execute('''
        function class(t)return t end
        package.loaded.manual_move_game_mode=native_module
        for name in pairs(module_sources)do
          local selected=name;package.preload[selected]=function()return assert(loadstring(module_sources[selected]))()end
        end
        listeners={};channels={}
        function CustomGameEventManager:RegisterListener(name,f)
          listeners[name]=f;if name=='dota_coach_manual_request'then listener=f end
        end
        function CustomGameEventManager:Send_ServerToPlayer(player,name,s)
          assert(player==PlayerResource:GetPlayer(3));channels[#channels+1]={name=name,state=s};emits[#emits+1]=s
        end
        ''')
        self.lua.globals().scene=self.lua.execute(WRAPPER.read_text(encoding='utf-8'))
    def check(self,s):self.lua.execute(s)
    def test_actual_policy_arbiter_journal_through_native_move(self):
        self.check('''
        Activate();sync();think();assert(#orders==1 and orders[1].Position.x==300)
        local s=emits[#emits];assert(s.mode=='AI')
        local journal=scene.journal_snapshot();assert(#journal>=2)
        assert(journal[#journal].clock==100 and journal[#journal].payload.mode=='AI')
        journal[#journal].payload.mode='spoof';assert(scene.journal_snapshot()[#journal].payload.mode=='AI')
        now=101;think();assert(#orders==2 and orders[2].Position.x==-300)
        ''')
    def test_roster_exact_wire_original_sender_guard_and_metadata(self):
        self.check('''
        Activate();local listener=listeners.dota_coach_roster_request
        local inspections=0;local watched={protocol_version=1,request_id='foreign',PlayerID=3}
        local old=rawget;rawget=function(t,k)if t==watched then inspections=inspections+1 end;return old(t,k)end
        listener(2,watched);rawget=old;assert(inspections==0 and #channels==0)
        local input={protocol_version=1,request_id='roster',PlayerID=3};listener(1,input)
        local s=channels[#channels].state;assert(s.status=='confirmed' and s.synthetic==1 and input.PlayerID==3)
        local n=0;for _ in pairs(s)do n=n+1 end;assert(n==8 and s.assignments['2'].warning=='weak-coverage')
        local first=s.revision;listener(1,{protocol_version=1,request_id='mismatch',PlayerID=4})
        s=channels[#channels].state;assert(s.reason=='invalid_request' and s.status=='rejected' and next(s.assignments)==nil and s.revision>first)
        listener(1,{protocol_version=2,request_id='unsupported'});assert(channels[#channels].state.reason=='unsupported_version')
        ''')
    def test_replaced_original_player_handle_cannot_take_roster_session(self):
        self.check('''
        Activate();listeners.dota_coach_roster_request(1,{protocol_version=1,request_id='first'})
        local n=#channels
        local replacement={GetPlayerID=function()return 3 end}
        function PlayerResource:GetPlayer(id)return replacement end
        EntIndexToHScript=function()return replacement end
        listeners.dota_coach_roster_request(1,{protocol_version=1,request_id='second'})
        assert(#channels==n)
        ''')
    def test_register_once_and_snapshot_hook_preserves_manual_priority(self):
        self.check('''
        Activate();Activate();sync();think();local s=emits[#emits]
        listener(1,{protocol_version=1,request_id='grant',kind='acquire',session_id=s.session_id,actor_id=s.actor_id,generation=s.generation,epoch=s.epoch})
        local n=#orders;now=102;think();assert(#orders==n)
        local j=scene.journal_snapshot();local found=false
        for _,e in ipairs(j)do if e.mode=='MANUAL'then found=true end end;assert(found)
        ''')
@unittest.skipIf(LuaRuntime is None,'optional_lua51_runtime_unavailable')
class CoachFixtureTests(unittest.TestCase):
    def setUp(self):
        source=C1/'02-runtime/03-time-events/tests/01-native-lifecycle/coach_scene_fixture.lua'
        self.assertTrue(source.is_file(),'TEST lifecycle fixture missing')
        harness=CoachSceneTests();harness.setUp();self.lua=harness.lua
        self.lua.execute('''
        package.loaded.coach_scene_game_mode=scene
        live=true;kill_calls=0;respawn_calls=0;pause_calls=0
        function h:IsAlive()return live end
        function h:ForceKill(b)assert(b==false);kill_calls=kill_calls+1;live=false end
        function h:RespawnHero(a,b)assert(a==false and b==false);respawn_calls=respawn_calls+1;live=true end
        PauseGame=function(value)pause_calls=pause_calls+1;paused_flag=value end
        ''')
        self.lua.execute(source.read_text(encoding='utf-8'))
    def test_caps_then_pause_unpause_kill_respawn_exact_owned_reply(self):
        self.lua.execute('''
        Activate();local f=listeners.dota_coach_scene_test
        f(1,{protocol_version=1,request_id='caps',kind='caps',PlayerID=3})
        local s=channels[#channels].state;local n=0;for _ in pairs(s)do n=n+1 end
        assert(n==13 and s.cap_pause==1 and s.cap_kill==1 and s.cap_respawn==1)
        assert(pause_calls==0 and kill_calls==0 and respawn_calls==0)
        f(1,{protocol_version=1,request_id='pause',kind='pause'});assert(channels[#channels].state.paused==1)
        f(1,{protocol_version=1,request_id='kill_paused',kind='kill'});assert(kill_calls==0)
        f(1,{protocol_version=1,request_id='unpause',kind='unpause'})
        f(1,{protocol_version=1,request_id='kill',kind='kill'});assert(channels[#channels].state.alive==0 and kill_calls==1)
        f(1,{protocol_version=1,request_id='respawn',kind='respawn'});assert(channels[#channels].state.alive==1 and respawn_calls==1)
        ''')
    def test_unknown_sender_extra_fields_and_absent_capability_have_no_effect(self):
        self.lua.execute('''
        Activate();local f=listeners.dota_coach_scene_test
        local watched={protocol_version=1,request_id='foreign',kind='kill'};local reads=0;local old=rawget
        rawget=function(t,k)if t==watched then reads=reads+1 end;return old(t,k)end
        f(2,watched);rawget=old;assert(reads==0 and #channels==0)
        f(1,{protocol_version=1,request_id='bad',kind='kill',PlayerID=999})
        assert(channels[#channels].state.reason=='invalid_request' and kill_calls==0)
        PauseGame=nil;f(1,{protocol_version=1,request_id='none',kind='pause'})
        assert(channels[#channels].state.status=='unsupported' and pause_calls==0)
        ''')
    def test_replaced_hero_and_player_do_not_inherit_test_authority(self):
        self.lua.execute('''
        Activate();local f=listeners.dota_coach_scene_test
        f(1,{protocol_version=1,request_id='pin',kind='caps'});local n=#channels
        local old=h;h=setmetatable({}, {__index=old})
        local reads=0;local watched={protocol_version=1,request_id='replacement',kind='kill'}
        local original=rawget;rawget=function(t,k)if t==watched then reads=reads+1 end;return original(t,k)end
        f(1,watched);assert(#channels==n and reads==0 and kill_calls==0)
        h=old;local p={GetPlayerID=function()return 3 end}
        function PlayerResource:GetPlayer(id)return p end;EntIndexToHScript=function()return p end
        f(1,watched);rawget=original;assert(#channels==n and reads==0 and kill_calls==0)
        ''')
    def test_strict_shape_version_and_missing_effects(self):
        self.lua.execute('''
        Activate();local f=listeners.dota_coach_scene_test
        for _,v in ipairs({0,true,0/0,math.huge,1.5,'1'})do
          f(1,{protocol_version=v,request_id='bad',kind='kill'});assert(channels[#channels].state.reason=='invalid_request')
        end
        f(1,{protocol_version=2,request_id='version',kind='kill'});assert(channels[#channels].state.reason=='unsupported_version')
        f(1,setmetatable({protocol_version=1,request_id='meta',kind='kill'}, {__index=function()error('DTO getter')end}))
        assert(channels[#channels].state.reason=='invalid_request')
        f(1,{protocol_version=1,request_id='extra',kind='kill',extra=true});assert(kill_calls==0)
        h.ForceKill=nil;h.RespawnHero=nil
        f(1,{protocol_version=1,request_id='kill',kind='kill'});assert(channels[#channels].state.status=='unsupported')
        live=false;f(1,{protocol_version=1,request_id='respawn',kind='respawn'});assert(channels[#channels].state.status=='unsupported')
        assert(kill_calls==0 and respawn_calls==0 and pause_calls==0)
        ''')
    def test_report_reads_both_clocks_and_native_failure_is_explicit(self):
        self.lua.execute('''
        local registrations=0;local original=CustomGameEventManager.RegisterListener
        function CustomGameEventManager:RegisterListener(n,f)
          if n=='dota_coach_scene_test'then registrations=registrations+1 end;original(self,n,f)
        end
        Activate();Activate();assert(registrations==1)
        local f=listeners.dota_coach_scene_test
        now=101;Time=function()return 901 end
        local input={protocol_version=1,request_id='report',kind='report',PlayerID=3}
        f(1,input);local s=channels[#channels].state
        assert(input.PlayerID==3 and s.game_time==101 and s.wall_time==901 and s.kind=='report')
        assert(channels[#channels].name=='dota_coach_scene_test_state' and pause_calls==0 and kill_calls==0)
        PauseGame=function()error('native failure')end
        f(1,{protocol_version=1,request_id='pause',kind='pause'})
        assert(channels[#channels].state.status=='rejected' and channels[#channels].state.reason=='native_effect_failed')
        ''')
if __name__=='__main__':unittest.main()
