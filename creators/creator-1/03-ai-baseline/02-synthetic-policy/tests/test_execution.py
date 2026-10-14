"""Actual TEST policy and arbiter; no engine effects."""
from pathlib import Path
import unittest
try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime=None
C1=Path(__file__).resolve().parents[3]
@unittest.skipIf(LuaRuntime is None,'optional_lua51_runtime_unavailable')
class SyntheticExecutionTests(unittest.TestCase):
    def test_fresh_own_position_patrol_and_manual_arbiter_block(self):
        lua=LuaRuntime(register_eval=False,register_builtins=False)
        lua.execute('function class(t)return t end')
        for path in ('03-ai-baseline/02-synthetic-policy/src/scripts/vscripts/synthetic_policy.lua','03-ai-baseline/03-order-arbiter/src/scripts/vscripts/order_arbiter.lua'):
            lua.execute((C1/path).read_text(encoding='utf-8'))
        lua.execute('''
        local p=setmetatable({}, {__index=CD1C302Synthetic});p:Init()
        local a=setmetatable({}, {__index=CD1C303Arbiter});a:Init()
        local input={own={{x=100,y=200,z=128}},visible={}}
        local first=p:Decide(input);assert(first.synthetic and first.kind=='move')
        assert(first.position[1]==400 and first.position[2]==200 and first.position[3]==128)
        input.own[1].x=800;local second=p:Decide(input)
        assert(second.position[1]==500 and first.position[1]==400)
        local admitted=a:Resolve({source='ai',orderId='p1',revision=1,choice=first},false);assert(admitted)
        assert(a:Resolve({source='ai',orderId='p2',revision=2,choice=second},true)==nil)
        assert(a.seen.p2==nil and input.own[1].x==800)
        assert(p:Decide({own={{x=0/0,y=0,z=0}},visible={}})==nil)
        ''')
