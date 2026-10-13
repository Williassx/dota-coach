/* TEST ONLY: programmatic scene acceptance, never physical mouse proof. */
(function(){'use strict';
 GameEvents.Subscribe('dota_coach_manual_state',function(dto){$.Msg('[C2NativeMoveWire] '+JSON.stringify(dto));});
 var b=null,start=Date.now(),origin=null,aiBefore=0,manualBefore=0;
 function current(){return b&&b.state.read();}
 function mark(phase,pass,extra){var v=current(),s=v&&v.snapshot;$.Msg('[C2NativeMove] '+phase+' pass='+pass+' '+JSON.stringify({phase:phase,pass:pass,details:extra||{},snapshot:s,origin:s?Entities.GetAbsOrigin(s.entity_index):null,history:v&&v.history}));var l=$('#MoveFixtureStatus');if(l)l.text='TEST programmatic: '+phase+' / '+(pass?'PASS':'FAIL');if(!pass)throw Error('TEST phase failed '+phase);}
 function until(predicate,done){var deadline=Date.now()+20000;function check(){if(predicate()){done();return;}if(Date.now()>deadline){mark('timeout',false);return;}$.Schedule(.1,check);}check();}
 function selectAcquire(done){var s=current().snapshot;b.state.select(s.actor_id);b.state.acquire();b.render();until(function(){return current().canMove;},done);}
 function moveFar(){var s=current().snapshot;origin=Entities.GetAbsOrigin(s.entity_index);var sent=b.state.move([origin[0]+1400,origin[1],origin[2]]);b.render();mark('move_sent',sent);until(function(){return current().snapshot.manual_order_count>manualBefore;},function(){mark('move_issued',current().snapshot.transition==='move_issued');$.Schedule(1,moving);});}
 function moving(){var p=Entities.GetAbsOrigin(current().snapshot.entity_index),d=Math.sqrt(Math.pow(p[0]-origin[0],2)+Math.pow(p[1]-origin[1],2));mark('moving',d>20,{distanceXY:d});until(function(){return current().snapshot.mode==='AI'&&current().snapshot.ai_order_count>aiBefore;},function(){var h=current().history;mark('returned',h.some(function(e){return e.transition==='expired'||e.transition==='arrived';})&&h.some(function(e){return e.transition==='ai_resumed';}));$.Schedule(10,cancelCycle);});}
 function cancelCycle(){selectAcquire(function(){aiBefore=current().snapshot.ai_order_count;var sent=b.state.cancel();b.render();until(function(){return current().snapshot.mode==='AI'&&current().snapshot.ai_order_count>aiBefore;},function(){mark('cancelled_return',sent&&current().history.some(function(e){return e.transition==='cancelled';}));$.Schedule(10,arrivalCycle);});});}
 function arrivalCycle(){selectAcquire(function(){aiBefore=current().snapshot.ai_order_count;var p=Entities.GetAbsOrigin(current().snapshot.entity_index);var sent=b.state.move([p[0]+60,p[1],p[2]]);b.render();until(function(){return current().snapshot.mode==='AI'&&current().snapshot.ai_order_count>aiBefore;},function(){mark('arrived_return',sent&&current().history.some(function(e){return e.transition==='arrived';}));$.Schedule(10,function(){b.dispose();mark('disposed',!b.state.read().active);});});});}
 function begin(){b=GameUI.CustomUIConfig().coachManualMove;if(!b||!b.state.read().snapshot||b.state.read().snapshot.mode!=='AI'){if(Date.now()-start>240000){mark('start_timeout',false);return;}$.Schedule(.25,begin);return;}
  aiBefore=current().snapshot.ai_order_count;mark('bound',aiBefore>0);
  $.Schedule(2,function(){var p=GameUI.GetScreenWorldPosition([640,360]);mark('world_point',Array.isArray(p)&&p.length===3&&p.every(function(x){return typeof x==='number'&&isFinite(x);}),{screen:[640,360],world:p,inputInjected:false});});
  $.Schedule(10,function(){selectAcquire(function(){aiBefore=current().snapshot.ai_order_count;manualBefore=current().snapshot.manual_order_count;mark('granted',current().snapshot.remaining>0);$.Schedule(1.8,moveFar);});});
 }
 begin();
}());
