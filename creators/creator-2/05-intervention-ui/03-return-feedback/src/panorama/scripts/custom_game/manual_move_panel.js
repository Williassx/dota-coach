/* Native bootstrap for the isolated manual-move scene; no TEST automator. */
(function(root){
 'use strict';
 var localOwnership={};
 var messages={state:'Состояние сервера',granted:'Управление предоставлено',move_issued:'Приказ перемещения выдан',cancelled:'Вмешательство отменено',expired:'Срок вмешательства истёк',arrived:'Герой достиг точки',dead:'Герой погиб',replaced:'Привязка героя изменена',ended:'Сцена завершена',ai_resumed:'ИИ выдал новый приказ',engine_failed:'Действие движка не подтверждено'};
 var reasons={none:'',invalid_request:'Неверный запрос',unsupported_version:'Версия не поддерживается',not_ready:'Герой ещё не готов',unauthorized:'Нет права управления',stale_session:'Сеанс устарел',stale_generation:'Герой заменён',stale_epoch:'Разрешение устарело',not_ai:'Герой не в режиме ИИ',not_manual:'Нет ручного управления',invalid_position:'Недопустимая точка',dedup_limit:'Лимит запросов сцены',request_conflict:'ID запроса уже использован',clock_regressed:'Ошибка игрового времени',engine_failed:'Ошибка движка',paused:'Игра на паузе'};
 var api={bind:function(parent,ports){
  if(!parent||!ports||!root.CoachManualMove)return null;
  var nodes={},required=['MoveRoot','MoveCard','MoveCardText','MoveAcquire','MoveCancel','MoveSync','MoveStatus','MoveMode','MoveResult','MoveHistory'];
  for(var i=0;i<required.length;i++){var n=parent.FindChildTraverse(required[i]);if(!n)return null;nodes[required[i]]=n;}
  // This isolated scene owns exactly one callback. Rebind expires the old owner.
  var ownership=ports.ownership||localOwnership;
  var previous=ownership.coachManualMoveOwner;
  if(previous){if(typeof previous.dispose!=='function')return null;previous.dispose();}
  var token={};ownership.coachManualMoveOwner=token;
  var active=true,schedules=[],subscription=null;
  var state=root.CoachManualMove.create({send:function(wire){ports.events.SendCustomGameEventToServer('dota_coach_manual_request',wire);},now:ports.now,id:ports.id});
  function render(){if(!active||ownership.coachManualMoveOwner!==token)return;var v=state.read(),s=v.snapshot;
   nodes.MoveStatus.text=v.requestStatus==='unknown'?'Результат неизвестен. Уточняем состояние.':v.pending?'Ожидается ответ сервера':s?'Связь с сервером установлена':'Ожидается состояние героя';
   nodes.MoveMode.text=s?'Управление: '+s.mode+' | Осталось по серверу: '+s.remaining.toFixed(1)+' с':'Управление: неизвестно';
   var result=v.history.length?v.history[v.history.length-1]:s;
   nodes.MoveResult.text=result?(messages[result.transition]||result.transition)+(result.reason!=='none'?' — '+reasons[result.reason]:''):'';
   nodes.MoveCardText.text=s?'TEST / синтетический игрок: '+s.actor_id+(v.selected===s.actor_id?' [выбран]':''): 'TEST / герой не готов';
   nodes.MoveAcquire.enabled=v.canAcquire;nodes.MoveCancel.enabled=v.canMove;nodes.MoveSync.enabled=!v.pending;
   nodes.MoveHistory.text=v.history.slice(-7).map(function(e){return '#'+e.revision+' '+(messages[e.transition]||e.transition)+(e.reason==='none'?'':' / '+reasons[e.reason]);}).join('\n');
  }
  function action(fn){return function(){if(!active||ownership.coachManualMoveOwner!==token)return;fn();render();};}
  nodes.MoveCard.SetPanelEvent('onactivate',action(function(){var s=state.read().snapshot;if(s)state.select(s.actor_id);}));
  nodes.MoveAcquire.SetPanelEvent('onactivate',action(function(){state.acquire();}));
  nodes.MoveCancel.SetPanelEvent('onactivate',action(function(){state.cancel();}));
  nodes.MoveSync.SetPanelEvent('onactivate',action(function(){state.sync();}));
  function mouse(event,button){if(!active||ownership.coachManualMoveOwner!==token||event!=='pressed'||button!==0||!state.read().canMove)return false;
   var screen=ports.ui.GetCursorPosition(),pos=ports.ui.GetScreenWorldPosition(screen);
   if(!pos)return false;var sent=state.move(pos);render();return sent;
  }
  try{subscription=ports.events.Subscribe('dota_coach_manual_state',function(dto){if(!active||ownership.coachManualMoveOwner!==token)return;state.receive(dto);render();});ports.ui.SetMouseCallback(mouse);}catch(e){if(subscription!==null)ports.events.Unsubscribe(subscription);state.dispose();active=false;if(ownership.coachManualMoveOwner===token)ownership.coachManualMoveOwner=null;return null;}
  function tick(){if(!active||ownership.coachManualMoveOwner!==token)return;state.tick();render();schedules.push(ports.schedule(.2,tick));if(schedules.length>2)schedules.shift();}
  state.sync();render();schedules.push(ports.schedule(.2,tick));
  var binding={state:state,render:render,dispose:function(){if(!active)return;active=false;state.dispose();ports.events.Unsubscribe(subscription);if(ownership.coachManualMoveOwner===token){ownership.coachManualMoveOwner=null;ports.ui.SetMouseCallback(function(){return false;});nodes.MoveAcquire.enabled=false;nodes.MoveCancel.enabled=false;}if(ports.cancelSchedule)schedules.forEach(function(h){ports.cancelSchedule(h);});}};
  token.dispose=binding.dispose;return binding;
 }};
 root.CoachManualMovePanel=api;
 if(typeof $!=='undefined'&&typeof GameEvents!=='undefined'&&typeof GameUI!=='undefined'){
  var sequence=0,nonce='m'+Date.now().toString(36)+'-'+Math.floor(Math.random()*2147483647).toString(36);
  var binding=api.bind($.GetContextPanel(),{ownership:GameUI.CustomUIConfig(),events:GameEvents,ui:GameUI,now:function(){return Date.now();},id:function(){sequence++;return nonce+'-'+sequence;},schedule:$.Schedule,cancelSchedule:$.CancelScheduled});
  if(binding){GameUI.CustomUIConfig().coachManualMove=binding;$.Msg('[C2ManualMove] panel_ready');}
  else $.Msg('[C2ManualMove] panel_unavailable');
 }
}(this));
