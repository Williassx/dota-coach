"use strict";
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const test=require('node:test');
const vm=require('node:vm');
function profile(id,extra={}){return {id,playerName:'Игрок '+id,profileVersion:'v1',kind:'synthetic',sourceLabel:'Тестовые данные',coverage:'unknown',...extra};}
function fixture(options={}){
 const nodes=new Map(),timers=new Map(),native=[];let serial=0;
 function panel(id){let text='';const p={valid:true,visible:true,enabled:false,html:true,events:{},
 IsValid(){return this.valid;},FindChildTraverse(id){return nodes.get(id);},
 SetPanelEvent(k,v){this.events[k]=v;},ClearPanelEvent(k){delete this.events[k];},
 get text(){return text;},set text(v){if(options.failText===id)throw Error('render failure');
 text=v;if(options.onText)options.onText(id,v);}};nodes.set(id,p);return p;}
 const root=panel('TeamPickerRoot');
 for(const id of ['TeamPickerStatus','TeamPickerCount','TeamPickerPage','TeamPagePrevious','TeamPageNext','TeamClear'])panel(id);
 for(let n=0;n<5;n++){
 panel('TeamCandidate'+n);panel('TeamSelected'+n);
 for(const name of ['Name','Version','Source','Coverage','Hint'])panel('TeamCandidate'+name+n);
 for(const name of ['Name','Version','Warnings','Action'])panel('TeamSelected'+name+n);
 }
 const deny=new Proxy({}, {get(_,key){return()=>{native.push(String(key));throw Error('unexpected native');};}});
 const context=vm.createContext({$: {Schedule(delay,callback){if(options.failSchedule)throw Error('schedule');timers.set(++serial,{delay,callback});return serial;},CancelScheduled(id){timers.delete(id);}},Game:deny,GameUI:deny,Entities:deny,GameEvents:deny});
 for(const file of ['team_picker_state.js','team_picker_panel.js'])vm.runInContext(fs.readFileSync(path.resolve(__dirname,'../src/panorama/scripts/custom_game',file),'utf8'),context,{filename:file});
 return {context,nodes,timers,native,root,options,bind(){return context.DotaCoachTeamPickerPanels.bind(root);},
 click(id){const callback=nodes.get(id).events.onactivate;assert.equal(typeof callback,'function',id);callback();},
 tick(){const [id,t]=[...timers][0];timers.delete(id);t.callback();}};
}
function setup(p,count=6){const ui=p.bind();assert.equal(ui.update({revision:0,profiles:Array.from({length:count},(_,n)=>profile('p'+n))}),true);return ui;}

test('startup has no candidates, actions or native side effects',()=>{
 const p=fixture(),ui=p.bind();assert.equal(ui.draft(),null);assert.match(p.nodes.get('TeamPickerCount').text,/0\/5/);
 assert.match(p.nodes.get('TeamPickerPage').text,/Нет записей/);assert.equal(p.nodes.get('TeamPageNext').enabled,false);
 assert.equal(p.nodes.get('TeamCandidate0').visible,false);assert.deepEqual(p.native,[]);ui.dispose();assert.equal(p.timers.size,0);
});
test('candidate and removal buttons edit only the local draft',()=>{
 const p=fixture(),ui=setup(p);p.click('TeamCandidate0');assert.equal(ui.draft().players[0].id,'p0');
 assert.equal(ui.draft().serverConfirmed,false);assert.match(p.nodes.get('TeamSelectedAction0').text,/Убрать/);
 p.click('TeamSelected0');assert.equal(ui.draft().players.length,0);ui.dispose();assert.deepEqual(p.native,[]);
});
test('candidate cards show kind, coverage and action cue before choice',()=>{
 const p=fixture(),ui=setup(p);assert.match(p.nodes.get('TeamCandidateSource0').text,/синтетический/i);
 assert.match(p.nodes.get('TeamCandidateCoverage0').text,/неизвестен/);assert.match(p.nodes.get('TeamCandidateHint0').text,/Добавить/);
 ui.update({revision:1,profiles:[profile('m',{kind:'player_model',coverage:'reported'})]});
 assert.match(p.nodes.get('TeamCandidateSource0').text,/не проверено/);assert.match(p.nodes.get('TeamCandidateCoverage0').text,/роль, герой и патч/);ui.dispose();
});
test('page controls do not mutate draft and stale old-page handlers cannot choose',()=>{
 const p=fixture(),ui=setup(p,12);const before=ui.draft().draftRevision,old=p.nodes.get('TeamCandidate0').events.onactivate;
 p.click('TeamPageNext');assert.match(p.nodes.get('TeamPickerPage').text,/2 из 3/);assert.match(p.nodes.get('TeamCandidateName0').text,/Игрок p5/);
 old();assert.equal(ui.draft().players.length,0);assert.equal(ui.draft().draftRevision,before);
 p.click('TeamCandidate0');assert.equal(ui.draft().players[0].id,'p5');p.click('TeamPagePrevious');assert.match(p.nodes.get('TeamPickerPage').text,/1 из 3/);ui.dispose();
});
test('last page hides and clears unused slots and disables next arrow',()=>{
 const p=fixture(),ui=setup(p,6);p.click('TeamPageNext');assert.match(p.nodes.get('TeamCandidateName0').text,/p5/);
 for(let n=1;n<5;n++){assert.equal(p.nodes.get('TeamCandidate'+n).visible,false);assert.equal(p.nodes.get('TeamCandidateName'+n).text,'');}
 assert.equal(p.nodes.get('TeamPageNext').enabled,false);ui.dispose();
});
test('maximum64 catalog has exactly13 pages with no phantom candidates',()=>{
 const p=fixture(),ui=setup(p,64);for(let n=0;n<12;n++)p.click('TeamPageNext');assert.match(p.nodes.get('TeamPickerPage').text,/13 из 13/);
 assert.match(p.nodes.get('TeamCandidateName3').text,/p63/);assert.equal(p.nodes.get('TeamCandidate4').visible,false);ui.dispose();
});
test('five choices disable other candidates but enable remove and clear',()=>{
 const p=fixture(),ui=setup(p);for(let n=0;n<5;n++)assert.equal(ui.choose('p'+n),true);
 assert.match(p.nodes.get('TeamPickerStatus').text,/локальный черновик/);assert.equal(p.nodes.get('TeamClear').enabled,true);
 p.click('TeamPageNext');assert.equal(p.nodes.get('TeamCandidate0').enabled,false);assert.match(p.nodes.get('TeamCandidateHint0').text,/пять/);
 p.click('TeamClear');assert.equal(ui.draft().complete,false);assert.equal(p.nodes.get('TeamCandidate0').enabled,true);ui.dispose();
});
test('duplicate chosen card is disabled and old choose handler has no effect',()=>{
 const p=fixture(),ui=setup(p);const old=p.nodes.get('TeamCandidate0').events.onactivate;p.click('TeamCandidate0');const revision=ui.draft().draftRevision;
 old();assert.equal(ui.draft().draftRevision,revision);assert.equal(p.nodes.get('TeamCandidate0').enabled,false);assert.match(p.nodes.get('TeamCandidateHint0').text,/Уже/);ui.dispose();
});
test('new catalog removes changed selection and clamps page',()=>{
 const p=fixture(),ui=setup(p,12);ui.choose('p0');p.click('TeamPageNext');p.click('TeamPageNext');
 ui.update({revision:1,profiles:[profile('p0',{profileVersion:'v2'})]});assert.match(p.nodes.get('TeamPickerPage').text,/1 из 1/);
 assert.equal(p.nodes.get('TeamSelected0').visible,false);assert.match(p.nodes.get('TeamPickerStatus').text,/выбор.*снят/);ui.dispose();
});
test('invalid newer catalog hides old names, version, source and selected warnings',()=>{
 const p=fixture(),ui=setup(p);ui.choose('p0');const old=p.nodes.get('TeamSelected0').events.onactivate;
 ui.update({revision:1,profiles:[profile('bad',{kind:'fake'})]});assert.equal(ui.draft(),null);
 for(const id of ['TeamCandidateName0','TeamCandidateVersion0','TeamCandidateSource0','TeamSelectedName0','TeamSelectedWarnings0'])assert.equal(p.nodes.get(id).text,'');
 old();assert.match(p.nodes.get('TeamPickerStatus').text,/черновик снят/);ui.dispose();
});
test('valid empty catalog has zero-page navigation and no negative clamp',()=>{
 const p=fixture(),ui=setup(p,0);assert.match(p.nodes.get('TeamPickerPage').text,/Нет записей/);
 for(const id of ['TeamPagePrevious','TeamPageNext','TeamClear'])assert.equal(p.nodes.get(id).enabled,false);
 assert.equal(ui.draft().players.length,0);ui.update({revision:1,profiles:[profile('a')]});assert.match(p.nodes.get('TeamPickerPage').text,/1 из 1/);ui.dispose();
});
test('every dynamic label is plain text and draft copy is independent',()=>{
 const p=fixture(),ui=p.bind();ui.update({revision:0,profiles:[profile('html',{playerName:'<b>Name</b>',sourceLabel:'<a>Source</a>'})]});ui.choose('html');
 assert.equal(p.nodes.get('TeamCandidateName0').text,'<b>Name</b>');for(const [id,node]of p.nodes)if(/^Team(?:Picker(?:Status|Count|Page)|Candidate(?:Name|Version|Source|Coverage|Hint)[0-4]|Selected(?:Name|Version|Warnings|Action)[0-4])$/.test(id))assert.equal(node.html,false,id);
 const draft=ui.draft();draft.players[0].id='bad';assert.equal(ui.draft().players[0].id,'html');ui.dispose();
});
test('duplicate root bind is rejected without closing current owner',()=>{
 const p=fixture(),ui=setup(p);assert.throws(()=>p.bind());assert.equal(ui.isDisposed(),false);assert.equal(p.timers.size,1);ui.dispose();const fresh=p.bind();fresh.dispose();
});
test('missing panel, render or schedule failure cleans partial binding and permits retry',()=>{
 for(const kind of ['missing','render','schedule']){const p=fixture();let missing;
 if(kind==='missing'){missing=p.nodes.get('TeamSelectedWarnings4');p.nodes.delete('TeamSelectedWarnings4');}
 if(kind==='render')p.options.failText='TeamCandidateName0';if(kind==='schedule')p.options.failSchedule=true;
 assert.throws(()=>p.bind(),undefined,kind);assert.equal(p.timers.size,0);if(missing)p.nodes.set('TeamSelectedWarnings4',missing);
 p.options.failText=null;p.options.failSchedule=false;const fresh=p.bind();fresh.dispose();assert.equal(p.timers.size,0);}
});
test('destroyed required panel blocks draft and closes immediately',()=>{
 const p=fixture(),ui=setup(p);ui.choose('p0');p.nodes.get('TeamCandidateName4').valid=false;assert.equal(ui.draft(),null);
 assert.equal(ui.isDisposed(),true);assert.equal(p.timers.size,0);assert.equal(p.root.visible,false);
});
test('destroyed root watcher cancels handlers and timer',()=>{
 const p=fixture(),ui=setup(p);p.root.valid=false;p.tick();assert.equal(ui.isDisposed(),true);assert.equal(p.timers.size,0);
 assert.equal(p.nodes.get('TeamCandidate0').events.onactivate,undefined);
});
test('dispose clears owned labels and stale callbacks do not harm fresh binding',()=>{
 const p=fixture(),ui=setup(p);const old=p.nodes.get('TeamCandidate0').events.onactivate,timer=[...p.timers.values()][0];ui.dispose();
 assert.equal(p.nodes.get('TeamCandidateName0').text,'');const fresh=setup(p);fresh.choose('p1');old();timer.callback();
 assert.equal(fresh.isDisposed(),false);assert.equal(fresh.draft().players[0].id,'p1');assert.equal(p.root.visible,true);fresh.dispose();assert.equal(p.timers.size,0);
});
test('input getter disposal and fresh rebind cannot repaint the new panel',()=>{
 const p=fixture(),old=setup(p);let fresh;const row=profile('old');Object.defineProperty(row,'playerName',{enumerable:true,get(){
 old.dispose();fresh=p.bind();fresh.update({revision:0,profiles:[profile('new')]});fresh.choose('new');return 'OLD';}});
 assert.equal(old.update({revision:1,profiles:[row]}),false);assert.equal(fresh.isDisposed(),false);
 assert.match(p.nodes.get('TeamCandidateName0').text,/Игрок new/);assert.equal(fresh.draft().players[0].id,'new');fresh.dispose();assert.equal(p.timers.size,0);
});
test('reentrant renderer update keeps newer rendering and active watcher',()=>{
 const p=fixture(),ui=setup(p);let fired=false;p.options.onText=(id,value)=>{
 if(!fired&&id==='TeamCandidateName0'&&value==='Игрок old'){fired=true;ui.update({revision:2,profiles:[profile('new')]});}};
 assert.equal(ui.update({revision:1,profiles:[profile('old')]}),false);
 assert.match(p.nodes.get('TeamCandidateName0').text,/Игрок new/);assert.equal(ui.isDisposed(),false);assert.equal(p.timers.size,1);ui.dispose();
});
test('update invalidates old candidate before reading a revision getter',()=>{
 const p=fixture(),ui=setup(p);const old=p.nodes.get('TeamCandidate0').events.onactivate;
 const next={get revision(){old();return 1;},profiles:[profile('new')]};
 assert.equal(ui.update(next),true);assert.equal(ui.draft().players.length,0);assert.match(p.nodes.get('TeamCandidateName0').text,/Игрок new/);ui.dispose();
});
test('old remove handler cannot remove a newly selected version of the same id',()=>{
 const p=fixture(),ui=setup(p);ui.choose('p0');const old=p.nodes.get('TeamSelected0').events.onactivate;
 ui.update({revision:1,profiles:[profile('p0',{profileVersion:'v2'})]});ui.choose('p0');old();
 assert.equal(ui.draft().players[0].profileVersion,'v2');ui.dispose();
});
