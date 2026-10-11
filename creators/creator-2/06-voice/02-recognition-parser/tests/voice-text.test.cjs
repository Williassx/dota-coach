const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../../../../..');
const roster = path.join(root, 'creators/creator-2/02-coach-interface/01-roster-cards/src/panorama/scripts/custom_game/roster_cards_state.js');
const source = path.join(__dirname, '../src/panorama/scripts/custom_game/voice_text_state.js');
function setup() {
    const calls = [];
    const native = new Proxy({}, {get(_t, k) { calls.push(String(k)); throw Error('Native forbidden'); }});
    const context = vm.createContext({Game: native, GameEvents: native, Players: native, Entities: native, $: native});
    vm.runInContext(fs.readFileSync(roster, 'utf8'), context);
    vm.runInContext(fs.readFileSync(source, 'utf8'), context);
    return {model: context.DotaCoachVoiceText.create(), calls};
}
function player(id='a', playerName='Альфа', role=1, extra={}) {
    return {id, playerName, heroName:'Synthetic hero', role, source:'synthetic', side:'own', availability:'alive', ...extra};
}
function snapshot(revision=1, players=[player()]) { return {revision, players}; }
function event(text='Альфа, фарми', extra={}) { return {utteranceId:'speech-1', text, rosterRevision:1, final:true, ...extra}; }
function fixture(players) { const data=setup(); assert.equal(data.model.update(snapshot(1, players)),true); return data; }
function plain(value) { return JSON.parse(JSON.stringify(value)); }

test('load and explicit create are inert; final phrase creates local proposal only',()=>{
    const {model,calls}=fixture(); const result=model.ingest(event());
    assert.equal(result.status,'ready'); assert.equal(result.reason,'none');
    assert.deepEqual(plain(result.proposal),{utteranceId:'speech-1',rosterRevision:1,action:'farm',recipientIds:['a'],addressKind:'player'});
    assert.deepEqual(calls,[]);
});
test('four actions and singular/plural exact vocabulary',()=>{
    const {model}=fixture(); const cases={фарми:'farm',фармите:'farm',отступай:'retreat',отступайте:'retreat',соберись:'regroup',соберитесь:'regroup','держи позицию':'hold','держите позицию':'hold'};
    let n=0; for(const [phrase,action] of Object.entries(cases)) assert.equal(model.ingest(event('Альфа '+phrase,{utteranceId:'s'+n++})).proposal.action,action);
});
test('case yo whitespace comma and terminal punctuation normalize',()=>{
    const {model}=fixture([player('a','Ёж')]); const result=model.ingest(event(' \tЕЖ,\n ДЕРЖИ   ПОЗИЦИЮ!!! '));
    assert.equal(result.status,'ready'); assert.equal(result.normalizedText,'еж держи позицию');
});
test('all five roles address stable IDs independent of row order',()=>{
    const players=[1,2,3,4,5].map(n=>player('p'+n,'Имя'+n,n)).reverse(); const {model}=fixture(players);
    ['керри','мидер','оффлейнер','четвёрка','пятёрка'].forEach((name,i)=>{
        const r=model.ingest(event(name+' отступай',{utteranceId:'r'+i})); assert.deepEqual(plain(r.proposal.recipientIds),['p'+(i+1)]); assert.equal(r.proposal.addressKind,'role');
    });
});
test('team targets all own eligible rows with no opponent',()=>{
    const {model}=fixture([player(),player('b','Бета',2),player('enemy','Враг',3,{side:'opponent'})]);
    for(const group of ['все','команда']) {
        const r=model.ingest(event(group+' соберитесь',{utteranceId:group})); assert.equal(r.proposal.addressKind,'group'); assert.deepEqual(plain(r.proposal.recipientIds),['a','b']);
    }
});
test('duplicate nick and role refuse ambiguous addresses',()=>{
    for(const players of [[player(),player('b','Альфа',2)],[player(),player('b','Бета',1)]]) {
        const {model}=fixture(players); const r=model.ingest(event(players[1].playerName==='Альфа'?'Альфа фарми':'керри фарми'));
        assert.equal(r.reason,'ambiguous_address'); assert.equal(r.proposal,null);
    }
});
test('reserved role/group nick collision refuses interpretation',()=>{
    for(const name of ['керри','команда']) {
        const {model}=fixture([player(),player('b',name,2)]); assert.equal(model.ingest(event(name+' фарми')).reason,'ambiguous_address');
    }
});
test('dead unsupported unknown-source or opponent name cannot produce proposal',()=>{
    for(const extra of [{availability:'dead'},{availability:'unsupported'},{source:'unknown'},{side:'opponent'}]) {
        const {model}=fixture([player('a','Альфа',1,extra)]); const r=model.ingest(event()); assert.equal(r.reason,'address_unavailable'); assert.equal(r.proposal,null);
    }
});
test('team refuses whole command if any own recipient unavailable; empty team rejected',()=>{
    const {model}=fixture([player(),player('b','Бета',2,{availability:'dead'})]);
    assert.equal(model.ingest(event('все отступайте')).reason,'address_unavailable');
    assert.equal(model.update(snapshot(2,[])),true); assert.equal(model.ingest(event('все фармите',{utteranceId:'empty',rosterRevision:2})).reason,'unknown_address');
});
test('no fuzzy matching default address hero selection or target inference',()=>{
    const {model}=fixture();
    for(const [text,reason] of [['Алфа фарми','unknown_address'],['фарми','missing_address'],['Synthetic hero фарми','unknown_address'],['Альфа атакуй','unknown_action'],['Альфа фарми лес','unknown_action']]) {
        const r=model.ingest(event(text,{utteranceId:text})); assert.equal(r.reason,reason); assert.equal(r.proposal,null);
    }
});
test('negation compound and unsupported symbols reject without proposal',()=>{
    const {model}=fixture();
    for(const [text,reason] of [['Альфа не отступай','negated'],['Альфа фарми и отступай','multiple_commands'],['Альфа потом фарми','multiple_commands'],['Альфа, <b>фарми</b>','invalid_text'],['Альфа\u0000 фарми','invalid_text'],['Альфа—фарми','invalid_text']]) assert.equal(model.ingest(event(text,{utteranceId:text.replace(/\u0000/g,'0')})).reason,reason);
});
test('interim events do not propose or reserve ID; final duplicate remains rejected',()=>{
    const {model}=fixture(); assert.equal(model.ingest(event('',{final:false})).status,'interim'); assert.equal(model.view().consumed,0);
    assert.equal(model.ingest(event()).status,'ready'); assert.equal(model.ingest(event('Альфа отступай')).reason,'duplicate'); assert.equal(model.view().consumed,1);
});
test('stale final and unknown final consume ID preventing later reinterpretation',()=>{
    const {model}=fixture(); assert.equal(model.ingest(event('Альфа фарми',{rosterRevision:0})).reason,'stale_roster');
    assert.equal(model.ingest(event()).reason,'duplicate'); assert.equal(model.ingest(event('unknown',{utteranceId:'s2'})).reason,'unknown_action');
    assert.equal(model.ingest(event('Альфа фарми',{utteranceId:'s2'})).reason,'duplicate');
});
test('new roster revisions never silently retarget a captured event',()=>{
    const {model}=fixture(); const old=model.ingest(event()).proposal;
    assert.equal(model.update(snapshot(2,[player('b','Альфа')])),true);
    assert.equal(model.ingest(event('Альфа фарми',{utteranceId:'s2'})).reason,'stale_roster');
    assert.deepEqual(plain(old.recipientIds),['a']); assert.deepEqual(plain(model.ingest(event('Альфа фарми',{utteranceId:'s3',rosterRevision:2})).proposal.recipientIds),['b']);
});
test('bounded final history fails closed without eviction across source updates',()=>{
    const {model}=fixture(); for(let i=0;i<128;i++) assert.equal(model.ingest(event('Альфа фарми',{utteranceId:'s'+i})).status,'ready');
    assert.equal(model.ingest(event('Альфа фарми',{utteranceId:'s128'})).reason,'history_full');
    assert.equal(model.update(snapshot(2)),true); assert.equal(model.ingest(event('Альфа фарми',{utteranceId:'s0',rosterRevision:2})).reason,'duplicate');
});
test('snapshot atomic monotonic exact schema and existing Roster validation',()=>{
    const {model}=fixture();
    const invalid=[snapshot(1),snapshot(0),snapshot(2,[player(),player()]),snapshot(2,[player('b','Бета',6)]),snapshot(2,[player('a','Альфа',1,{source:'fake'})]),{...snapshot(2),extra:true},snapshot(true),snapshot(Infinity)];
    for(const data of invalid) assert.equal(model.update(data),false);
    assert.equal(model.view().revision,1); assert.deepEqual(plain(model.ingest(event()).proposal.recipientIds),['a']);
});
test('bounded and sparse arrays reject before reading items/getters',()=>{
    const {model}=fixture(); let reads=0;
    const huge=new Array(6); Object.defineProperty(huge,0,{get(){reads++;throw Error('read');},enumerable:true});
    assert.equal(model.update(snapshot(2,huge)),false); assert.equal(reads,0);
    assert.equal(model.update(snapshot(2,new Array(1))),false);
    const named=[player()]; named.extra=1; assert.equal(model.update(snapshot(2,named)),false);
});
test('own data descriptors reject accessors without executing them',()=>{
    const {model}=fixture(); let reads=0;
    for(const [data,key] of [[snapshot(2),'players'],[player(),'playerName'],[event(),'text']]) {
        Object.defineProperty(data,key,{enumerable:true,get(){reads++;throw Error('read');}});
        if(key==='players') assert.equal(model.update(data),false); else if(key==='playerName') assert.equal(model.update(snapshot(2,[data])),false); else assert.equal(model.ingest(data).reason,'invalid_event');
    }
    assert.equal(reads,0);
});
test('event metadata bounds exact schema and non-final values reject safely',()=>{
    const {model}=fixture();
    for(const extra of [{utteranceId:''},{utteranceId:' x'},{utteranceId:'x'.repeat(65)},{final:1},{rosterRevision:true},{rosterRevision:-1},{extra:1}]) assert.equal(model.ingest(event('Альфа фарми',extra)).reason,'invalid_event');
    assert.equal(model.view().consumed,0); assert.equal(model.ingest(event('x'.repeat(257))).reason,'invalid_text');
});
test('no roster before first valid source and dependency errors fail explicitly',()=>{
    const {model,calls}=setup(); assert.equal(model.ingest(event()).reason,'no_roster'); assert.equal(model.view().consumed,1); assert.deepEqual(calls,[]);
    const context=vm.createContext({}); vm.runInContext(fs.readFileSync(source,'utf8'),context); assert.throws(()=>context.DotaCoachVoiceText.create(),/Roster/);
});
test('input proposal view and vocabulary are independent copies; history stores IDs only',()=>{
    const {model}=setup(); const data=snapshot(); assert.equal(model.update(data),true); data.players[0].id='mutated'; data.players[0].playerName='mutated';
    const r=model.ingest(event()); r.proposal.recipientIds[0]='bad'; const view=model.view(); view.revision=99;
    const words=model.vocabulary(); words.actions[0].phrases[0]='bad'; assert.equal(model.vocabulary().actions[0].phrases[0],'фарми');
    assert.equal(model.view().revision,1); assert.equal(JSON.stringify(model.view()).includes('Альфа'),false);
    assert.deepEqual(plain(model.ingest(event('Альфа фарми',{utteranceId:'s2'})).proposal.recipientIds),['a']);
});
test('descriptor proxy reentry cannot mutate or parse during update',()=>{
    const {model}=fixture(); let once=false, nested;
    const data=new Proxy(snapshot(2),{getOwnPropertyDescriptor(target,key){if(!once){once=true; nested=model.ingest(event()); assert.equal(model.update(snapshot(3)),false);} return Reflect.getOwnPropertyDescriptor(target,key);}});
    assert.equal(model.update(data),true); assert.equal(nested.reason,'busy'); assert.equal(model.view().consumed,0); assert.equal(model.view().revision,2);
});
test('dispose during source or event descriptor trap is permanent',()=>{
    for(const mode of ['update','ingest']) {
        const {model}=fixture(); let once=false; const data=new Proxy(mode==='update'?snapshot(2):event(),{getOwnPropertyDescriptor(target,key){if(!once){once=true;model.dispose();}return Reflect.getOwnPropertyDescriptor(target,key);}});
        const result=mode==='update'?model.update(data):model.ingest(data); if(mode==='update') assert.equal(result,false); else {assert.equal(result.status,'disposed');assert.equal(result.proposal,null);}
        assert.equal(model.view().status,'disposed'); assert.equal(model.update(snapshot(3)),false); assert.equal(model.ingest(event()).status,'disposed'); model.dispose();
    }
});
