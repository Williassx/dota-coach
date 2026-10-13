/* Explicit versioned server consumer. Local selection never grants control. */
(function(root,factory){var api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.CoachManualMove=api;}(this,function(){
 'use strict';
 var fields=['protocol_version','session_id','actor_id','generation','epoch','revision','mode','alive','remaining','entity_index','request_id','request_status','reason','transition','ai_order_count','manual_order_count','server_time'];
 var reasons=['none','invalid_request','unsupported_version','not_ready','unauthorized','stale_session','stale_generation','stale_epoch','not_ai','not_manual','invalid_position','dedup_limit','request_conflict','clock_regressed','engine_failed','paused'];
 var transitions=['state','granted','move_issued','cancelled','expired','arrived','dead','replaced','ended','ai_resumed','engine_failed'];
 function finite(v){return typeof v==='number'&&isFinite(v);}
 function integer(v){return finite(v)&&v>=0&&v<=2147483647&&Math.floor(v)===v;}
 function id(v){return typeof v==='string'&&/^[A-Za-z0-9_-]{1,64}$/.test(v);}
 function clone(v){return v===null?null:JSON.parse(JSON.stringify(v));}
 function validate(v){
  if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).length!==fields.length)return false;
  for(var i=0;i<fields.length;i++)if(!Object.prototype.hasOwnProperty.call(v,fields[i]))return false;
  return v.protocol_version===1&&id(v.session_id)&&id(v.actor_id)&&integer(v.generation)&&integer(v.epoch)&&integer(v.revision)&&integer(v.entity_index)&&integer(v.ai_order_count)&&integer(v.manual_order_count)&&
   ['AI','MANUAL','INACTIVE'].indexOf(v.mode)>=0&&(v.alive===0||v.alive===1)&&finite(v.remaining)&&v.remaining>=0&&v.remaining<=5&&finite(v.server_time)&&
   (v.request_id===''||id(v.request_id))&&['none','accepted','rejected'].indexOf(v.request_status)>=0&&reasons.indexOf(v.reason)>=0&&transitions.indexOf(v.transition)>=0&&
   ((v.request_id===''&&v.request_status==='none')||(v.request_id!==''&&v.request_status!=='none'))&&
   (v.mode==='INACTIVE'||v.alive===1)&& (v.mode==='MANUAL'||v.remaining===0)&&
   (v.request_status!=='accepted'||v.reason==='none');
 }
 function create(ports){
  if(!ports||typeof ports.send!=='function'||typeof ports.now!=='function'||typeof ports.id!=='function')throw Error('Explicit ports required');
  var active=true,busy=false,current=null,pending=null,selected=null,captured=null,status='idle',history=[];
  function canMove(){return active&&!busy&&!pending&&current&&current.mode==='MANUAL'&&current.alive&&current.remaining>0&&captured&&captured.actor_id===current.actor_id&&captured.generation===current.generation&&captured.epoch===current.epoch&&captured.session_id===current.session_id;}
  function send(kind,coords){
   if(!active||busy||pending)return false;
   var wire={protocol_version:1,request_id:ports.id(),kind:kind};if(!id(wire.request_id))return false;
   if(kind!=='sync'){
    wire.session_id=current.session_id;wire.actor_id=current.actor_id;wire.generation=current.generation;wire.epoch=current.epoch;
    if(kind==='move'){wire.x=coords[0];wire.y=coords[1];wire.z=coords[2];}
   }
   var now=ports.now();if(!finite(now))return false;
   pending={request_id:wire.request_id,kind:kind,deadline:now+5000};status='pending';busy=true;
   try{ports.send(clone(wire));}catch(e){pending=null;status='transport_error';busy=false;return false;}
   busy=false;return true;
  }
  function sync(){if(!active||busy)return false;pending=null;return send('sync');}
  function receive(v){
   if(!active||busy)return false;
   try{if(!validate(v))return false;}catch(e){return false;}
   var matching=pending&&v.request_id===pending.request_id;
   var switching=!current||v.session_id!==current.session_id;
   if(switching&&!(matching&&pending.kind==='sync'&&v.request_status==='accepted'))return false;
   if(!switching&&v.revision<=current.revision)return false;
   if(!switching&&(v.generation<current.generation||v.epoch<current.epoch||v.server_time<current.server_time||v.ai_order_count<current.ai_order_count||v.manual_order_count<current.manual_order_count))return false;
   if(switching)captured=null;
   current=clone(v);current.alive=v.alive===1;
   if(matching){var kind=pending.kind;status=v.request_status;pending=null;
    if(kind==='acquire'&&v.request_status==='accepted'&&v.transition==='granted'&&v.mode==='MANUAL')captured={actor_id:v.actor_id,session_id:v.session_id,generation:v.generation,epoch:v.epoch};
    // Resync observes the server's lease, without inventing a new grant.
    if(kind==='sync'&&v.mode==='MANUAL')captured={actor_id:v.actor_id,session_id:v.session_id,generation:v.generation,epoch:v.epoch};
   }
   if(current.mode!=='MANUAL'||!current.alive||captured&&(captured.generation!==current.generation||captured.epoch!==current.epoch))captured=null;
   // Periodic state updates must not evict outcomes from the bounded journal.
   if(v.transition!=='state'||v.request_status==='rejected')history.push({revision:v.revision,request_id:v.request_id,request_status:v.request_status,transition:v.transition,reason:v.reason,mode:v.mode});if(history.length>30)history.shift();
   return true;
  }
  return {
   select:function(actor){if(!active||busy||!id(actor))return false;selected=actor;return true;},
   sync:sync,receive:receive,
   acquire:function(){if(!active||busy||pending||!current||selected!==current.actor_id||current.mode!=='AI'||!current.alive)return false;return send('acquire');},
   move:function(coords){if(!canMove())return false;try{if(!Array.isArray(coords)||coords.length!==3||!coords.every(finite)||Math.abs(coords[0])>16000||Math.abs(coords[1])>16000||Math.abs(coords[2])>2048)return false;}catch(e){return false;}return send('move',coords);},
   cancel:function(){return canMove()?send('cancel'):false;},
   tick:function(){if(!active||busy||!pending)return;var now=ports.now();if(finite(now)&&now>=pending.deadline){pending=null;status='unknown';sync();status='unknown';}},
   read:function(){return {active:active,selected:selected,captured:clone(captured),snapshot:clone(current),pending:clone(pending),requestStatus:status,canMove:!!canMove(),canAcquire:!!(active&&!busy&&!pending&&current&&selected===current.actor_id&&current.mode==='AI'&&current.alive),history:clone(history)};},
   dispose:function(){if(!active)return;active=false;pending=null;captured=null;}
  };
 }
 return {create:create};
}));
