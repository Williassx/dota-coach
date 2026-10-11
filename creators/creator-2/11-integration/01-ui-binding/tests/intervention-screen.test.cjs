'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),test=require('node:test'),assert=require('node:assert/strict');
const library=path.resolve(__dirname,'../../..');
function scene(options={}) {
    const nodes=new Map(),timers=new Map();let serial=0;
    function node(id){let text='';const item={id,valid:true,visible:true,enabled:false,events:{},classes:new Set(),
        IsValid(){return this.valid;},FindChildTraverse(id){return nodes.get(id);},
        SetPanelEvent(name,fn){this.events[name]=fn;},ClearPanelEvent(name){delete this.events[name];},
        SetHasClass(name,on){if(on)this.classes.add(name);else this.classes.delete(name);},
        get text(){return text;},set text(value){if(options.failText===id)throw Error('paint');text=value;if(options.onText)options.onText(id,value);}};
        nodes.set(id,item);return item;}
    const root=node('CoachInterventionScreen'),roster=node('CoachInterventionRoster'),manual=node('ManualRequestRoot');
    node('CoachInterventionStatus');node('RosterStatus');
    for(let i=0;i<5;i++){node('RosterCard'+i);for(const name of ['Name','Hero','Role','Source','Availability','Hint'])node('Roster'+name+i);}
    for(const name of ['Recipient','Mode','Actor','State','Reason','Message','Hint','Button'])node('ManualRequest'+name);
    const deny=new Proxy({}, {get(){throw Error('native');}});
    const context=vm.createContext({Game:deny,GameUI:deny,GameEvents:deny,Entities:deny,$:{
        Schedule(delay,callback){if(options.failDelay===delay)throw Error('schedule');const handle=++serial;timers.set(handle,{delay,callback});return handle;},
        CancelScheduled(handle){timers.delete(handle);}
    }});
    for(const [section,file] of [
        ['02-coach-interface/01-roster-cards','roster_cards_state.js'],['02-coach-interface/01-roster-cards','roster_cards.js'],
        ['02-coach-interface/02-status-orders','orders_state.js'],['05-intervention-ui/01-request-ack','intervention_request_state.js'],
        ['05-intervention-ui/01-request-ack','intervention_request_panel.js'],['11-integration/01-ui-binding','preparation_panel_port.js'],
        ['11-integration/01-ui-binding','intervention_selection_state.js'],['11-integration/01-ui-binding','intervention_screen_binding.js']
    ]) {const filePath=path.join(library,section,'src/panorama/scripts/custom_game',file);
        if(file==='intervention_screen_binding.js'&&!fs.existsSync(filePath))continue;
        vm.runInContext(fs.readFileSync(filePath,'utf8'),context);}
    return {root,roster,manual,nodes,timers,options,context,flow:context.DotaCoachInterventionSelection.create(true),
        bindRoster(observer){return context.DotaCoachRosterPanels.bind(roster,observer,this.flow.rosterPort());},
        bind(send){assert.ok(context.DotaCoachInterventionScreenPanels,'screen binding missing');return context.DotaCoachInterventionScreenPanels.bind(root,send);},
        click(id){const fn=nodes.get(id).events.onactivate;assert.equal(typeof fn,'function',id);fn();},
        fire(delay){const timer=[...timers].find(([,r])=>r.delay===delay);assert.ok(timer);timers.delete(timer[0]);timer[1].callback();}
    };
}
function card(id='a',extra={}){return {id,playerName:'Игрок '+id,heroName:'Axe',role:3,source:'synthetic',side:'own',availability:'alive',...extra};}
function frame(id='a',extra={}){return {id,playerName:'Игрок '+id,mode:'AI',epoch:1,revision:1,side:'own',availability:'alive',...extra};}
function ready(ui){ui.replaceRoster([card(),card('b')]);ui.updateControl(frame());ui.updateControl(frame('b'));ui.selectPlayer('a');}

test('stable roster port and actual card click select the same private flow',()=>{
    const p=scene();assert.equal(p.flow.rosterPort(),p.flow.rosterPort());
    const ui=p.bindRoster();ui.replace([card(),card('b')]);p.click('RosterCard1');
    assert.equal(p.flow.view().roster.selectedId,'b');ui.clearSelection();assert.equal(p.flow.view().roster.selectedId,null);
    ui.dispose();assert.equal(p.flow.isDisposed(),true);
});
test('port refresh displays external selection and expires previous generation click',()=>{
    const p=scene(),ui=p.bindRoster();ui.replace([card(),card('b')]);const saved=p.nodes.get('RosterCard0').events.onactivate;
    p.flow.selectPlayer('b');assert.equal(ui.refresh(),true);saved();assert.equal(p.flow.view().roster.selectedId,'b');
    assert.equal(p.nodes.get('RosterCard1').classes.has('RosterSelected'),true);ui.dispose();
});
test('roster source getters see hidden blank staging and cannot reenter selection',()=>{
    const p=scene(),ui=p.bindRoster();ui.replace([card()]);const data=card('b');let reads=0;
    Object.defineProperty(data,'source',{enumerable:true,get(){assert.equal(p.roster.visible,false);
        assert.equal(p.nodes.get('RosterName0').text,'');assert.equal(ui.select('a'),false);
        assert.equal(ui.replace(new Proxy([], {get(){reads++;throw Error('nested');}})),false);return 'synthetic';}});
    assert.equal(ui.replace([data]),true);assert.equal(reads,0);ui.dispose();
});
test('missing off-page required label stops old click and closes shared flow',()=>{
    const p=scene(),ui=p.bindRoster();ui.replace([card()]);const saved=p.nodes.get('RosterCard0').events.onactivate;
    p.nodes.get('RosterHint4').valid=false;saved();assert.equal(ui.isDisposed(),true);assert.equal(p.flow.isDisposed(),true);
});
test('duplicate roster port on another root does not dispose its original owner',()=>{
    const p=scene(),ui=p.bindRoster();assert.throws(()=>p.context.DotaCoachRosterPanels.bind(p.root,null,p.flow.rosterPort()));
    assert.equal(p.flow.isDisposed(),false);assert.equal(ui.isDisposed(),false);ui.dispose();
});
test('roster suspend prevents actions and refresh restores the shared view',()=>{
    const p=scene(),ui=p.bindRoster();ui.replace([card()]);assert.equal(ui.suspend(),true);assert.equal(p.roster.visible,false);
    assert.equal(ui.select('a'),false);assert.equal(ui.refresh(),true);p.click('RosterCard0');
    assert.equal(p.flow.view().roster.selectedId,'a');ui.dispose();
});
test('roster reentrant repaint keeps the newer generation',()=>{
    const p=scene(),ui=p.bindRoster();let changed=false;
    p.options.onText=(id,value)=>{if(!changed&&id==='RosterName0'&&value==='Игрок a'){
        changed=true;ui.replace([card('b')]);}};
    assert.equal(ui.replace([card()]),false);assert.equal(p.nodes.get('RosterName0').text,'Игрок b');ui.dispose();
});
test('two-pane actual card click updates the request recipient without sending',()=>{
    const p=scene(),sent=[];const ui=p.bind(intent=>sent.push(intent));ready(ui);p.click('RosterCard1');
    assert.equal(ui.view().roster.selectedId,'b');assert.match(p.nodes.get('ManualRequestRecipient').text,/\[b\]/);
    assert.equal(sent.length,0);p.click('ManualRequestButton');assert.equal(sent.length,1);
    assert.equal(sent[0].recipientId,'b');assert.equal(ui.view().manual.request.recipientId,'b');ui.dispose();
});
test('same screen keeps captured actor on card switch and late ACK',()=>{
    const p=scene();let reply;const ui=p.bind((_,cb)=>reply=cb);ready(ui);p.click('ManualRequestButton');p.click('RosterCard1');
    assert.match(p.nodes.get('ManualRequestRecipient').text,/\[b\]/);assert.match(p.nodes.get('ManualRequestActor').text,/\[a\]/);
    assert.equal(reply({sequence:0,stage:'accepted',reason:null}),true);assert.equal(ui.view().manual.status,'accepted');ui.dispose();
});
test('parent transaction blanks both panes before DTO getters and rejects nested calls',()=>{
    const p=scene(),ui=p.bind(()=>{});ready(ui);const data=frame('a',{revision:2});let reads=0;
    Object.defineProperty(data,'mode',{enumerable:true,get(){assert.equal(p.roster.visible,false);assert.equal(p.manual.visible,false);
        assert.equal(p.nodes.get('RosterName0').text,'');assert.equal(p.nodes.get('ManualRequestRecipient').text,'');
        assert.equal(ui.view(),null);assert.equal(ui.selectPlayer('b'),false);assert.equal(ui.request(),false);
        assert.equal(ui.updateControl(new Proxy({}, {get(){reads++;throw Error('nested');}})),false);return 'AI';}});
    assert.equal(ui.updateControl(data),true);assert.equal(reads,0);assert.equal(p.root.visible,true);ui.dispose();
});
test('clearing selection disables request while preserving unresolved actor',()=>{
    const p=scene(),ui=p.bind(()=>{});ready(ui);p.click('ManualRequestButton');assert.equal(ui.clearSelection(),true);
    assert.equal(ui.view().roster.selectedId,null);assert.equal(ui.view().manual.request.recipientId,'a');
    assert.equal(p.nodes.get('ManualRequestButton').enabled,false);ui.dispose();
});
test('required child destruction closes entire group before another DTO is read',()=>{
    const p=scene(),ui=p.bind(()=>{});ready(ui);p.click('ManualRequestButton');p.nodes.get('RosterHint4').valid=false;
    let reads=0;assert.equal(ui.updateControl(new Proxy({}, {get(){reads++;throw Error('stale');}})),false);
    assert.equal(reads,0);assert.equal(ui.isDisposed(),true);assert.equal(p.timers.size,0);assert.equal(p.manual.visible,false);
});
test('old handler reply and timers do not touch a fresh group on the released root',()=>{
    const p=scene();let reply;const ui=p.bind((_,cb)=>reply=cb);ready(ui);
    const saved=p.nodes.get('RosterCard1').events.onactivate;p.click('ManualRequestButton');const timers=[...p.timers.values()];
    ui.dispose();const fresh=p.bind(()=>{});ready(fresh);saved();for(const row of timers)row.callback();let reads=0;
    assert.equal(reply(new Proxy({}, {get(){reads++;throw Error('old');}})),false);assert.equal(reads,0);
    assert.equal(fresh.view().roster.selectedId,'a');assert.equal(fresh.isDisposed(),false);assert.equal(p.timers.size,2);fresh.dispose();
});
test('already owned manual scope survives partial group bind failure',()=>{
    const p=scene();const independent=p.context.DotaCoachInterventionRequestPanels.bind(p.manual);
    assert.throws(()=>p.bind(()=>{}));assert.equal(independent.isDisposed(),false);assert.equal(p.root.visible,true);
    independent.dispose();const fresh=p.bind(()=>{});assert.equal(fresh.isDisposed(),false);fresh.dispose();
});
test('duplicate group root leaves initial group functioning',()=>{
    const p=scene(),ui=p.bind(()=>{});assert.throws(()=>p.bind(()=>{}));ready(ui);
    assert.equal(ui.request(),true);assert.equal(ui.isDisposed(),false);ui.dispose();
});
test('parent watcher scheduling failure cleans children for a successful retry',()=>{
    const p=scene({failDelay:0.25});assert.throws(()=>p.bind(()=>{}));assert.equal(p.timers.size,0);
    p.options.failDelay=null;const ui=p.bind(()=>{});assert.equal(ui.isDisposed(),false);ui.dispose();
});
test('source getter disposal and immediate rebind cannot repaint the new group',()=>{
    const p=scene(),ui=p.bind(()=>{});ready(ui);let fresh;const data=frame('a',{revision:2});
    Object.defineProperty(data,'mode',{enumerable:true,get(){ui.dispose();fresh=p.bind(()=>{});ready(fresh);return 'AI';}});
    assert.equal(ui.updateControl(data),false);assert.equal(fresh.isDisposed(),false);
    assert.match(p.nodes.get('ManualRequestRecipient').text,/\[a\]/);assert.equal(p.timers.size,2);fresh.dispose();
});
test('hidden required roster label closes shared flow before selection',()=>{
    const p=scene(),ui=p.bindRoster();ui.replace([card()]);const click=p.nodes.get('RosterCard0').events.onactivate;
    p.nodes.get('RosterHint4').visible=false;click();assert.equal(ui.isDisposed(),true);assert.equal(p.flow.isDisposed(),true);
});
test('observer exception after a successful repaint closes the current roster owner',()=>{
    const p=scene();let fail=false;const ui=p.bindRoster(()=>{if(fail)throw Error('observer');});fail=true;
    assert.equal(ui.replace([card()]),false);assert.equal(ui.isDisposed(),true);assert.equal(p.flow.isDisposed(),true);
});
test('group watcher refreshes request summary after an ACK deadline',()=>{
    const p=scene(),ui=p.bind(()=>{});ready(ui);p.click('ManualRequestButton');p.fire(5);
    p.fire(0.25);p.fire(0.25);assert.match(p.nodes.get('CoachInterventionStatus').text,/неизвестен/);ui.dispose();
});
