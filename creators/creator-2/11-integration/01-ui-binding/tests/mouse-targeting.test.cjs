"use strict";
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm"),test=require("node:test"),assert=require("node:assert/strict");
const repo=path.resolve(__dirname,"../../../../..");
const files=["03-map-view/03-visibility-targets/src/panorama/scripts/custom_game/targets_state.js",
 "05-intervention-ui/02-mouse-targeting/src/panorama/scripts/custom_game/mouse_proposal_state.js",
 "05-intervention-ui/02-mouse-targeting/src/panorama/scripts/custom_game/mouse_proposal_panel.js",
 "11-integration/01-ui-binding/src/panorama/scripts/custom_game/mouse_targeting_binding.js"];
const actor=id=>({id,playerName:"Player "+id,epoch:1});
const visible=(id="t",team="enemy",kind="hero",alive=true)=>({id,visibility:"visible",label:"<b>"+id+"</b>",team,kind,alive,entityIndex:10});
function fixture(){
 const native=new Proxy({},{get(){throw Error("native API forbidden");}}),context=vm.createContext({$:native,Game:native,GameEvents:native,Entities:native});
 for(const relative of files){const file=path.join(repo,"creators/creator-2",relative);assert.ok(fs.existsSync(file),relative);vm.runInContext(fs.readFileSync(file,"utf8"),context);}
 const names=["MouseActor","MouseAction","MouseTarget","MouseState","MouseLease","MouseHint"],nodes={};
 for(const id of names)nodes[id]={visible:true,html:true,text:"",valid:true,IsValid(){return this.valid;}};
 const root={visible:false,valid:true,IsValid(){return this.valid;},FindChildTraverse:id=>nodes[id]};
 const f={context,names,nodes,root,time:0,clock:null};
 f.bind=()=>context.DotaCoachMouseTargetingPanels.bind(root,{now(){return f.clock?f.clock():f.time;},maxAgeMs:1000});return f;
}
function ready(f,row=visible()){const p=f.bind();p.captureActor(actor("a"));p.updateTargets({revision:1,targets:[row]});p.selectTarget(row.id);return p;}
test("explicit independent group keeps authority flags false and no auto bind",()=>{
 const f=fixture();assert.equal(f.root.visible,false);const p=f.bind(),v=p.view();
 assert.equal(v.closed,false);assert.equal(v.observation.status,"empty");assert.equal(v.mouse.actor,null);
 for(const key of ["canSend","nativeConfirmed","sourceAuthorizationConfirmed"])assert.equal(v[key],false);
 assert.match(f.nodes.MouseLease.text,/неизвестно/);
});
test("fresh selected Targets projection produces all three actions with fixed actor",()=>{
 for(const [team,kind,action]of [["enemy","hero","attack"],["enemy","creep","last_hit"],["ally","creep","deny"]]){
  const f=fixture(),p=ready(f,visible("t",team,kind));assert.equal(p.proposeTarget(),true);
  assert.equal(p.view().mouse.proposal.action,action);assert.equal(f.nodes.MouseTarget.text,"<b>t</b>");assert.equal(f.nodes.MouseTarget.html,false);
  assert.equal(p.captureActor(actor("b")),false);assert.equal(p.view().mouse.proposal.actor.id,"a");
 }
});
test("target proposal uses owned source and ignores any caller snapshot",()=>{
 const f=fixture(),p=ready(f);const unread=new Proxy({},{get(){throw Error("caller ignored");},ownKeys(){throw Error("caller ignored");}});
 assert.equal(p.proposeTarget(unread),true);assert.equal(p.view().mouse.proposal.target.id,"t");
});
test("expiry at exact boundary clears target proposal but retains actor",()=>{
 const f=fixture(),p=ready(f);assert.equal(p.proposeTarget(),true);f.time=999;assert.ok(p.view().mouse.proposal);
 f.time=1000;assert.equal(p.refresh(),true);assert.equal(p.view().observation.status,"stale");assert.equal(p.view().mouse.proposal,null);
 assert.equal(f.nodes.MouseAction.text,"");assert.equal(f.nodes.MouseActor.text,"Player a");assert.equal(p.proposeTarget(),false);
});
test("view performs freshness check without requiring explicit refresh",()=>{
 const f=fixture(),p=ready(f);p.proposeTarget();f.time=1000;assert.equal(p.view().mouse.proposal,null);assert.equal(f.nodes.MouseTarget.text,"");
});
test("hidden gone unknown dead allied hero cannot retain or create target action",()=>{
 for(const row of [{id:"t",visibility:"hidden"},{id:"t",visibility:"gone"},{id:"t",visibility:"unknown"},visible("t","enemy","hero",false),visible("t","ally","hero")]){
  const f=fixture(),p=ready(f);p.proposeTarget();assert.equal(p.updateTargets({revision:2,targets:[row]}),true);
  assert.equal(p.view().mouse.proposal,null);assert.equal(p.proposeTarget(),false);assert.equal(f.nodes.MouseTarget.text,"");
 }
});
test("source update clears old target before DTO getters even when stale rejected",()=>{
 const f=fixture(),p=ready(f);p.proposeTarget();let reads=0;
 const input={get revision(){reads++;assert.equal(f.nodes.MouseAction.text,"");assert.equal(f.nodes.MouseTarget.text,"");assert.equal(p.view(),null);return 1;},targets:[visible()]};
 assert.equal(p.updateTargets(input),false);assert.ok(reads>0);assert.equal(p.view().mouse.proposal,null);assert.equal(p.view().mouse.actor.id,"a");
});
test("changing target never silently reissues action and second click replaces explicitly",()=>{
 const f=fixture(),p=ready(f);p.proposeTarget();p.updateTargets({revision:2,targets:[visible(),visible("u","ally","creep")]});
 assert.equal(p.selectTarget("u"),true);assert.equal(p.view().mouse.proposal,null);assert.equal(p.proposeTarget(),true);
 assert.equal(p.view().mouse.proposal.action,"deny");assert.equal(p.view().mouse.proposal.serial,2);assert.equal(p.selectTarget("missing"),false);
 assert.equal(p.view().mouse.proposal,null);
});
test("move proposal is independent of source updates selection and local expiry",()=>{
 const f=fixture(),p=ready(f);p.proposeMove({x:100,y:200,z:0});
 assert.equal(p.updateTargets({revision:2,targets:[{id:"t",visibility:"hidden"}]}),true);p.selectTarget(null);f.time=1000;p.refresh();
 assert.equal(p.view().mouse.proposal.action,"move");assert.equal(p.view().mouse.proposal.point.x,100);assert.equal(f.nodes.MouseAction.text,"Движение");
});
test("reset clears actor proposal and target selection but preserves monotonic history",()=>{
 const f=fixture(),p=ready(f);p.proposeTarget();assert.equal(p.reset(),true);assert.equal(p.view().mouse.actor,null);assert.equal(p.view().observation.target,null);
 assert.equal(p.updateTargets({revision:1,targets:[visible()]}),false);p.captureActor(actor("b"));p.selectTarget("t");p.proposeTarget();
 assert.equal(p.view().mouse.proposal.actor.id,"b");assert.equal(p.view().mouse.proposal.serial,2);
});
test("invalid or backwards clock removes target draft and newer source can recover",()=>{
 for(const bad of [-1,NaN]){const f=fixture(),p=ready(f);p.proposeTarget();f.time=10;p.refresh();f.time=bad;p.refresh();
  assert.equal(p.view().mouse.proposal,null);assert.equal(p.isDisposed(),false);f.time=11;
  assert.equal(p.updateTargets({revision:2,targets:[visible()]}),true);p.selectTarget("t");assert.equal(p.proposeTarget(),true);
 }
});
test("nested clock calls reject all methods before DTO reads and busy view is null",()=>{
 const f=fixture(),p=ready(f);let reads=0;const unread=new Proxy({},{get(){reads++;return undefined;},ownKeys(){reads++;return [];}});
 f.clock=()=>{assert.equal(p.captureActor(unread),false);assert.equal(p.updateTargets(unread),false);assert.equal(p.proposeMove(unread),false);
  assert.equal(p.selectTarget(unread),false);assert.equal(p.proposeTarget(),false);assert.equal(p.reset(),false);assert.equal(p.refresh(),false);
  assert.equal(p.view(),null);assert.equal(p.isDisposed(),false);return f.time;};
 assert.equal(p.proposeTarget(),true);assert.equal(reads,0);
});
test("native callback advancing clock during proposal cannot leave expired target action",()=>{
 const f=fixture(),p=ready(f);let value="",fired=false;
 Object.defineProperty(f.nodes.MouseAction,"text",{get(){return value;},set(v){value=v;if(v==="Атака героя"&&!fired){fired=true;f.time=1000;}}});
 assert.equal(p.proposeTarget(),false);assert.equal(value,"");assert.equal(p.view().mouse.proposal,null);
});
test("dispose from clock stops before caller input and old handle cannot affect rebound",()=>{
 const f=fixture(),p=ready(f);let reads=0;const unread=new Proxy({},{get(){reads++;return undefined;},ownKeys(){reads++;return [];}});
 f.clock=()=>{p.dispose();return f.time;};assert.equal(p.captureActor(unread),false);assert.equal(reads,0);assert.equal(f.root.visible,false);
 f.clock=null;const fresh=f.bind();fresh.captureActor(actor("b"));
 for(const method of ["captureActor","updateTargets","proposeMove","selectTarget"])assert.equal(p[method](unread),false);
 assert.equal(p.proposeTarget(),false);p.view();p.refresh();p.reset();p.dispose();assert.equal(p.isDisposed(),true);
 assert.equal(f.nodes.MouseActor.text,"Player b");assert.equal(reads,0);
});
test("dispose from source getter prevents publication and closes private target model",()=>{
 const f=fixture(),p=ready(f);p.proposeTarget();assert.equal(p.updateTargets({get revision(){p.dispose();return 2;},get targets(){throw Error("late read");}}),false);
 assert.equal(p.isDisposed(),true);assert.equal(p.view().closed,true);assert.equal(p.view().observation,null);assert.equal(f.root.visible,false);
});
test("missing hidden replaced invalid UI closes group before clock or input",()=>{
 for(const mutate of [f=>{delete f.nodes.MouseLease;},f=>{f.nodes.MouseLease.visible=false;},f=>{f.nodes.MouseLease={...f.nodes.MouseLease};},f=>{f.nodes.MouseLease.valid=false;}]){
  const f=fixture(),p=ready(f);p.proposeTarget();mutate(f);f.clock=()=>{throw Error("must not call clock");};
  assert.equal(p.updateTargets(new Proxy({},{get(){throw Error("must not read DTO");}})),false);
  assert.equal(p.isDisposed(),true);assert.equal(p.view().mouse,null);assert.equal(f.root.visible,false);
 }
});
test("duplicate ownership failure preserves existing group and copied output",()=>{
 const f=fixture(),p=ready(f);p.proposeTarget();assert.throws(()=>f.bind(),/already bound/);
 const v=p.view();v.mouse.actor.id="other";v.observation.target.label="changed";
 assert.equal(p.view().mouse.actor.id,"a");assert.equal(p.view().observation.target.label,"<b>t</b>");assert.equal(p.isDisposed(),false);
});

test("destroyed root closes without writing its invalid native properties",()=>{
 const f=fixture(),p=ready(f);p.proposeTarget();f.root.valid=false;let writes=0;
 Object.defineProperty(f.root,"visible",{get(){return true;},set(){writes++;throw Error("destroyed root");}});
 assert.equal(p.refresh(),false);assert.equal(p.isDisposed(),true);assert.equal(p.view().closed,true);assert.equal(writes,0);
});
for(const method of ["proposeTarget","view"]){
 test("final clock barrier after native callbacks: "+method,()=>{
  for(let threshold=1;threshold<=6;threshold++){
   const f=fixture(),p=ready(f);if(method==="view")p.proposeTarget();let reads=0,advance=false;
   f.clock=()=>{reads++;if(reads===threshold)advance=true;return f.time;};
   f.root.IsValid=function(){if(advance){advance=false;f.time=1000;}return this.valid;};
   const result=p[method]();
   if(f.time===1000){
    if(method==="view")assert.equal(result.mouse.proposal,null,"expired view at barrier "+threshold);
    else assert.equal(result,false,"expired result at barrier "+threshold);
    assert.equal(f.nodes.MouseAction.text,"");assert.equal(f.nodes.MouseTarget.text,"");
   }else{
    if(method==="view")assert.equal(result.mouse.proposal.action,"attack");else assert.equal(result,true);
   }
  }
 });
}
