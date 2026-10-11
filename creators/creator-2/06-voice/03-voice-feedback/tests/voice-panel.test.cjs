const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const c2=path.resolve(__dirname,'../../..');
const script='src/panorama/scripts/custom_game/';
const files=[path.join(c2,'02-coach-interface/01-roster-cards',script,'roster_cards_state.js'),path.join(c2,'06-voice/02-recognition-parser',script,'voice_text_state.js'),path.join(__dirname,'..',script,'voice_text_panel.js')];
const labels=['Status','Normalized','Address','Action','Hint'];
function fixture(options={}) {
 const nodes=new Map(),timers=new Map(),nativeCalls=[];let timerId=0;
 function panel(id) {
  let text='';return {id,valid:true,visible:true,enabled:true,html:true,events:{},IsValid(){return this.valid;},SetPanelEvent(k,f){this.events[k]=f;},ClearPanelEvent(k){delete this.events[k];},get text(){if(options.onRead)options.onRead(id);return text;},set text(v){if(options.failText===id)throw Error('write');text=v;if(options.onText)options.onText(id,v);}};
 }
 const root=panel('VoiceTextRoot');root.FindChildTraverse=id=>{if(options.onFind)options.onFind(id);return nodes.get(id)||null;};
 ['Input','PreviewButton','ClearButton',...labels].forEach(name=>nodes.set('VoiceText'+name,panel('VoiceText'+name)));
 const dollar={Schedule(delay,callback){if(options.failSchedule)throw Error('schedule');if(options.badHandle)return null;const h=timerId++;timers.set(h,{delay,callback});if(options.onSchedule)options.onSchedule(delay);return h;},CancelScheduled(handle){timers.delete(handle);}};
 const native=new Proxy({}, {get(_t,k){nativeCalls.push(String(k));throw Error('Native forbidden');}});
 const context=vm.createContext({$:dollar,Game:native,GameEvents:native,Players:native,Entities:native});
 files.forEach(file=>vm.runInContext(fs.readFileSync(file,'utf8'),context));
 return {root,nodes,timers,nativeCalls,options,bind:()=>context.DotaCoachVoicePanels.bind(root),click(){nodes.get('VoiceTextPreviewButton').events.onactivate?.();},clearClick(){nodes.get('VoiceTextClearButton').events.onactivate?.();},fire(){const [h,t]=timers.entries().next().value;timers.delete(h);t.callback();}};
}
function player(id='a',playerName='Альфа',role=1,extra={}){return {id,playerName,heroName:'Synthetic',role,source:'synthetic',side:'own',availability:'alive',...extra};}
function snapshot(revision=1,players=[player()]){return {revision,players};}
function event(text='Альфа фарми',extra={}){return {utteranceId:'asr-final-1',text,rosterRevision:1,final:true,...extra};}
function prepared(p){const ui=p.bind();assert.equal(ui.updateRoster(snapshot()),true);return ui;}
function plain(v){return JSON.parse(JSON.stringify(v));}

test('load inert; bind empty source disables preview and one watcher has integer zero handle',()=>{
 const p=fixture();assert.equal(p.timers.size,0);const ui=p.bind();assert.equal(p.nodes.get('VoiceTextPreviewButton').enabled,false);assert.match(p.nodes.get('VoiceTextHint').text,/Микрофон не подключён/);assert.equal(p.timers.size,1);assert.equal(p.timers.has(0),true);assert.deepEqual(p.nativeCalls,[]);ui.dispose();assert.equal(p.timers.size,0);
});
test('actual input/button previews one local command with player name and action',()=>{
 const p=fixture(),ui=prepared(p);p.nodes.get('VoiceTextInput').text='КЕРРИ, отступай';p.click();
 assert.match(p.nodes.get('VoiceTextStatus').text,/Предложение готово/);assert.equal(p.nodes.get('VoiceTextNormalized').text,'керри отступай');assert.equal(p.nodes.get('VoiceTextAddress').text,'Альфа');assert.equal(p.nodes.get('VoiceTextAction').text,'Отступление');assert.equal(ui.view().parser.consumed,1);assert.deepEqual(p.nativeCalls,[]);ui.dispose();
});
test('unknown ambiguous unavailable and negative commands show local failure without stale actor',()=>{
 const p=fixture(),ui=prepared(p);assert.equal(ui.preview('Альфа фарми'),true);
 assert.equal(ui.preview('Альфа атакуй'),false);assert.match(p.nodes.get('VoiceTextStatus').text,/Действие не распознано/);assert.equal(p.nodes.get('VoiceTextAddress').text,'');
 assert.equal(ui.updateRoster(snapshot(2,[player(),player('b','Альфа',2)])),true);assert.equal(ui.preview('Альфа фарми'),false);assert.match(p.nodes.get('VoiceTextStatus').text,/Адресат неоднозначен/);
 assert.equal(ui.updateRoster(snapshot(3,[player('a','Альфа',1,{availability:'dead'})])),true);assert.equal(ui.preview('Альфа фарми'),false);assert.match(p.nodes.get('VoiceTextStatus').text,/Адресат недоступен/);assert.equal(ui.preview('Альфа не фарми'),false);assert.match(p.nodes.get('VoiceTextStatus').text,/Отрицание/);ui.dispose();
});
test('source update clears typed input and proposal before reading source; nested calls do not read DTO',()=>{
 const p=fixture(),ui=prepared(p);ui.preview('Альфа фарми');p.nodes.get('VoiceTextInput').text='Альфа отступай';let reads=0;
 const data=new Proxy(snapshot(2,[player('b','Альфа')]),{getOwnPropertyDescriptor(t,k){assert.equal(p.root.visible,false);assert.equal(p.nodes.get('VoiceTextInput').text,'');for(const name of labels)assert.equal(p.nodes.get('VoiceText'+name).text,'');assert.equal(ui.preview('Альфа фарми'),false);assert.equal(ui.updateRoster(new Proxy({}, {getOwnPropertyDescriptor(){reads++;throw Error('nested');}})),false);assert.equal(ui.view(),null);return Reflect.getOwnPropertyDescriptor(t,k);}});
 assert.equal(ui.updateRoster(data),true);assert.equal(reads,0);assert.equal(ui.view().result,null);assert.equal(p.nodes.get('VoiceTextInput').text,'');ui.dispose();
});
test('failed source closes input gate despite parser preserving prior snapshot; newer valid source recovers',()=>{
 const p=fixture(),ui=prepared(p);assert.equal(ui.updateRoster({}),false);assert.equal(ui.view().sourceReady,false);assert.equal(ui.preview('Альфа фарми'),false);assert.equal(p.nodes.get('VoiceTextPreviewButton').enabled,false);assert.equal(p.nodes.get('VoiceTextInput').enabled,false);assert.equal(ui.updateRoster(snapshot(2)),true);assert.equal(ui.preview('Альфа фарми'),true);ui.dispose();
});
test('incoming final text preserves ID revision and duplicate/stale outcomes; interim is not ready',()=>{
 const p=fixture(),ui=prepared(p);assert.equal(ui.receive(event('Альфа фарми',{final:false})),false);assert.match(p.nodes.get('VoiceTextStatus').text,/Промежуточный/);assert.equal(ui.receive(event()),true);assert.equal(ui.receive(event()),false);assert.match(p.nodes.get('VoiceTextStatus').text,/Повтор/);
 assert.equal(ui.updateRoster(snapshot(2)),true);assert.equal(ui.receive(event('Альфа фарми',{utteranceId:'stale'})),false);assert.match(p.nodes.get('VoiceTextStatus').text,/Состав изменился/);assert.equal(ui.view().result.proposal,null);ui.dispose();
});
test('clear actual callback clears local preview but preserves final ID history',()=>{
 const p=fixture(),ui=prepared(p);ui.receive(event());p.clearClick();assert.equal(ui.view().result,null);assert.equal(ui.view().parser.consumed,1);assert.equal(ui.receive(event()),false);assert.match(p.nodes.get('VoiceTextStatus').text,/Повтор/);ui.dispose();
});
test('plaintext captured recipient names and copied view never become markup or alias state',()=>{
 const p=fixture(),ui=p.bind();ui.updateRoster(snapshot(1,[player('a','<b>Альфа</b>')]));assert.equal(ui.preview('керри фарми'),true);assert.equal(p.nodes.get('VoiceTextAddress').text,'<b>Альфа</b>');assert.equal(p.nodes.get('VoiceTextAddress').html,false);
 const v=ui.view();v.result.proposal.recipientNames[0]='bad';assert.equal(ui.view().result.proposal.recipientNames[0],'<b>Альфа</b>');ui.dispose();
});
test('hidden invalid or replaced required nodes close panel before event DTO reads',()=>{
 for(const mode of ['hidden','invalid','replace']){const p=fixture(),ui=prepared(p);const node=p.nodes.get('VoiceTextHint');if(mode==='hidden')node.visible=false;if(mode==='invalid')node.valid=false;if(mode==='replace')p.nodes.set('VoiceTextHint',{...node});let reads=0;assert.equal(ui.receive(new Proxy({}, {getOwnPropertyDescriptor(){reads++;throw Error('read');}})),false);assert.equal(reads,0);assert.equal(ui.isDisposed(),true);assert.equal(p.timers.size,0);}
});
test('source repaint expires saved preview handler without reading old/new input',()=>{
 const p=fixture(),ui=prepared(p);const old=p.nodes.get('VoiceTextPreviewButton').events.onactivate;ui.updateRoster(snapshot(2));let reads=0;p.options.onRead=()=>reads++;old();assert.equal(reads,0);assert.equal(ui.view().parser.consumed,0);ui.dispose();
});
test('dispose cleanup and cancelled callbacks cannot touch fresh owner',()=>{
 const p=fixture(),ui=prepared(p);ui.preview('Альфа фарми');const oldButton=p.nodes.get('VoiceTextPreviewButton').events.onactivate,oldTimer=[...p.timers.values()][0].callback;ui.dispose();assert.equal(p.root.visible,false);for(const name of labels)assert.equal(p.nodes.get('VoiceText'+name).text,'');assert.equal(p.nodes.get('VoiceTextInput').text,'');assert.equal(p.timers.size,0);
 const fresh=prepared(p);oldButton();oldTimer();assert.equal(fresh.isDisposed(),false);assert.equal(p.timers.size,1);assert.equal(fresh.view().parser.consumed,0);fresh.dispose();
});
test('duplicate root rejects without damaging owner and watcher detects deleted required node',()=>{
 const p=fixture(),ui=prepared(p);assert.throws(()=>p.bind(),/already bound/);assert.equal(ui.isDisposed(),false);p.nodes.get('VoiceTextInput').valid=false;p.fire();assert.equal(ui.isDisposed(),true);assert.equal(p.timers.size,0);
});
test('partial discovery setter and schedule failures release owner and clean up',()=>{
 for(const kind of ['missing','text','schedule','handle']){const p=fixture();let removed;if(kind==='missing'){removed=p.nodes.get('VoiceTextHint');p.nodes.delete('VoiceTextHint');}if(kind==='text')p.options.failText='VoiceTextAction';if(kind==='schedule')p.options.failSchedule=true;if(kind==='handle')p.options.badHandle=true;assert.throws(()=>p.bind());assert.equal(p.timers.size,0);if(removed)p.nodes.set('VoiceTextHint',removed);p.options.failText=null;p.options.failSchedule=false;p.options.badHandle=false;p.bind().dispose();}
});
test('renderer nested updates/previews reject and original resolved actor stays consistent',()=>{
 const p=fixture(),ui=prepared(p);let fired=false;p.options.onText=(id,text)=>{if(!fired&&id==='VoiceTextAddress'&&text==='Альфа'){fired=true;assert.equal(ui.updateRoster(snapshot(2,[player('b','Бета')])),false);assert.equal(ui.preview('Альфа отступай'),false);}};assert.equal(ui.preview('Альфа фарми'),true);assert.equal(ui.view().result.proposal.recipientIds[0],'a');assert.equal(ui.view().parser.consumed,1);ui.dispose();
});
test('input getter disposal closes before parse and new bind remains untouched',()=>{
 const p=fixture(),ui=prepared(p);let fresh,once=false;p.options.onRead=id=>{if(id==='VoiceTextInput'&&!once){once=true;ui.dispose();fresh=prepared(p);}};p.click();assert.equal(ui.isDisposed(),true);assert.equal(fresh.isDisposed(),false);assert.equal(fresh.view().parser.consumed,0);fresh.dispose();
});
test('source descriptor disposal plus fresh bind cannot repaint old results',()=>{
 const p=fixture(),ui=prepared(p);let fresh,once=false;const data=new Proxy(snapshot(2),{getOwnPropertyDescriptor(t,k){if(!once){once=true;ui.dispose();fresh=prepared(p);}return Reflect.getOwnPropertyDescriptor(t,k);}});assert.equal(ui.updateRoster(data),false);assert.equal(fresh.isDisposed(),false);assert.equal(fresh.view().parser.revision,1);assert.equal(p.timers.size,1);fresh.dispose();
});
test('late schedule handle after synchronous disposal is cancelled',()=>{
 const p=fixture(),ui=prepared(p);p.options.onSchedule=()=>ui.dispose();p.fire();assert.equal(ui.isDisposed(),true);assert.equal(p.timers.size,0);
});
test('capacity disables local preview and clear does not reset history',()=>{
 const p=fixture(),ui=prepared(p);for(let i=0;i<128;i++)assert.equal(ui.preview('Альфа фарми'),true);assert.equal(p.nodes.get('VoiceTextPreviewButton').enabled,false);ui.clear();assert.equal(ui.view().parser.consumed,128);assert.equal(p.nodes.get('VoiceTextPreviewButton').enabled,false);ui.dispose();
});

test('busy nested APIs reject before native tree reads',()=>{
 const p=fixture(),ui=prepared(p);let once=false;
 const data=new Proxy(snapshot(2),{getOwnPropertyDescriptor(t,k){if(!once){once=true;let reads=0;p.options.onFind=()=>reads++;assert.equal(ui.preview('Альфа фарми'),false);assert.equal(ui.updateRoster(snapshot(3)),false);assert.equal(ui.receive(event()),false);assert.equal(ui.clear(),false);assert.equal(ui.view(),null);assert.equal(ui.isDisposed(),false);p.options.onFind=null;assert.equal(reads,0);}return Reflect.getOwnPropertyDescriptor(t,k);}});
 assert.equal(ui.updateRoster(data),true);ui.dispose();
});

test('mutation reserves busy before native preflight can reenter another update',()=>{
 const p=fixture(),ui=prepared(p);let once=false,nested;
 p.options.onFind=()=>{if(!once){once=true;nested=ui.updateRoster(snapshot(3));}};
 assert.equal(ui.updateRoster(snapshot(2)),true);assert.equal(nested,false);assert.equal(ui.view().parser.revision,2);ui.dispose();
});

test('externally hidden root fails closed before event DTO is read',()=>{
 const p=fixture(),ui=prepared(p);p.root.visible=false;let reads=0;assert.equal(ui.receive(new Proxy({}, {getOwnPropertyDescriptor(){reads++;throw Error('read');}})),false);assert.equal(reads,0);assert.equal(ui.isDisposed(),true);assert.equal(p.timers.size,0);
});
