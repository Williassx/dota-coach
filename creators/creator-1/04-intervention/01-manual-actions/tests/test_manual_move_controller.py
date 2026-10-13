"""Actual optional Lua51 controller/adapter tests, not native gameplay proof."""
from pathlib import Path
import unittest

try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime = None

SOURCE = Path(__file__).resolve().parents[1] / 'src/scripts/vscripts'


@unittest.skipIf(LuaRuntime is None, 'optional_lua51_runtime_unavailable')
class ManualMoveTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((SOURCE / 'manual_move_controller.lua').is_file(), 'controller missing')
        self.assertTrue((SOURCE / 'manual_move_game_mode.lua').is_file(), 'adapter missing')
        self.lua = LuaRuntime(unpack_returned_tuples=True, register_eval=False, register_builtins=False)
        self.lua.globals().M = self.lua.execute((SOURCE / 'manual_move_controller.lua').read_text(encoding='utf-8'))
        self.lua.execute('''
        now=100; paused=false; connected=true; moves=0; stops=0; ais=0; emits={}
        move_ok=true; stop_ok=true; ai_ok=true; position_ok=true
        obs={entity_index=42,generation=1,alive=true,x=0,y=0,z=0,valid=true}
        ports={owner=3,session_id='TEST_session',actor_id='TEST_actor',
          clock=function() return now end,paused=function() return paused end,
          connected=function() return connected end,observe=function() return obs end,
          move=function(x,y,z) moves=moves+1; return move_ok end,
          stop=function() stops=stops+1; return stop_ok end,
          ai=function(o) ais=ais+1; assert(o==obs); return ai_ok end,
          valid_position=function(x,y,z,o) assert(o==obs); return position_ok end,
          emit=function(sender,s) assert(sender==3); emits[#emits+1]=s end}
        C=M.new(ports)
        function state() return C:snapshot(3,'','none','none','state') end
        function request(kind,id)
          local s=state()
          if kind=='sync' then return {protocol_version=1,request_id=id,kind=kind} end
          return {protocol_version=1,request_id=id,kind=kind,session_id=s.session_id,
            actor_id=s.actor_id,generation=s.generation,epoch=s.epoch}
        end
        function ready() C:tick(); assert(state().mode=='AI') end
        function grant(id) C:handle(3,request('acquire',id or 'grant')); assert(state().mode=='MANUAL') end
        function moving(id,x,y)
          local r=request('move',id or 'move'); r.x=x or 500; r.y=y or 0; r.z=0
          return C:handle(3,r)
        end
        ''')

    def check(self, code):
        self.lua.execute(code)

    def test_start_inactive_requires_actual_ai_success_and_exact_snapshot(self):
        self.check('''
        assert(state().mode=='INACTIVE' and ais==0)
        ready(); local s=state(); assert(s.alive and s.entity_index==42 and s.ai_order_count==1)
        local n=0; for _ in pairs(s) do n=n+1 end; assert(n==17)
        assert(s.protocol_version==1 and s.remaining==0 and s.server_time==100)
        assert(s.request_status=='none' and s.request_id=='')
        ''')

    def test_acquire_stops_ai_and_grants_fixed_five_seconds(self):
        self.check('''
        ready(); grant(); local s=state(); assert(stops==1 and s.epoch==1 and s.remaining==5)
        now=102; moving(); assert(moves==1 and state().remaining==3)
        moving('move2',600); assert(moves==2 and state().remaining==3)
        assert(state().manual_order_count==2)
        ''')

    def test_unauthorized_sender_does_not_inspect_or_emit(self):
        self.check('''
        ready(); local count=#emits; local reads=0
        local r=setmetatable({}, {__index=function() reads=reads+1; error('read') end})
        assert(C:handle(4,r)==nil and reads==0 and #emits==count and stops==0)
        assert(C:snapshot(4,'id','accepted','none','state')==nil and #emits==count)
        ''')

    def test_schema_types_unknown_fields_bad_ids_and_nonfinite_positions(self):
        self.check('''
        ready()
        for _,v in ipairs({true,'1',0/0,math.huge,1.5}) do
          local r=request('acquire','bad'); r.generation=v
          assert(C:handle(3,r).reason=='invalid_request')
        end
        local r=request('acquire','extra'); r.PlayerID=3
        assert(C:handle(3,r).reason=='invalid_request')
        r=request('acquire',' version '); assert(C:handle(3,r)==nil)
        r=request('sync','version'); r.protocol_version=2
        assert(C:handle(3,r).reason=='unsupported_version')
        grant(); for _,v in ipairs({0/0,math.huge,'2',true}) do
          r=request('move','badpos'); r.x=v; r.y=0; r.z=0
          assert(C:handle(3,r).reason=='invalid_request')
        end
        assert(moves==0)
        ''')

    def test_session_generation_epoch_actor_preconditions(self):
        self.check('''
        ready()
        local r=request('acquire','stales'); r.session_id='other'
        assert(C:handle(3,r).reason=='stale_session')
        r=request('acquire','staleg'); r.generation=0
        assert(C:handle(3,r).reason=='stale_generation')
        r=request('acquire','stalee'); r.epoch=99
        assert(C:handle(3,r).reason=='stale_epoch')
        r=request('acquire','stalea'); r.actor_id='other'
        assert(C:handle(3,r).reason=='unauthorized' and stops==0)
        ''')

    def test_duplicate_exact_body_has_no_effect_and_conflict_rejects(self):
        self.check('''
        ready(); local r=request('acquire','same'); C:handle(3,r)
        local first=state(); C:handle(3,r); assert(stops==1 and state().epoch==first.epoch)
        r.generation=2; assert(C:handle(3,r).reason=='request_conflict' and stops==1)
        local m=request('move','same_move'); m.x=500;m.y=0;m.z=0
        C:handle(3,m); now=101; C:handle(3,m)
        assert(moves==1 and state().remaining==4)
        ''')

    def test_dedup_limit_never_evicts_and_sync_is_exempt(self):
        self.check('''
        ready()
        for i=1,128 do local r=request('cancel','id_'..i); assert(C:handle(3,r).reason=='not_manual') end
        assert(C:handle(3,request('acquire','overflow')).reason=='dedup_limit')
        assert(C:handle(3,request('sync','sync')).request_status=='accepted')
        assert(C:handle(3,request('cancel','id_1')).reason=='not_manual' and stops==0)
        ''')

    def test_position_bounds_distance_and_native_grid_policy(self):
        self.check('''
        ready();grant()
        for i,p in ipairs({{16001,0,0},{0,-16001,0},{0,0,2049},{2001,0,0}}) do
          local r=request('move','pos_'..i);r.x=p[1];r.y=p[2];r.z=p[3]
          assert(C:handle(3,r).reason=='invalid_position')
        end
        position_ok=false; assert(moving('blocked').reason=='invalid_position')
        position_ok=true; assert(moving('good',1000).transition=='move_issued' and moves==1)
        ''')

    def test_pause_prevents_all_effects_and_lease_uses_game_clock(self):
        self.check('''
        ready();grant(); paused=true; local s=stops;local a=ais
        assert(moving('paused').reason=='paused'); C:tick();C:tick()
        assert(moves==0 and stops==s and ais==a and state().remaining==5)
        paused=false;now=104.9;C:tick();assert(state().mode=='MANUAL')
        now=105;C:tick();assert(state().mode=='AI' and stops==s+1 and ais==a+1)
        ''')

    def test_cancel_emits_terminal_before_fresh_ai_resumption(self):
        self.check('''
        ready();grant(); local wire=request('cancel','cancel'); local n=#emits
        local r=C:handle(3,wire)
        assert(emits[n+1].transition=='cancelled' and emits[n+1].mode=='INACTIVE')
        assert(emits[n+2].transition=='ai_resumed' and r.mode=='AI')
        assert(stops==2 and ais==2 and r.remaining==0)
        ''')

    def test_arrival_and_expiry_issue_stop_then_new_ai(self):
        self.check('''
        ready();grant();moving();obs.x=450;now=101;C:tick()
        assert(state().mode=='AI' and ais==2 and stops==2)
        local arrived=false; for _,s in ipairs(emits) do if s.transition=='arrived' then arrived=true end end
        assert(arrived);grant('again');now=106;C:tick()
        assert(state().mode=='AI' and ais==3 and stops==4)
        ''')

    def test_failed_stop_move_and_ai_fail_closed(self):
        self.check('''
        ready();stop_ok=false
        assert(C:handle(3,request('acquire','badstop')).reason=='engine_failed')
        assert(state().mode=='INACTIVE' and ais==1)
        ''')
        self.setUp()
        self.check('''
        ready();grant();move_ok=false;assert(moving().reason=='engine_failed')
        assert(state().mode=='INACTIVE' and state().manual_order_count==0)
        ''')
        self.setUp()
        self.check('''
        ready();grant();ai_ok=false
        assert(C:handle(3,request('cancel','bad_ai')).reason=='engine_failed')
        assert(state().mode=='INACTIVE' and state().ai_order_count==1)
        ''')

    def test_clock_regression_invalid_clock_fail_closed_without_new_ai(self):
        self.check('''
        ready();grant();now=99;C:tick();local s=state()
        assert(s.mode=='INACTIVE' and s.server_time==100 and ais==1)
        assert(C:handle(3,request('sync','clock')).reason=='clock_regressed')
        ''')
        self.setUp()
        self.check("ready();now=0/0;C:tick();assert(state().mode=='INACTIVE' and ais==1)")

    def test_death_replacement_and_new_generation_cannot_revive_old_lease(self):
        self.check('''
        ready();grant();local old=request('move','old');old.x=500;old.y=0;old.z=0
        obs.alive=false;C:tick();assert(state().mode=='INACTIVE' and ais==1)
        obs.alive=true;C:tick();assert(state().mode=='INACTIVE' and ais==1)
        obs.generation=2;C:tick();assert(state().mode=='INACTIVE')
        C:tick();assert(state().mode=='AI' and ais==2)
        assert(C:handle(3,old).reason=='stale_generation' and moves==0)
        ''')

    def test_replacement_during_stop_prevents_ai_order_for_old_binding(self):
        self.check('''
        ready();grant()
        ports.stop=function() stops=stops+1;obs.generation=2;obs.entity_index=43;return true end
        C:handle(3,request('cancel','race'))
        assert(state().mode=='INACTIVE' and ais==1 and state().generation==2)
        ''')

    def test_periodic_ai_refresh_rate_and_disconnect_close(self):
        self.check('''
        ready();local n=#emits;C:tick();now=100.5;C:tick();assert(ais==1 and #emits==n)
        now=101;C:tick();assert(ais==2 and #emits==n+1)
        grant();connected=false;C:tick();assert(state().mode=='INACTIVE')
        local a=ais;connected=true;C:tick();assert(ais==a)
        C:close();C:tick();assert(ais==a and state().mode=='INACTIVE')
        ''')

    def test_snapshot_revision_increases_and_wrong_sender_has_no_visibility(self):
        self.check('''
        ready();local a=state();local b=state();assert(b.revision==a.revision+1)
        a.mode='spoof';assert(state().mode=='AI')
        assert(C:snapshot(7,'','none','none','state')==nil)
        ''')

    def test_unknown_pause_state_cannot_issue_effects(self):
        self.check('''ready();grant();local a=ais;local m=moves;local s=stops
        ports.paused=function() error('unavailable') end
        assert(moving('unknownpause').reason=='paused'); C:tick()
        assert(ais==a and moves==m and stops==s)''')

    def test_clock_regression_with_unknown_pause_cannot_issue_stop(self):
        self.check('''ready();grant();local a=ais;local s=stops
        ports.paused=function() error('unavailable') end;now=99;C:tick()
        assert(state().mode=='INACTIVE' and ais==a and stops==s)''')

    def test_disconnect_while_paused_stops_old_order_on_resume_without_ai(self):
        self.check('''ready();grant();moving();paused=true;connected=false
        local s=stops;local a=ais;C:tick();assert(stops==s and state().mode=='INACTIVE')
        paused=false;C:tick();assert(stops==s+1 and ais==a)
        C:tick();assert(stops==s+1 and ais==a)''')

    def test_deferred_stop_never_targets_replacement_binding(self):
        self.check('''ready();grant();paused=true;C:close();local s=stops
        obs.generation=2;obs.entity_index=43;paused=false;C:tick()
        assert(stops==s and ais==1 and state().mode=='INACTIVE')''')


if __name__ == '__main__':
    unittest.main()
