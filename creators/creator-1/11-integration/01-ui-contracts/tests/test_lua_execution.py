"""Execute the actual pure Lua sources; never engine/API acceptance.

Requires optional lupa.lua51; no package installation on import. Its absence is
an explicit skip, so the canonical runner continues to report incomplete coverage.
"""
from pathlib import Path
import importlib.util
import unittest

try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime = None

C1 = Path(__file__).resolve().parents[3]
MODULES = {
    'arbiter': ('03-ai-baseline/03-order-arbiter/src/scripts/vscripts/order_arbiter.lua', 'CD1C303Arbiter'),
    'binding': ('02-runtime/02-actor-binding/src/scripts/vscripts/actor_binding.lua', 'CD1C202Binding'),
    'manual': ('04-intervention/01-manual-actions/src/scripts/vscripts/manual_mode.lua', 'CD1C401Manual'),
    'return': ('04-intervention/02-return-ai/src/scripts/vscripts/return_manager.lua', 'CD1C402Return'),
}


@unittest.skipIf(LuaRuntime is None, 'optional_lua51_runtime_unavailable')
class LuaExecutionTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True, register_eval=False,
                              register_builtins=False)
        self.lua.execute('function class(t) return t end')

    def load(self, module):
        path, name = MODULES[module]
        self.lua.execute((C1 / path).read_text(encoding='utf-8'))
        self.lua.execute(f'instance=setmetatable({{}}, {{__index={name}}}); instance:Init()')

    def check(self, script):
        self.lua.execute(script)

    def test_manual_blocks_ai_and_coach_without_consuming_ids(self):
        self.load('arbiter')
        self.check('''
        for _,source in ipairs({'ai','coach'}) do
          local cmd={orderId=source,source=source,revision=3}
          local result,why=instance:Resolve(cmd,true)
          assert(result==nil and why=='manual-holds-authority')
          assert(instance.seen[source]==nil and instance.lastRevision==0)
        end
        assert(instance:Resolve({orderId='m',source='manual',revision=3},true))
        ''')

    def test_actual_voice_producer_reaches_arbiter_and_duplicate_stays_rejected(self):
        path = C1 / '11-integration/02-voice-commands/src/voice_gate.py'
        spec = importlib.util.spec_from_file_location('voice_gate_execution', path)
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        command, reason = gate.parse_structured({'action': 'farm', 'target': 'TEST-t1',
                                                'orderId': 'TEST-voice-1', 'revision': 3})
        self.assertEqual(reason, 'ok')
        self.assertEqual(command['source'], 'coach')
        self.assertEqual(command['origin'], 'voice')
        self.load('arbiter')
        self.lua.globals().command = self.lua.table_from(command)
        self.check('''
        local result,winner=instance:Resolve(command,false)
        assert(result and winner=='coach' and result.origin=='voice')
        local duplicate,why=instance:Resolve(command,false)
        assert(duplicate==nil and why=='duplicate-or-missing-id')
        ''')

    def test_same_revision_lower_priority_is_rejected_new_epoch_allowed(self):
        self.load('arbiter')
        self.check('''
        assert(instance:Resolve({orderId='c',source='coach',revision=3},false))
        local result,why=instance:Resolve({orderId='a',source='ai',revision=3},false)
        assert(result==nil and why=='lower-priority')
        assert(instance.seen.a==nil)
        assert(instance:Resolve({orderId='a',source='ai',revision=4},false))
        local repeatResult=instance:Resolve({orderId='a',source='ai',revision=4},false)
        assert(repeatResult==nil)
        ''')

    def test_invalid_revision_and_id_never_poison_arbiter(self):
        self.load('arbiter')
        self.check('''
        for _,r in ipairs({0/0,math.huge,-1,1.5,9007199254740992}) do
          assert(instance:Resolve({orderId='bad',source='coach',revision=r},false)==nil)
          assert(instance.lastRevision==0 and instance.seen.bad==nil)
        end
        for _,id in ipairs({'','   ',true,{},42,string.rep('x',129)}) do
          assert(instance:Resolve({orderId=id,source='coach',revision=0},false)==nil)
        end
        assert(instance:Resolve({orderId='ok',source='coach',revision=0},false))
        ''')

    def test_binding_snapshot_mutation_does_not_change_internal_authority(self):
        self.load('binding')
        self.check('''
        local revision=instance:Bind('TEST-p1',0,11,0)
        local copy=instance:Resolve('TEST-p1')
        copy.owner=9; copy.entity=99; copy.revision=999; copy.alive=false
        assert(instance:Accepts('TEST-p1',11,revision))
        assert(instance:CheckOwner('TEST-p1',0))
        assert(not instance:CheckOwner('TEST-p1',9))
        ''')

    def test_binding_rejects_bad_indices_and_respawn_owner_atomically(self):
        self.load('binding')
        self.check('''
        for _,bad in ipairs({-1,0/0,math.huge,1.5}) do
          assert(instance:Bind('bad',bad,11,0)==nil)
          assert(instance:Bind('bad',0,bad,0)==nil)
          assert(instance:Bind('bad',0,11,bad)==nil)
        end
        assert(instance.revision==0)
        local revision=instance:Bind('TEST-p1',0,11,0)
        assert(instance:OnDeath(11))
        local before=instance.revision
        assert(instance:OnRespawn('TEST-p1',12,'foreign')==nil)
        assert(instance.revision==before and not instance:Resolve('TEST-p1').alive)
        local nextRevision=instance:OnRespawn('TEST-p1',12,0)
        assert(nextRevision>revision and instance:Accepts('TEST-p1',12,nextRevision))
        assert(not instance:Accepts('TEST-p1',11,revision))
        ''')

    def test_return_three_public_cycles_require_new_observation_revision(self):
        self.load('return')
        self.check('''
        for cycle,reason in ipairs({'cancel','timeout','release'}) do
          assert(instance:EnterManual(cycle*10))
          assert(instance:StartReturn(reason))
          for _,bad in ipairs({cycle*10,cycle*10-1,0/0,math.huge,1.5}) do
            assert(instance:FinishReturn(bad)==nil)
            assert(instance.state=='REASSESS' and instance.completedCycles==cycle-1)
          end
          assert(instance:FinishReturn(cycle*10+1)==cycle)
          assert(instance.state=='AI' and instance.reassessed)
        end
        ''')

    def test_manual_refusal_clears_captured_actor_and_invalid_request_is_inert(self):
        self.load('manual')
        self.check('''
        for _,bad in ipairs({-1,0/0,math.huge,1.5}) do
          assert(instance:Request(bad)==nil and instance.state=='AI')
        end
        assert(instance:Request(11))
        assert(instance:Confirm(false)==nil)
        assert(instance.state=='AI' and instance.actor==nil)
        assert(instance:Request(12)); assert(instance:Confirm(true)==1)
        assert(instance:IsManual()); assert(instance:Leave('timeout'))
        assert(instance.state=='AI' and instance.actor==nil)
        ''')


if __name__ == '__main__':
    unittest.main()
