'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const test=require('node:test'),assert=require('node:assert/strict');
const library=path.resolve(__dirname,'../../..');
const labels=['Recipient','Mode','Actor','State','Reason','Message','Hint'];
function fixture(options={}) {
    const timers=new Map();let serial=0;
    const deny=new Proxy({}, {get(){throw Error('native access');}});
    const context=vm.createContext({Game:deny,GameUI:deny,GameEvents:deny,Entities:deny,$:{
        Schedule(delay,callback){const handle=++serial;timers.set(handle,{delay,callback});return handle;},
        CancelScheduled(handle){timers.delete(handle);}
    }});
    for(const [section,file] of [
        ['02-coach-interface/01-roster-cards','roster_cards_state.js'],
        ['02-coach-interface/02-status-orders','orders_state.js'],
        ['05-intervention-ui/01-request-ack','intervention_request_state.js'],
        ['11-integration/01-ui-binding','intervention_selection_state.js'],
        ['11-integration/01-ui-binding','preparation_panel_port.js'],
        ['05-intervention-ui/01-request-ack','intervention_request_panel.js']
    ]) vm.runInContext(fs.readFileSync(path.join(library,section,'src/panorama/scripts/custom_game',file),'utf8'),context);
    function tree(){const nodes=new Map();
        function node(id){let text='';const item={id,valid:true,visible:true,enabled:false,events:{},
            IsValid(){return this.valid;},FindChildTraverse(id){return nodes.get(id);},
            SetPanelEvent(key,callback){this.events[key]=callback;},ClearPanelEvent(key){delete this.events[key];},
            get text(){return text;},set text(value){text=value;if(options.onText)options.onText(id,value);}};
            nodes.set(id,item);return item;}
        const root=node('ManualRequestRoot');for(const name of [...labels,'Button'])node('ManualRequest'+name);
        return {root,nodes};
    }
    const scene=tree(),flow=context.DotaCoachInterventionSelection.create(true);
    return {...scene,flow,timers,tree,options,
        bind(send=()=>{},port=flow.requestPort(),sceneOverride=scene){return context.DotaCoachInterventionRequestPanels.bind(sceneOverride.root,send,port);},
        bindWithoutSend(){return context.DotaCoachInterventionRequestPanels.bind(scene.root,undefined,flow.requestPort());},
        text(name){return scene.nodes.get('ManualRequest'+name).text;},
        click(){const fn=scene.nodes.get('ManualRequestButton').events.onactivate;assert.equal(typeof fn,'function');fn();},
        fire(delay){const row=[...timers].find(([,v])=>v.delay===delay);assert.ok(row);timers.delete(row[0]);row[1].callback();}
    };
}
function card(id='a',extra={}){return {id,playerName:'Игрок '+id,heroName:'Axe',role:3,source:'synthetic',side:'own',availability:'alive',...extra};}
function frame(id='a',extra={}){return {id,playerName:'Игрок '+id,mode:'AI',epoch:1,revision:1,side:'own',availability:'alive',...extra};}
function response(stage='accepted'){return {sequence:0,stage,reason:stage==='rejected'?'Отказ':null};}
function ready(p){p.flow.replaceRoster([card(),card('b')]);p.flow.updateControl(frame());p.flow.updateControl(frame('b'));p.flow.selectPlayer('a');}

test('one stable narrow port delegates without a second selected state',()=>{
    const p=fixture();const port=p.flow.requestPort();assert.equal(port,p.flow.requestPort());
    ready(p);assert.equal(port.view().selected.id,'a');assert.equal(port.select('b'),true);
    assert.equal(p.flow.view().roster.selectedId,'b');assert.equal(port.view().selected.id,'b');
    port.dispose();assert.equal(p.flow.isDisposed(),true);assert.equal(port.isDisposed(),true);
});
test('actual shared panel click creates a request in the supplied flow',()=>{
    const p=fixture(),sent=[];ready(p);const ui=p.bind((intent,reply)=>sent.push({intent,reply}));
    assert.match(p.text('Recipient'),/\[a\]/);p.click();assert.equal(sent.length,1);
    assert.equal(p.flow.view().manual.request.ticket,sent[0].intent.ticket);
    assert.equal(p.flow.view().manual.request.recipientId,'a');assert.equal(p.timers.size,2);ui.dispose();
});
test('shared gate keeps dead roster disabled despite live control',()=>{
    const p=fixture();p.flow.replaceRoster([card('a',{availability:'dead'})]);p.flow.updateControl(frame());p.flow.selectPlayer('a');
    let sends=0;const ui=p.bind(()=>sends++);assert.equal(p.nodes.get('ManualRequestButton').enabled,false);
    assert.equal(ui.request(),false);assert.equal(sends,0);assert.match(p.text('Message'),/недоступна/);ui.dispose();
});
test('external selection refresh changes recipient but retains captured actor and ACK',()=>{
    const p=fixture();let reply;ready(p);const ui=p.bind((_,cb)=>reply=cb);p.click();
    p.flow.selectPlayer('b');assert.equal(ui.refresh(),true);assert.match(p.text('Recipient'),/\[b\]/);
    assert.match(p.text('Actor'),/\[a\]/);assert.equal(reply(response()),true);
    assert.equal(p.flow.view().manual.status,'accepted');assert.match(p.text('State'),/MANUAL.*не подтверждён/);ui.dispose();
});
test('stale displayed recipient first refreshes without dispatch and needs another click',()=>{
    const p=fixture(),sent=[];ready(p);const ui=p.bind(intent=>sent.push(intent));
    const saved=p.nodes.get('ManualRequestButton').events.onactivate;p.flow.selectPlayer('b');saved();
    assert.equal(sent.length,0);assert.equal(p.flow.view().manual.request,null);assert.match(p.text('Recipient'),/\[b\]/);
    saved();assert.equal(sent.length,0);p.click();assert.equal(sent.length,1);assert.equal(sent[0].recipientId,'b');ui.dispose();
});
test('newer control revision behind the displayed frame also requires a refreshed action',()=>{
    const p=fixture();let sends=0;ready(p);const ui=p.bind(()=>sends++);
    p.flow.updateControl(frame('a',{revision:2}));assert.equal(ui.request(),false);assert.equal(sends,0);
    assert.equal(ui.request(),true);assert.equal(sends,1);ui.dispose();
});
test('invalid external roster refresh disables request with shared reason',()=>{
    const p=fixture();let sends=0;ready(p);const ui=p.bind(()=>sends++);
    p.flow.replaceRoster([]);assert.equal(ui.refresh(),true);assert.equal(ui.request(),false);
    assert.equal(sends,0);assert.equal(p.nodes.get('ManualRequestButton').enabled,false);ui.dispose();
});
test('external MANUAL observation refresh cancels ACK timer without granting input',()=>{
    const p=fixture();let reply;ready(p);const ui=p.bind((_,cb)=>reply=cb);p.click();
    p.flow.updateControl(frame('a',{revision:2,mode:'MANUAL'}));assert.equal(ui.refresh(),true);
    assert.equal(p.timers.size,1);assert.match(p.text('State'),/право ввода не подтверждено/);
    let reads=0;assert.equal(reply(new Proxy({}, {get(){reads++;throw Error('stale');}})),false);
    assert.equal(reads,0);ui.dispose();
});
test('shared timeout and late ACK update the same captured request',()=>{
    const p=fixture();let reply;ready(p);const ui=p.bind((_,cb)=>reply=cb);p.click();p.fire(5);
    assert.equal(p.flow.view().manual.status,'unknown');assert.equal(reply(response()),true);
    assert.equal(p.flow.view().manual.status,'accepted');assert.equal(p.timers.size,1);ui.dispose();
});
test('duplicate port rejected on another tree preserves original flow and owner',()=>{
    const p=fixture();ready(p);const ui=p.bind();assert.throws(()=>p.bind(()=>{},p.flow.requestPort(),p.tree()));
    assert.equal(p.flow.isDisposed(),false);assert.equal(ui.isDisposed(),false);assert.equal(ui.request(),true);ui.dispose();
});
test('panel disposal closes the flow, cancels timers and ignores old callbacks',()=>{
    const p=fixture();let reply;ready(p);const ui=p.bind((_,cb)=>reply=cb);p.click();
    const callbacks=[...p.timers.values()].map(v=>v.callback);ui.dispose();assert.equal(p.flow.isDisposed(),true);
    assert.equal(p.timers.size,0);for(const callback of callbacks)callback();let reads=0;
    assert.equal(reply(new Proxy({}, {get(){reads++;throw Error('closed');}})),false);assert.equal(reads,0);
    assert.equal(ui.refresh(),false);assert.throws(()=>p.bind());
});
test('external flow closure rejects payload reads and closes panel watcher',()=>{
    const p=fixture();ready(p);const ui=p.bind();p.flow.dispose();let reads=0;
    assert.equal(ui.update(new Proxy({}, {get(){reads++;throw Error('closed');}})),false);
    assert.equal(reads,0);assert.equal(ui.isDisposed(),true);assert.equal(p.timers.size,0);
});
test('shared source getter cannot trigger nested dispatch and closes safely on dispose',()=>{
    const p=fixture();let sends=0;ready(p);const ui=p.bind(()=>sends++),data=frame('a',{revision:2});
    Object.defineProperty(data,'mode',{enumerable:true,get(){assert.equal(p.root.visible,false);
        assert.equal(ui.request(),false);assert.equal(ui.refresh(),false);return 'AI';}});
    assert.equal(ui.update(data),true);assert.equal(sends,0);ui.dispose();
});
test('invalid port accessors are never invoked and root ownership rolls back',()=>{
    const p=fixture();let reads=0;const invalid={};Object.defineProperty(invalid,'update',{get(){reads++;throw Error('getter');}});
    assert.throws(()=>p.bind(()=>{},invalid));assert.equal(reads,0);assert.equal(p.timers.size,0);
    ready(p);p.bind().dispose();
});
test('selection changed from a staging setter cannot dispatch to an unseen actor',()=>{
    const p=fixture(),sent=[];ready(p);const ui=p.bind(intent=>sent.push(intent));let changed=false;
    p.options.onText=(id,value)=>{if(!changed&&id==='ManualRequestRecipient'&&value===''){
        changed=true;p.flow.selectPlayer('b');}};
    assert.equal(ui.request(),false);assert.equal(sent.length,0);
    assert.equal(p.flow.view().manual.request,null);assert.match(p.text('Recipient'),/\[b\]/);ui.dispose();
});
test('final tree preflight reentry cannot bypass the displayed-frame check at begin',()=>{
    const p=fixture(),sent=[];ready(p);let staged=false,readAfterStage=false,changed=false;
    const port=p.flow.requestPort(),view=port.view;
    port.view=function(){const value=view();if(staged)readAfterStage=true;return value;};
    p.root.IsValid=function(){if(readAfterStage&&!changed){changed=true;p.flow.selectPlayer('b');}return this.valid;};
    const ui=p.bind(intent=>sent.push(intent),port);
    p.options.onText=(id,value)=>{if(id==='ManualRequestMessage'&&value.includes('обновляются'))staged=true;};
    assert.equal(ui.request(),false);assert.equal(sent.length,0);assert.equal(p.flow.view().manual.request,null);
    assert.match(p.text('Recipient'),/\[b\]/);ui.dispose();
});
test('configured shared flow cannot enable a panel without its actual send adapter',()=>{
    const p=fixture();ready(p);assert.equal(p.flow.view().canRequest,true);const ui=p.bindWithoutSend();
    assert.equal(p.nodes.get('ManualRequestButton').enabled,false);
    assert.match(p.text('Message'),/Переходник.*не подключён/);assert.equal(ui.request(),false);
    assert.equal(p.flow.view().manual.request,null);ui.dispose();
});
test('MANUAL arriving after timer arming before dispatch releases busy and cancels ACK',()=>{
    const p=fixture();ready(p);let sends=0,changed=false;
    const ui=p.bind(()=>sends++);
    p.root.IsValid=function(){if(!changed&&[...p.timers.values()].some(row=>row.delay===5)){
        changed=true;p.flow.updateControl(frame('a',{revision:2,mode:'MANUAL'}));}return this.valid;};
    assert.equal(ui.request(),false);assert.equal(sends,0);assert.equal(p.flow.view().manual.status,'mode-observed');
    assert.equal(ui.refresh(),true);assert.equal(p.timers.size,1);
    assert.match(p.text('State'),/право ввода не подтверждено/);
    assert.equal(ui.update(frame('a',{revision:3,mode:'AI'})),true);ui.dispose();
});
test('new actor epoch clearing request before dispatch keeps shared panel usable',()=>{
    const p=fixture();ready(p);let sends=0,changed=false;const ui=p.bind(()=>sends++);
    p.root.IsValid=function(){if(!changed&&[...p.timers.values()].some(row=>row.delay===5)){
        changed=true;p.flow.updateControl(frame('a',{epoch:2,revision:0}));}return this.valid;};
    assert.equal(ui.request(),false);assert.equal(sends,0);assert.equal(p.flow.view().manual.request,null);
    assert.equal(ui.isDisposed(),false);assert.equal(p.timers.size,1);assert.equal(ui.refresh(),true);ui.dispose();
});
test('ACK expiry while suspended is applied on refresh and late reply remains correlated',()=>{
    const p=fixture();let reply;ready(p);const ui=p.bind((_,cb)=>reply=cb);p.click();ui.suspend();p.fire(5);
    assert.equal(ui.refresh(),true);assert.equal(p.flow.view().manual.status,'unknown');assert.equal(p.timers.size,1);
    assert.equal(p.nodes.get('ManualRequestButton').enabled,false);assert.equal(reply(response()),true);ui.dispose();
});
test('ACK expiry inside a busy source getter is applied after the source transaction',()=>{
    const p=fixture();ready(p);const ui=p.bind();p.click();const data=frame('a',{revision:2});
    Object.defineProperty(data,'mode',{enumerable:true,get(){p.fire(5);return 'AI';}});
    assert.equal(ui.update(data),true);assert.equal(p.flow.view().manual.status,'unknown');
    assert.match(p.text('State'),/неизвестен/);assert.equal(p.timers.size,1);ui.dispose();
});
test('deferred expiry cannot overwrite an externally accepted captured response',()=>{
    const p=fixture();ready(p);const ui=p.bind();p.click();const ticket=p.flow.view().manual.request.ticket;
    ui.suspend();p.fire(5);assert.equal(p.flow.report(ticket,response()),true);
    assert.equal(ui.refresh(),true);assert.equal(p.flow.view().manual.status,'accepted');ui.dispose();
});
