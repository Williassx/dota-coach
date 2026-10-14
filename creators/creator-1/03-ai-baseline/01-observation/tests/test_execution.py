"""Actual Lua projection invariance; no native visibility assertion."""
from pathlib import Path
import unittest
try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime = None
SOURCE = Path(__file__).resolve().parents[1] / 'src/scripts/vscripts/observation.lua'
@unittest.skipIf(LuaRuntime is None, 'optional_lua51_runtime_unavailable')
class ObservationExecutionTests(unittest.TestCase):
    def test_hidden_and_future_changes_preserve_actual_visible_choice(self):
        lua=LuaRuntime(register_eval=False,register_builtins=False)
        lua.execute('function class(t)return t end')
        lua.execute(SOURCE.read_text(encoding='utf-8'))
        lua.execute('''
        local o=setmetatable({}, {__index=CD1C301Observation});o:Init()
        local a=o:FilterVisible({{id=7,visible=true},{id=8,visible=false,x=1},{id=9,visible=true,future=true}})
        local b=o:FilterVisible({{id=7,visible=true},{id=88,visible=false,x=99999},{id=99,visible=true,future=true}})
        local p=o:BuildProjection({},a);local q=o:BuildProjection({},b)
        assert(#a==1 and #b==1 and o:Choose(p,11)==o:Choose(q,11))
        assert(o:BuildProjection({},{{id=8,visible=true,hidden=true}})==nil)
        assert(o:BuildProjection({},{{id=8,visible=true,future=true}})==nil)
        ''')
