"use strict";
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const test=require('node:test');
const vm=require('node:vm');
function fixture(){
 const calls=[];
 const deny=new Proxy({}, {get(_,key){calls.push(String(key));throw Error('native unavailable');}});
 const context=vm.createContext({$:deny,Game:deny,Entities:deny,GameEvents:deny,GameUI:deny});
 const source=path.resolve(__dirname,'../src/panorama/scripts/custom_game/team_picker_state.js');
 vm.runInContext(fs.readFileSync(source,'utf8'),context);
 return {model:context.DotaCoachTeamPicker.create(),calls};
}
function profile(id,extra={}){return {id,playerName:'Тестовый игрок '+id,profileVersion:'v1',kind:'synthetic',sourceLabel:'Синтетическая фикстура',coverage:'unknown',...extra};}
function snapshot(revision,profiles){return {revision,profiles};}
function catalog(model,count=6){assert.equal(model.update(snapshot(0,Array.from({length:count},(_,n)=>profile('p'+n)))),true);}

test('empty definitions do not access native and cannot produce a draft',()=>{
 const {model,calls}=fixture();assert.equal(model.view().status,'empty');assert.equal(model.draft(),null);
 assert.equal(model.choose('p0'),false);assert.deepEqual(calls,[]);
});
test('choose exactly five distinct ids and reject sixth or duplicate without revision change',()=>{
 const {model}=fixture();catalog(model);for(let n=0;n<5;n++)assert.equal(model.choose('p'+n),true);
 const draft=model.draft();assert.equal(draft.complete,true);assert.equal(draft.serverConfirmed,false);
 assert.equal(draft.players.length,5);assert.equal(model.choose('p0'),false);assert.match(model.view().message,/уже выбрана/);
 assert.equal(model.choose('p5'),false);assert.match(model.view().message,/пять/);assert.equal(model.draft().draftRevision,draft.draftRevision);
});
test('selection order and remove/clear update local revision only when choices change',()=>{
 const {model}=fixture();catalog(model);model.choose('p2');model.choose('p0');assert.equal(model.draft().players[0].id,'p2');
 const before=model.draft().draftRevision;assert.equal(model.remove('p3'),false);assert.equal(model.draft().draftRevision,before);
 assert.equal(model.remove('p2'),true);assert.equal(model.draft().draftRevision,before+1);assert.equal(model.draft().players[0].id,'p0');
 model.clear();const empty=model.draft().draftRevision;assert.equal(model.clear(),true);assert.equal(model.draft().draftRevision,empty);
});
test('catalog reorder retains exact selected id and profile version',()=>{
 const {model}=fixture();catalog(model);model.choose('p2');model.choose('p0');const before=model.draft().draftRevision;
 model.update(snapshot(1,[profile('p0'),profile('p2')]));assert.equal(model.draft().players[0].id,'p2');assert.equal(model.draft().draftRevision,before);
});
test('changed version or missing player is removed without automatic reselection',()=>{
 const {model}=fixture();catalog(model);model.choose('p0');model.choose('p1');const before=model.draft().draftRevision;
 model.update(snapshot(1,[profile('p0',{profileVersion:'v2'}),profile('p2')]));assert.equal(model.view().count,0);assert.equal(model.draft().draftRevision,before+1);
 model.update(snapshot(2,[profile('p0'),profile('p1')]));assert.equal(model.view().count,0);assert.equal(model.choose('p0'),true);
});
test('different ids with same display name remain distinct; versions of same id cannot fill two slots',()=>{
 const {model}=fixture();assert.equal(model.update(snapshot(0,[profile('a',{playerName:'Same'}),profile('b',{playerName:'Same'})])),true);
 model.choose('a');model.choose('b');assert.equal(model.view().count,2);
 assert.equal(model.update(snapshot(1,[profile('a'),profile('a',{profileVersion:'v2'})])),false);assert.equal(model.draft(),null);
});
test('mixed profile types and reported coverage remain unverified selected warnings',()=>{
 const {model}=fixture();model.update(snapshot(0,[profile('s'),profile('m',{kind:'player_model',sourceLabel:'Источник указан интегратором',coverage:'reported'})]));
 model.choose('m');assert.equal(model.view().warnings.length,2);assert.match(model.view().warnings[0].text,/не проверено/);
 assert.match(model.view().warnings[1].text,/роль, герой и патч/);model.choose('s');assert.equal(model.view().warnings.length,4);
 assert.match(model.view().warnings[2].text,/синтетический/);assert.equal(model.draft().serverConfirmed,false);
});
test('limited and unknown coverage warning do not invent percentages or block local draft',()=>{
 const {model}=fixture();model.update(snapshot(0,[profile('l',{coverage:'limited'}),profile('u')]));model.choose('l');model.choose('u');
 assert.match(model.view().warnings[1].text,/ограниченный/);assert.match(model.view().warnings[3].text,/неизвестен/);assert.equal(model.view().count,2);
});
test('view and draft return independent copies of all nested data',()=>{
 const {model}=fixture();catalog(model);model.choose('p0');const view=model.view(),draft=model.draft();
 view.profiles[0].playerName='Mutation';view.selected[0].profileVersion='bad';view.warnings[0].text='bad';view.selected.length=0;
 draft.players[0].id='bad';draft.players.length=0;assert.equal(model.view().selected[0].id,'p0');assert.equal(model.draft().players[0].profileVersion,'v1');
});
test('input mutations after accepted snapshot do not change stored profiles',()=>{
 const {model}=fixture();const row=profile('a'),rows=[row];model.update(snapshot(0,rows));row.playerName='Mutation';rows.length=0;
 assert.equal(model.view().profiles[0].playerName,'Тестовый игрок a');assert.equal(model.choose('a'),true);
});
test('old and duplicate revision skip both profile body and own keys',()=>{
 const {model}=fixture();catalog(model);model.choose('p0');let reads=0;
 const old=new Proxy({revision:0},{get(target,key){if(key==='profiles'){reads++;throw Error('body');}return target[key];},ownKeys(){reads++;throw Error('keys');}});
 assert.equal(model.update(old),false);assert.equal(reads,0);assert.equal(model.view().count,1);
});
test('invalid newer snapshot clears catalog and draft and consumes revision',()=>{
 const {model}=fixture();catalog(model);model.choose('p0');assert.equal(model.update(snapshot(5,[profile('bad',{kind:'fake'})])),false);
 assert.equal(model.view().status,'invalid');assert.equal(model.draft(),null);assert.equal(model.choose('p0'),false);
 assert.equal(model.update(snapshot(5,[profile('p0')])),false);assert.equal(model.view().status,'invalid');
 assert.equal(model.update(snapshot(6,[profile('p0')])),true);assert.equal(model.view().count,0);
});
test('invalid revisions and malformed headers fail closed',()=>{
 for(const revision of [NaN,Infinity,-1,.5,'2',9007199254740992]){const {model}=fixture();catalog(model);model.choose('p0');assert.equal(model.update(snapshot(revision,[profile('p0')])),false);assert.equal(model.draft(),null);}
 for(const input of [null,[],{}, {revision:1,profiles:[],extra:true}]){const {model}=fixture();catalog(model);assert.equal(model.update(input),false);assert.equal(model.draft(),null);}
});
test('profile schema rejects nonenumerable extras, missing fields and invalid strings',()=>{
 for(const mode of ['extra','missing','space-id','blank-name','version','kind','coverage']){
 const {model}=fixture();const row=profile('a');
 if(mode==='extra')Object.defineProperty(row,'secret',{value:true});if(mode==='missing')delete row.sourceLabel;
 if(mode==='space-id')row.id=' a';if(mode==='blank-name')row.playerName=' ';if(mode==='version')row.profileVersion='v'.repeat(65);
 if(mode==='kind')row.kind='real';if(mode==='coverage')row.coverage='supported';assert.equal(model.update(snapshot(0,[row])),false,mode);
 }
});
test('catalog is bounded to 64 profiles and rejects sparse or non-array input',()=>{
 for(const rows of [Array.from({length:65},(_,n)=>profile('p'+n)),new Array(2),{length:1,0:profile('a')},null]){
 const {model}=fixture();assert.equal(model.update(snapshot(0,rows)),false);
 }const {model}=fixture();catalog(model,64);assert.equal(model.view().profiles.length,64);
});
test('complete copy explicitly labels local draft and never reports match readiness',()=>{
 const {model}=fixture();catalog(model);assert.match(model.view().message,/состав не подтверждён/);
 for(let n=0;n<5;n++)model.choose('p'+n);assert.match(model.view().message,/локальный черновик/);assert.equal(model.view().complete,true);
 model.remove('p0');assert.equal(model.view().complete,false);
});
test('catalog getter cannot choose while a new snapshot is decoding',()=>{
 const {model}=fixture();catalog(model);model.choose('p0');const next=snapshot(1,[]);
 Object.defineProperty(next,'profiles',{enumerable:true,get(){assert.equal(model.choose('p1'),false);assert.equal(model.draft(),null);return [profile('p0'),profile('p1')];}});
 assert.equal(model.update(next),true);assert.equal(model.view().count,1);assert.equal(model.view().selected[0].id,'p0');
});
test('getter disposal cannot restore catalog or draft',()=>{
 const {model}=fixture();catalog(model);const row=profile('a');Object.defineProperty(row,'playerName',{enumerable:true,get(){model.dispose();return 'Disposed';}});
 assert.equal(model.update(snapshot(1,[row])),false);assert.equal(model.isDisposed(),true);assert.equal(model.view().profiles.length,0);assert.equal(model.draft(),null);
});
test('newer reentrant snapshot wins over an older decoding result',()=>{
 const {model}=fixture();catalog(model);const row=profile('old');Object.defineProperty(row,'sourceLabel',{enumerable:true,get(){assert.equal(model.update(snapshot(2,[profile('new')])),true);model.choose('new');return 'old';}});
 assert.equal(model.update(snapshot(1,[row])),false);assert.equal(model.view().profiles[0].id,'new');assert.equal(model.view().selected[0].id,'new');assert.equal(model.draft().catalogRevision,2);
});
test('throw after newer reentrant update cannot clear the newer catalog',()=>{
 const {model}=fixture();const row=profile('old');Object.defineProperty(row,'sourceLabel',{enumerable:true,get(){model.update(snapshot(2,[profile('new')]));throw Error('old failed');}});
 assert.equal(model.update(snapshot(1,[row])),false);assert.equal(model.view().status,'ready');assert.equal(model.view().profiles[0].id,'new');
});
test('shape changed by a getter invalidates the whole new snapshot',()=>{
 const {model}=fixture();const row=profile('a');Object.defineProperty(row,'sourceLabel',{enumerable:true,get(){row.extra=true;return 'fixture';}});
 assert.equal(model.update(snapshot(0,[row])),false);assert.equal(model.view().status,'invalid');
});
test('disposed model ignores all mutations without native work',()=>{
 const {model,calls}=fixture();catalog(model);model.choose('p0');model.dispose();model.dispose();
 assert.equal(model.update(snapshot(1,[profile('a')])),false);assert.equal(model.choose('a'),false);assert.equal(model.remove('p0'),false);assert.equal(model.clear(),false);
 assert.equal(model.view().status,'disposed');assert.equal(model.view().selected.length,0);assert.equal(model.draft(),null);assert.deepEqual(calls,[]);
});
test('all local draft mutations are unavailable while snapshot body is decoding',()=>{
 const {model}=fixture();catalog(model);model.choose('p0');const next={revision:1,get profiles(){
 assert.equal(model.draft(),null);assert.equal(model.remove('p0'),false);assert.equal(model.clear(),false);
 assert.equal(model.choose('p1'),false);return [profile('p0'),profile('p1')];}};
 assert.equal(model.update(next),true);assert.equal(model.view().selected[0].id,'p0');assert.equal(model.draft().catalogRevision,1);
});
test('rejected old reentry cannot cancel an accepted newer outer snapshot',()=>{
 const {model}=fixture();catalog(model);const next={revision:3,get profiles(){
 for(const revision of [0,2])assert.equal(model.update({revision,get profiles(){throw Error('old body');}}),false);
 return [profile('new')];}};assert.equal(model.update(next),true);assert.equal(model.draft().catalogRevision,3);
});
test('failed attempts after invalid catalog retain explanation that previous draft was removed',()=>{
 const {model}=fixture();catalog(model);model.choose('p0');model.update(snapshot(1,[profile('bad',{kind:'fake'})]));
 for(const call of [()=>model.choose('p0'),()=>model.remove('p0'),()=>model.clear()]){
 assert.equal(call(),false);assert.match(model.view().message,/черновик снят/);
 }
});
test('new catalog explains removal caused by changed profile version or disappearance',()=>{
 for(const rows of [[profile('p0',{profileVersion:'v2'})],[]]){
 const {model}=fixture();catalog(model);model.choose('p0');model.update(snapshot(1,rows));
 assert.equal(model.view().count,0);assert.match(model.view().message,/выбор.*снят/i);
 }
});
test('catalog length is captured once before bounded decode and cannot grow the loop',()=>{
 const {model}=fixture();let lengths=0,items=0;
 const rows=new Proxy([], {get(target,key){if(key==='length')return ++lengths===1?0:1000;
 if(/^\d+$/.test(String(key))){items++;return profile('p'+key);}return Reflect.get(target,key);}});
 assert.equal(model.update(snapshot(0,rows)),false);assert.equal(items,0);assert.equal(model.view().profiles.length,0);
});
test('invalid reentrant update prevents older in-flight decode from restoring a catalog',()=>{
 const {model}=fixture();catalog(model);const next={revision:2,get profiles(){
 assert.equal(model.update({revision:'invalid',profiles:[]}),false);return [profile('restored')];}};
 assert.equal(model.update(next),false);assert.equal(model.view().status,'invalid');assert.equal(model.draft(),null);
 assert.equal(model.update(snapshot(3,[profile('fresh')])),true);
});
