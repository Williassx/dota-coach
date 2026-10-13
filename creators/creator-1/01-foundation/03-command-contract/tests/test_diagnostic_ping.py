"""Actual Lua51 evaluator and stubbed TEST adapter; never native acceptance.

Optional lupa.lua51 absence is explicit incomplete coverage, not a silent PASS.
No installation, listener registration or engine action occurs on Python import.
"""
from pathlib import Path
import unittest

try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime = None

SOURCE = Path(__file__).resolve().parents[1] / 'src/scripts/vscripts'


@unittest.skipIf(LuaRuntime is None, 'optional_lua51_runtime_unavailable')
class DiagnosticPingTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((SOURCE / 'diagnostic_ping.lua').is_file(), 'Diagnostic evaluator missing')
        self.assertTrue((SOURCE / 'ping_game_mode.lua').is_file(), 'Diagnostic TEST entrypoint missing')
        self.lua = LuaRuntime(unpack_returned_tuples=True, register_eval=False, register_builtins=False)
        self.lua.execute('''
        native_calls = 0
        function forbidden() native_calls=native_calls+1; error('engine action forbidden') end
        CreateUnitByName=forbidden; ExecuteOrderFromTable=forbidden
        ListenToGameEvent=forbidden; EntIndexToHScript=forbidden
        CustomGameEventManager={Send_ServerToAllClients=forbidden}
        PlayerResource={GetPlayer=forbidden}
        ''')
        module = self.lua.execute((SOURCE / 'diagnostic_ping.lua').read_text(encoding='utf-8'))
        self.lua.globals().M = module

    def check(self, script):
        self.lua.execute(script)
        self.assertEqual(self.lua.globals().native_calls, 0)

    def adapter(self):
        self.lua.execute('''
        package.loaded['diagnostic_ping']=M
        entities={}; players={}; sends={}; logs={}; registrations=0
        function print(message) logs[#logs+1]=message end
        function EntIndexToHScript(index) return entities[index] end
        PlayerResource={GetPlayer=function(self,id) return players[id] end}
        playerA={GetPlayerID=function(self) return 3 end}
        playerB={GetPlayerID=function(self) return 4 end}
        entities[12]=playerA; players[3]=playerA; players[4]=playerB
        CustomGameEventManager={
          RegisterListener=function(self,name,callback)
            assert(name=='dota_coach_probe_request')
            registrations=registrations+1; handler=callback; return 7
          end,
          Send_ServerToPlayer=function(self,player,name,response)
            assert(player==playerA and name=='dota_coach_probe_result')
            sends[#sends+1]={player=player,name=name,response=response}
          end,
          Send_ServerToAllClients=forbidden
        }
        ''')
        self.lua.execute((SOURCE / 'ping_game_mode.lua').read_text(encoding='utf-8'))
        self.lua.execute('Activate()')

    def test_exact_valid_request_returns_only_four_response_fields(self):
        self.check('''
        local reply=M.evaluate({protocol_version=1,request_id='TEST-id'})
        assert(reply.protocol_version==1 and reply.request_id=='TEST-id')
        assert(reply.status=='ok' and reply.reason=='none')
        local n=0; for key in pairs(reply) do n=n+1 end; assert(n==4)
        ''')

    def test_positive_integer_other_versions_are_explicit_rejections(self):
        self.check('''
        for _,version in ipairs({2,3,1000}) do
          local reply=M.evaluate({protocol_version=version,request_id='TEST-version'})
          assert(reply.protocol_version==1 and reply.request_id=='TEST-version')
          assert(reply.status=='rejected' and reply.reason=='unsupported_version')
        end
        ''')

    def test_malformed_versions_with_usable_id_are_invalid_requests(self):
        self.check('''
        for _,version in ipairs({0,-1,1.5,'1',true,false,0/0,math.huge,-math.huge,{}}) do
          local reply=M.evaluate({protocol_version=version,request_id='TEST-malformed'})
          assert(reply.status=='rejected' and reply.reason=='invalid_request')
        end
        assert(M.evaluate({request_id='TEST-missing'}).reason=='invalid_request')
        ''')

    def test_extra_fields_are_rejected_not_sanitized_by_pure_evaluator(self):
        self.check('''
        for _,key in ipairs({'PlayerID','source','command','unexpected'}) do
          local input={protocol_version=1,request_id='TEST-extra'}; input[key]=3
          local reply=M.evaluate(input)
          assert(reply.status=='rejected' and reply.reason=='invalid_request')
          assert(input[key]==3)
        end
        assert(M.evaluate({[1]='extra',protocol_version=1,request_id='TEST-extra'}).reason=='invalid_request')
        ''')

    def test_invalid_ids_never_produce_a_reply(self):
        self.check(r'''
        for _,id in ipairs({'',' ',' leading','trailing ', 'line\n', 'nul\0',
                              string.rep('x',65),false,1,{}}) do
          assert(M.evaluate({protocol_version=1,request_id=id})==nil)
        end
        assert(M.evaluate({protocol_version=1})==nil)
        local id=string.rep('x',64); assert(M.evaluate({protocol_version=1,request_id=id}).request_id==id)
        ''')

    def test_non_tables_and_metatables_are_inert(self):
        self.check('''
        assert(M.evaluate(nil)==nil and M.evaluate(false)==nil and M.evaluate('request')==nil)
        local traps=0
        local hidden=setmetatable({}, {__index=function() traps=traps+1; error('getter forbidden') end})
        assert(M.evaluate(hidden)==nil and traps==0)
        local input=setmetatable({protocol_version=1,request_id='TEST-meta'},
          {__index=function() traps=traps+1; error('getter forbidden') end})
        assert(M.evaluate(input).reason=='invalid_request' and traps==0)
        ''')

    def test_repeated_diagnostic_ids_are_stateless_and_inputs_unchanged(self):
        self.check('''
        local input={protocol_version=1,request_id='TEST-repeat'}
        local first=M.evaluate(input); first.status='mutated'
        local second=M.evaluate(input); assert(second.status=='ok')
        assert(input.protocol_version==1 and input.request_id=='TEST-repeat')
        local n=0; for key in pairs(input) do n=n+1 end; assert(n==2)
        ''')

    def test_activate_registers_only_once(self):
        self.adapter()
        self.check("Activate(); assert(registrations==1 and #sends==0)")

    def test_trace_metadata_enum_distinguishes_verified_fields_without_inspecting_unknown_sender(self):
        self.adapter()
        self.check('''
        assert(logs[#logs]:find('metadata=uninspected',1,true))
        handler(12,{protocol_version=1,request_id='TEST-trace-absent'})
        assert(logs[#logs]:find('metadata=absent',1,true))
        handler(12,{protocol_version=1,request_id='TEST-trace-match',PlayerID=3})
        assert(logs[#logs]:find('metadata=matching_native',1,true))
        handler(12,{protocol_version=1,request_id='TEST-trace-mismatch',PlayerID=99999})
        assert(logs[#logs]:find('metadata=mismatch',1,true))
        assert(sends[1].response.status=='ok' and sends[2].response.status=='ok')
        assert(sends[3].response.reason=='invalid_request' and #sends==3)
        local watched={protocol_version=1,request_id='TEST-trace-unknown',PlayerID=99999}
        local original_rawget=rawget; local inspections=0
        rawget=function(value,key)
          if value==watched then inspections=inspections+1 end
          return original_rawget(value,key)
        end
        handler(999,watched)
        rawget=original_rawget
        assert(inspections==0 and #sends==3)
        assert(logs[#logs]:find('metadata=uninspected',1,true))
        assert(logs[#logs]:find('result=drop_unknown_sender',1,true))
        for _,message in ipairs(logs) do
          assert(not message:find('99999',1,true) and not message:find('TEST-trace',1,true))
        end
        ''')

    def test_verified_sender_receives_addressed_reply_and_matching_engine_id_is_stripped(self):
        self.adapter()
        self.check('''
        handler(12,{protocol_version=1,request_id='TEST-native'})
        local input={protocol_version=1,request_id='TEST-injected',PlayerID=3}
        handler(12,input)
        assert(#sends==2 and sends[1].player==playerA and sends[2].player==playerA)
        assert(sends[1].response.status=='ok' and sends[2].response.status=='ok')
        assert(input.PlayerID==3)
        assert(logs[#logs]:find('native%-match=true') and logs[#logs]:find('result=ok:none'))
        ''')

    def test_unknown_sender_never_uses_payload_player_id_as_fallback(self):
        self.adapter()
        self.check('''
        local input={protocol_version=1,request_id='TEST-unknown',PlayerID=3}
        handler(999,input); handler(-1,input); handler('12',input)
        entities[13]={}; handler(13,input)
        entities[14]={GetPlayerID=function() return 3 end}; handler(14,input)
        assert(#sends==0)
        ''')

    def test_mismatched_or_malformed_engine_player_id_replies_only_to_verified_sender(self):
        self.adapter()
        self.check('''
        for _,id in ipairs({4,'3',true,false,-1,0/0}) do
          handler(12,{protocol_version=1,request_id='TEST-spoof',PlayerID=id})
        end
        assert(#sends==6)
        for _,sent in ipairs(sends) do
          assert(sent.player==playerA and sent.response.status=='rejected')
          assert(sent.response.reason=='invalid_request')
        end
        ''')

    def test_native_bad_request_replies_only_to_verified_sender_when_id_is_usable(self):
        self.adapter()
        self.check('''
        handler(12,{protocol_version=2,request_id='TEST-unsupported',PlayerID=3})
        handler(12,{protocol_version=1,request_id='TEST-extra',PlayerID=3,extra=true})
        handler(12,{protocol_version=1,request_id='',PlayerID=3})
        assert(#sends==2)
        assert(sends[1].response.reason=='unsupported_version')
        assert(sends[2].response.reason=='invalid_request')
        ''')

    def test_native_resolution_exceptions_invalid_pid_and_identity_mismatch_drop(self):
        self.adapter()
        self.check('''
        entities[15]={GetPlayerID=function() error('unavailable') end}
        handler(15,{protocol_version=1,request_id='TEST-exception'})
        entities[16]={GetPlayerID=function() return math.huge end}
        handler(16,{protocol_version=1,request_id='TEST-infinite'})
        players[3]=playerB; handler(12,{protocol_version=1,request_id='TEST-mismatch',PlayerID=3})
        assert(#sends==0)
        ''')


if __name__ == '__main__':
    unittest.main()
