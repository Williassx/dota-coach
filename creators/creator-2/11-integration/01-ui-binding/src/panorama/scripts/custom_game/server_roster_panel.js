/* Read-only native server confirmation of five TEST assignments. */
(function(root,factory){var api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.CoachServerRoster=api;
 if(typeof $!=='undefined'&&typeof GameEvents!=='undefined'&&typeof GameUI!=='undefined'){
  var seq=0,nonce='roster_'+Date.now().toString(36)+'_'+Math.floor(Math.random()*10000000);
  var b=api.bind($.GetContextPanel(),{ownership:GameUI.CustomUIConfig(),events:GameEvents,now:function(){return Date.now();},id:function(){return nonce+'_'+(++seq);},schedule:$.Schedule,cancelSchedule:$.CancelScheduled});
  if(b){GameUI.CustomUIConfig().coachServerRoster=b;$.Msg('[C2ServerRoster] bound');}
 }
}(this,function(){'use strict';
 function panelValid(n){try{return !!n&&(typeof n.IsValid!=='function'||n.IsValid()===true);}catch(e){return false;}}
 var localOwner={},fields=['protocol_version','request_id','session_id','revision','status','reason','synthetic','assignments'];
 function record(v,names){if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).length!==names.length)return false;for(var i=0;i<names.length;i++)if(!Object.prototype.hasOwnProperty.call(v,names[i]))return false;return true;}
 function id(v){return typeof v==='string'&&/^[A-Za-z0-9_-]{1,64}$/.test(v);}
 function finite(v){return typeof v==='number'&&isFinite(v);}
 function clone(v){return v===null?null:JSON.parse(JSON.stringify(v));}
 function valid(v){if(!record(v,fields)||v.protocol_version!==1||!id(v.request_id)||!id(v.session_id)||!finite(v.revision)||v.revision<1||v.revision>2147483647||Math.floor(v.revision)!==v.revision||v.synthetic!==1)return false;
  if(v.status==='rejected')return ['invalid_request','unsupported_version','not_ready'].indexOf(v.reason)>=0&&record(v.assignments,[]);
  if(v.status!=='confirmed'||v.reason!=='none'||!record(v.assignments,['1','2','3','4','5']))return false;
  var ids={},heroes={},roles={};for(var i=1;i<=5;i++){var e=v.assignments[String(i)];if(!record(e,['id','hero','role','coverage','warning'])||!id(e.id)||!/^TEST[-_]/.test(e.id)||typeof e.hero!=='string'||!/^npc_dota_hero_[a-z0-9_]+$/.test(e.hero)||!finite(e.role)||Math.floor(e.role)!==e.role||e.role<1||e.role>5||!finite(e.coverage)||e.coverage<0||e.coverage>1||e.warning!==(e.coverage<.5?'weak-coverage':''))return false;
   if(ids[e.id]||heroes[e.hero]||roles[e.role])return false;ids[e.id]=heroes[e.hero]=roles[e.role]=true;}
  return true;
 }
 function create(ports){var active=true,pending=null,snapshot=null,status='idle',revision=0,session=null;
  function sync(){if(!active||pending)return false;var rid=ports.id();if(!id(rid))return false;var now=ports.now();if(!finite(now))return false;pending={id:rid,deadline:now+3000};status='waiting';try{ports.send({protocol_version:1,request_id:rid});return true;}catch(e){pending=null;status='unknown';return false;}}
  function receive(v){if(!active)return false;try{if(!pending||!valid(v)||v.request_id!==pending.id)return false;if(v.session_id===session&&v.revision<=revision)return false;
    var copied=clone(v);session=copied.session_id;revision=copied.revision;snapshot=copied;pending=null;status=copied.status;return true;}catch(e){return false;}}
  function tick(){if(!active||!pending)return;var now=ports.now();if(!finite(now)||now>=pending.deadline){pending=null;status='unknown';}}
  return {sync:sync,receive:receive,tick:tick,read:function(){return {active:active,status:status,pending:pending!==null,snapshot:clone(snapshot)};},dispose:function(){if(!active)return;active=false;pending=null;status='disposed';}};
 }
 function bind(parent,ports){if(!parent||typeof parent.FindChildTraverse!=='function')return null;var ids=['RosterServerRoot','RosterServerStatus','RosterServerSync','RosterServer1','RosterServer2','RosterServer3','RosterServer4','RosterServer5'],nodes={};for(var i=0;i<ids.length;i++){var n=parent.FindChildTraverse(ids[i]);if(!panelValid(n))return null;nodes[ids[i]]=n;}
  var ownership=ports.ownership||localOwner,old=ownership.coachServerRosterOwner;if(old&&old.dispose)old.dispose();var token={},active=true,sub=null,handles=[],state=create({send:function(q){ports.events.SendCustomGameEventToServer('dota_coach_roster_request',q);},now:ports.now,id:ports.id});ownership.coachServerRosterOwner=token;
  function dispose(){if(!active)return;active=false;state.dispose();if(sub!==null)ports.events.Unsubscribe(sub);if(ownership.coachServerRosterOwner===token){ownership.coachServerRosterOwner=null;if(panelValid(nodes.RosterServerSync))nodes.RosterServerSync.enabled=false;}if(ports.cancelSchedule)handles.forEach(function(h){ports.cancelSchedule(h);});}
  function live(){if(!active||ownership.coachServerRosterOwner!==token)return false;for(var i=0;i<ids.length;i++)if(!panelValid(nodes[ids[i]])){dispose();return false;}return true;}
  function render(){if(!live())return;var v=state.read();nodes.RosterServerStatus.text=v.status==='confirmed'?'TEST состав подтверждён сервером. Это не старт матча.':v.status==='waiting'?'Ожидается подтверждение сервера':v.status==='rejected'?'Состав не подтверждён: '+v.snapshot.reason:v.status==='unknown'?'Ответ неизвестен. Обновите состояние.':'TEST состав не подтверждён';nodes.RosterServerSync.enabled=!v.pending;
   for(var i=1;i<=5;i++){var e=v.status==='confirmed'&&v.snapshot.assignments[String(i)];nodes['RosterServer'+i].text=e?'TEST '+e.id+' | роль '+e.role+' | '+e.hero+' | покрытие '+e.coverage.toFixed(2)+(e.warning?' — мало данных':''):'TEST / нет подтверждённого назначения';}}
  var sync=function(){if(!live())return;state.sync();render();};nodes.RosterServerSync.SetPanelEvent('onactivate',sync);
  try{sub=ports.events.Subscribe('dota_coach_roster_state',function(dto){if(!live())return;state.receive(dto);render();});}catch(e){state.dispose();ownership.coachServerRosterOwner=null;return null;}
  function tick(){if(!live())return;state.tick();render();handles.push(ports.schedule(.2,tick));if(handles.length>2)handles.shift();}
  var binding={state:state,render:render,dispose:dispose};token.dispose=binding.dispose;sync();handles.push(ports.schedule(.2,tick));return binding;
 }
 return {create:create,bind:bind};
}));
