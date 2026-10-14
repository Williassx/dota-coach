"""Actual journal copies/clock guards; no native clock proof."""
from pathlib import Path
import unittest
try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime=None
SOURCE=Path(__file__).resolve().parents[1]/'src/scripts/vscripts/event_log.lua'
@unittest.skipIf(LuaRuntime is None,'optional_lua51_runtime_unavailable')
class EventExecutionTests(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(register_eval=False,register_builtins=False)
        self.lua.execute('function class(t)return t end')
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute('j=setmetatable({}, {__index=CD1C203EventLog});j:Init()')
    def test_owned_records_cannot_be_mutated_via_input_or_read(self):
        self.lua.execute('''
        local input={nested={value=7}};local seq=j:Append(100,'move_issued',42,input)
        input.nested.value=8;j:LinkOrder('order',seq);j:TagMode(seq,'MANUAL')
        local out=j:Get(seq);assert(out.payload.nested.value==7);out.payload.nested.value=9
        local linked=j:GetByOrder('order');linked[1].mode='spoof'
        assert(j:Get(seq).mode=='MANUAL' and j:Get(seq).payload.nested.value==7)
        ''')
    def test_game_clock_finite_monotonic_with_equal_pause_entries(self):
        self.lua.execute('''
        assert(j:Append(100,'state',42,{}));assert(j:Append(100,'paused',42,{}))
        for _,v in ipairs({99,0/0,math.huge,true,'100'})do assert(j:Append(v,'state',42,{})==nil)end
        assert(j:Count()==2 and j:Append(101,'unpaused',42,{}))
        ''')
