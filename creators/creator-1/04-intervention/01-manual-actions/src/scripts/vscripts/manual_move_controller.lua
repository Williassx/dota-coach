-- TEST/synthetic manual move v1. No engine/global effects on require.
local module = {}
local serial = 0
local MAX = 2147483647
local function finite(v) return type(v) == "number" and v == v and v ~= math.huge and v ~= -math.huge end
local function counter(v) return finite(v) and v >= 0 and v <= MAX and v % 1 == 0 end
local function id(v) return type(v) == "string" and #v >= 1 and #v <= 64 and not v:find("[^A-Za-z0-9_-]") end
local function effect(fn, ...)
    if type(fn) ~= "function" then return false end
    local ok, result = pcall(fn, ...)
    return ok and result == true
end

function module.new(ports)
    assert(type(ports) == "table" and counter(ports.owner), "server owner required")
    serial = serial + 1
    local session = ports.session_id or ("TEST_session_" .. serial)
    local actor = ports.actor_id or "TEST_actor"
    assert(id(session) and id(actor), "server IDs required")
    local self = {}
    local mode, generation, epoch, revision = "INACTIVE", 0, 0, 0
    local entity_index, alive, bound = 0, false, false
    local time, deadline, target = 0, nil, nil
    local ai_count, manual_count = 0, 0
    local last_ai, last_state = nil, nil
    local blocked_generation, clock_failed, closed, busy = nil, false, false, false
    local registry, registry_count = {}, 0
    local deferred_stop = nil
    local function paused()
        local ok, value = pcall(ports.paused)
        return not ok or type(value) ~= "boolean" or value
    end
    local function defer_stop()
        if bound and alive and mode ~= "INACTIVE" then
            deferred_stop = {generation=generation,entity_index=entity_index}
        end
    end

    function self:snapshot(sender, request_id, status, reason, transition)
        if sender ~= ports.owner then return nil end
        if revision >= MAX then closed = true; mode = "INACTIVE"; deadline = nil; target = nil end
        revision = math.min(MAX, revision + 1)
        local remaining = mode == "MANUAL" and deadline and math.max(0, math.min(5, deadline - time)) or 0
        local s = {protocol_version=1,session_id=session,actor_id=actor,generation=generation,
            epoch=epoch,revision=revision,mode=mode,alive=alive,remaining=remaining,
            entity_index=entity_index,request_id=request_id or "",request_status=status or "none",
            reason=reason or "none",transition=transition or "state",ai_order_count=ai_count,
            manual_order_count=manual_count,server_time=time}
        if type(ports.emit) == "function" then pcall(ports.emit, sender, s) end
        return s
    end
    local function publish(reason, transition)
        last_state = time
        return self:snapshot(ports.owner, "", "none", reason, transition)
    end
    local function revoke()
        deadline = nil; target = nil; mode = "INACTIVE"
        if epoch < MAX then epoch = epoch + 1 else closed = true end
    end
    local function failed(reason)
        revoke(); blocked_generation = generation
        publish(reason or "engine_failed", "engine_failed")
    end
    local function read_clock()
        local ok, now = pcall(ports.clock)
        if not ok or not finite(now) or now < 0 or now < time then
            if not clock_failed then
                clock_failed = true
                if mode ~= "INACTIVE" then
                    if paused() then defer_stop() else effect(ports.stop) end
                end
                failed("clock_regressed")
            end
            return false
        end
        time = now
        return not clock_failed
    end
    local function observe()
        local ok, o = pcall(ports.observe)
        if not ok or type(o) ~= "table" or o.valid ~= true or not counter(o.entity_index)
            or not counter(o.generation) or type(o.alive) ~= "boolean"
            or not finite(o.x) or not finite(o.y) or not finite(o.z) then return nil end
        return o
    end
    local function cleanup_deferred_stop()
        if deferred_stop == nil or paused() then return end
        local expected = deferred_stop
        deferred_stop = nil
        local o = observe()
        -- Revoked rights do not permit stopping a replacement or foreign actor.
        if o and o.alive and o.generation == expected.generation
            and o.entity_index == expected.entity_index then
            if not effect(ports.stop) then publish("engine_failed", "engine_failed") end
        end
    end
    local function binding(o)
        if o == nil then
            if bound then bound = false; alive = false; revoke(); blocked_generation = generation; publish("not_ready", "replaced") end
            return false
        end
        if bound and (o.generation ~= generation or o.entity_index ~= entity_index) then
            local previous = generation
            generation = math.max(generation, o.generation); entity_index = o.entity_index; alive = o.alive
            revoke(); blocked_generation = previous
            -- A changed native handle without an advancing generation cannot be admitted.
            if o.generation <= previous then blocked_generation = generation end
            publish("not_ready", "replaced")
            return false
        end
        if not bound then
            if o.generation < generation then return false end
            generation = o.generation; entity_index = o.entity_index; bound = true
        end
        if not o.alive then
            if alive or blocked_generation ~= generation then
                alive = false; revoke(); blocked_generation = generation; publish("not_ready", "dead")
            end
            return false
        end
        alive = true
        return true
    end
    local function current(expected_generation, expected_entity)
        local o = observe()
        if not binding(o) then return nil end
        if o.generation ~= expected_generation or o.entity_index ~= expected_entity then return nil end
        return o
    end
    local function connected()
        return ports.connected == nil or effect(ports.connected)
    end
    local function resume(o, request_id, status, transition)
        if not effect(ports.ai, o) then
            failed("engine_failed")
            return self:snapshot(ports.owner, request_id, "rejected", "engine_failed", "engine_failed")
        end
        ai_count = math.min(MAX, ai_count + 1); mode = "AI"; last_ai = time
        if request_id then return self:snapshot(ports.owner, request_id, status, "none", transition) end
        return publish("none", transition)
    end
    local function finish(transition, request_id)
        local expected_generation, expected_entity = generation, entity_index
        if not effect(ports.stop) then failed("engine_failed"); return self:snapshot(ports.owner,request_id,"rejected","engine_failed","engine_failed") end
        revoke()
        self:snapshot(ports.owner, request_id, request_id and "accepted" or "none", "none", transition)
        local o = current(expected_generation, expected_entity)
        if not o then return self:snapshot(ports.owner,request_id,request_id and "rejected" or "none","not_ready","state") end
        return resume(o, request_id, "accepted", "ai_resumed")
    end
    local function refresh()
        if not read_clock() then return nil end
        if not connected() then
            if not closed then
                if mode ~= "INACTIVE" then
                    if paused() then defer_stop() else effect(ports.stop) end
                end
                closed = true; revoke(); publish("not_ready", "ended")
            end
            return nil
        end
        if closed then return nil end
        local o = observe()
        if not binding(o) then return nil end
        return o
    end
    local function validate(r)
        if type(r) ~= "table" or getmetatable(r) ~= nil then return nil, "invalid_request" end
        if not id(rawget(r,"request_id")) then return nil, nil end
        if rawget(r,"protocol_version") ~= 1 then
            local v = rawget(r,"protocol_version")
            return nil, finite(v) and v > 0 and v % 1 == 0 and "unsupported_version" or "invalid_request"
        end
        local kind = rawget(r,"kind")
        if kind ~= "sync" and kind ~= "acquire" and kind ~= "move" and kind ~= "cancel" then return nil,"invalid_request" end
        local allowed = {protocol_version=true,request_id=true,kind=true}
        local expected = 3
        if kind ~= "sync" then
            allowed.session_id=true;allowed.actor_id=true;allowed.generation=true;allowed.epoch=true;expected=7
            if not id(r.session_id) or not id(r.actor_id) or not counter(r.generation) or not counter(r.epoch) then return nil,"invalid_request" end
        end
        if kind == "move" then
            allowed.x=true;allowed.y=true;allowed.z=true;expected=10
            if not finite(r.x) or not finite(r.y) or not finite(r.z) then return nil,"invalid_request" end
        end
        local n=0; for key in pairs(r) do if not allowed[key] then return nil,"invalid_request" end; n=n+1 end
        if n ~= expected then return nil,"invalid_request" end
        return kind
    end
    local function same(a,b)
        for k,v in pairs(a) do if b[k] ~= v then return false end end
        for k,v in pairs(b) do if a[k] ~= v then return false end end
        return true
    end
    function self:handle(sender, r)
        if sender ~= ports.owner then return nil end -- before any request inspection
        if busy then return nil end
        local kind, reason = validate(r)
        local rid = type(r)=="table" and rawget(r,"request_id") or nil
        if not id(rid) then return nil end
        local function reply(why) return self:snapshot(sender,rid,"rejected",why,"state") end
        if not kind then return reply(reason or "invalid_request") end
        local o = refresh()
        if clock_failed then return reply("clock_regressed") end
        if kind == "sync" then return self:snapshot(sender,rid,"accepted","none","state") end
        local previous = registry[rid]
        if previous then
            if not same(previous.body,r) then return reply("request_conflict") end
            return self:snapshot(sender,rid,previous.status,previous.reason,"state")
        end
        if registry_count >= 128 then return reply("dedup_limit") end
        local record={body={},status="rejected",reason="not_ready"}
        for k,v in pairs(r) do record.body[k]=v end
        registry[rid]=record;registry_count=registry_count+1
        local function reject(why) record.reason=why;return reply(why) end
        if r.session_id ~= session then return reject("stale_session") end
        if r.actor_id ~= actor then return reject("unauthorized") end
        if r.generation ~= generation then return reject("stale_generation") end
        if r.epoch ~= epoch then return reject("stale_epoch") end
        if not o or closed or blocked_generation==generation then return reject("not_ready") end
        if paused() then return reject("paused") end
        if mode == "MANUAL" and time >= deadline then finish("expired");return reject("stale_epoch") end
        local result
        busy=true
        if kind == "acquire" then
            if mode ~= "AI" then busy=false;return reject("not_ai") end
            if not effect(ports.stop) then failed("engine_failed");busy=false;return reject("engine_failed") end
            if not current(generation,entity_index) then busy=false;return reject("not_ready") end
            if epoch >= MAX then closed=true;busy=false;return reject("not_ready") end
            epoch=epoch+1;mode="MANUAL";deadline=time+5;target=nil
            result=self:snapshot(sender,rid,"accepted","none","granted")
        elseif kind == "move" then
            if mode ~= "MANUAL" then busy=false;return reject("not_manual") end
            local dx,dy=r.x-o.x,r.y-o.y
            if math.abs(r.x)>16000 or math.abs(r.y)>16000 or math.abs(r.z)>2048 or dx*dx+dy*dy>2000*2000
                or (ports.valid_position~=nil and not effect(ports.valid_position,r.x,r.y,r.z,o)) then
                busy=false;return reject("invalid_position")
            end
            if not current(generation,entity_index) then busy=false;return reject("not_ready") end
            if not effect(ports.move,r.x,r.y,r.z) then failed("engine_failed");busy=false;return reject("engine_failed") end
            manual_count=math.min(MAX,manual_count+1);target={x=r.x,y=r.y,z=r.z}
            result=self:snapshot(sender,rid,"accepted","none","move_issued")
        else
            if mode ~= "MANUAL" then busy=false;return reject("not_manual") end
            result=finish("cancelled",rid)
        end
        busy=false
        record.status=result.request_status;record.reason=result.reason
        return result
    end
    function self:tick()
        if busy then return end
        busy=true;cleanup_deferred_stop();busy=false
        local o=refresh()
        if not o or paused() or blocked_generation==generation then return end
        busy=true
        if mode == "MANUAL" then
            if time >= deadline then finish("expired")
            elseif target and (o.x-target.x)^2+(o.y-target.y)^2<=80*80 then finish("arrived")
            elseif last_state==nil or time-last_state>=1 then publish("none","state") end
        elseif mode == "INACTIVE" then resume(o,nil,nil,"ai_resumed")
        elseif last_ai==nil or time-last_ai>=1 then
            if effect(ports.ai,o) then
                ai_count=math.min(MAX,ai_count+1);last_ai=time
                if last_state==nil or time-last_state>=1 then publish("none","state") end
            else failed("engine_failed") end
        end
        busy=false
    end
    function self:close()
        if closed then return end
        read_clock()
        if mode ~= "INACTIVE" then
            if paused() then defer_stop() else effect(ports.stop) end
        end
        closed=true;revoke();publish("none","ended")
    end
    return self
end
return module
