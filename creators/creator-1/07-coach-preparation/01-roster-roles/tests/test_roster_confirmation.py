"""Production TEST roster validator via optional actual Lua51."""
from pathlib import Path
import unittest
try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime=None
SOURCE=Path(__file__).resolve().parents[1]/'src/scripts/vscripts/roster_confirmation.lua'
@unittest.skipIf(LuaRuntime is None,'optional_lua51_runtime_unavailable')
class RosterConfirmationTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SOURCE.is_file(),'production roster module missing')
        self.lua=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False)
        self.lua.globals().R=self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute('a=R.default_assignments();p=R.server_profiles()')
    def check(self,s):self.lua.execute(s)
    def test_exact_five_string_slots_and_weak_coverage(self):
        self.check("local c,w=R.confirm(a,p);assert(c and w=='none' and c.synthetic==1);assert(c.assignments['2'].warning=='weak-coverage');local n=0;for k,e in pairs(c.assignments)do n=n+1;assert(type(k)=='string');local m=0;for _ in pairs(e)do m=m+1 end;assert(m==5)end;assert(n==5)")
    def test_count_duplicates_role_and_hero_compatibility(self):
        for mutate in ("a[5]=nil", "a[5].projectId=a[1].projectId", "a[5].role=a[1].role", "a[1].hero='npc_dota_hero_axe'", "a.extra=true"):
            self.setUp();self.check(mutate+";assert(R.confirm(a,p)==nil)")
    def test_bool_nan_malformed_and_nonsynthetic_profiles_refused(self):
        for mutate in ("a[1].role=true", "a[1].role=0/0", "a[1]='bad'", "a[1].extra=true", "p[a[1].projectId].coverage=0/0", "p[a[1].projectId].coverage=true", "p[a[1].projectId].synthetic=false", "p[a[1].projectId].coverage=2", "p.extra={}"):
            self.setUp();self.check(mutate+";assert(R.confirm(a,p)==nil)")
    def test_defaults_and_confirmed_records_are_owned_copies(self):
        self.check("local c=R.confirm(a,p);c.assignments['1'].hero='spoof';a[1].hero='spoof';p['TEST-player-001'].coverage=0;assert(R.default_assignments()[1].hero~='spoof');assert(R.server_profiles()['TEST-player-001'].coverage==0.8)")
    def test_metatable_dto_never_calls_getters(self):
        self.check("local reads=0;local bad=setmetatable({}, {__index=function()reads=reads+1;error('read')end});assert(R.confirm(bad,p)==nil and reads==0);a[1]=bad;assert(R.confirm(a,p)==nil and reads==0)")
