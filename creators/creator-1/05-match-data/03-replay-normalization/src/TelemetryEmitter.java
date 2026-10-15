import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;
import com.google.gson.*;
import skadistats.clarity.Clarity;
import skadistats.clarity.model.*;
import skadistats.clarity.model.s2.S2FieldPath;
import skadistats.clarity.state.s2.S2EntityState;
import skadistats.clarity.processor.entities.*;
import skadistats.clarity.processor.reader.*;
import skadistats.clarity.processor.gameevents.OnCombatLogEntry;
import skadistats.clarity.processor.runner.*;
import skadistats.clarity.source.MappedFileSource;
import skadistats.clarity.wire.shared.common.proto.CommonNetworkBaseTypes.CNETMsg_Tick;

/** One offline, fail-closed extractor. It cannot publish a completed import. */
@UsesEntities
public final class TelemetryEmitter implements AutoCloseable {
    static final Gson GSON=new GsonBuilder().serializeNulls().disableHtmlEscaping().create();
    static final Pattern STEAM=Pattern.compile("m_vecPlayerData\\.(\\d+)\\.m_iPlayerSteamID");
    static final class Failure extends RuntimeException { final int code; Failure(int c,String s){super(s);code=c;} }
    static Map<String,Object> obj(Object... kv) {
        Map<String,Object> m=new TreeMap<>();for(int i=0;i<kv.length;i+=2)m.put((String)kv[i],kv[i+1]);return m;
    }
    final Path out;
    final JsonObject expected,limits;
    final Map<String,Object> observed=new TreeMap<>();
    final Map<String,skadistats.clarity.model.s2.Field> fieldCache=new HashMap<>();
    final Set<String> requested=new HashSet<>();
    final TelemetryCore core=new TelemetryCore();
    final BufferedWriter states,events,gaps;
    final long account;
    final String steamId,heroName;
    long realTicks=0,syntheticTicks=0,stateCount=0,eventCount=0,gapCount=0,bytes=0,unassigned=0;
    int serverTick=-1,lastTick=-1;
    boolean mismatch=false;
    TelemetryEmitter(Path output,JsonObject schema,JsonObject lim,long accountId,String steam,String hero)throws IOException {
        out=output;expected=schema.getAsJsonObject("fields");limits=lim;account=accountId;steamId=steam;heroName=hero;
        if(expected==null)throw new Failure(2,"schema_fields_required");
        for(var f:lim.getAsJsonArray("fields"))requested.add(f.getAsString());
        states=Files.newBufferedWriter(out.resolve("states.jsonl"),StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
        events=Files.newBufferedWriter(out.resolve("events.jsonl"),StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
        gaps=Files.newBufferedWriter(out.resolve("gaps.jsonl"),StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
    }
    long limit(String key) {return limits.get(key).getAsLong();}
    void line(BufferedWriter writer,Map<String,Object> row)throws IOException {
        String s=GSON.toJson(row)+"\n";int n=s.getBytes(StandardCharsets.UTF_8).length;
        if(n>limit("max_line_bytes") || (bytes+=n)>limit("max_output_bytes"))throw new Failure(6,"output_limit");
        if(!mismatch)writer.write(s);
    }
    Object read(Entity e,String name,boolean required) {
        var fp=e.getFieldPathForName(name);
        if(fp==null) {if(required)throw new Failure(2,"required_field_missing:"+e.getDtClass().getDtName()+":"+name);return null;}
        var state=(S2EntityState)e.getState();var field=state.getFieldForFieldPath((S2FieldPath)fp);
        String key=e.getDtClass().getDtName()+":"+name.replaceAll("\\.\\d+(?=\\.)",".*");
        if(fieldCache.get(key)!=field) {
          var props=field.getSerializerProperties();
          var descriptor=obj("type",field.getType().toString(),"decoder",field.getDecoder()==null?null:field.getDecoder().getClass().getName(),
            "bit_count",props==null?null:props.getBitCount(),"encode_flags",props==null?null:props.getEncodeFlags(),
            "low",props==null?null:props.getLowValue(),"high",props==null?null:props.getHighValue(),
            "encoder",props==null?null:props.getEncoderType());
          Object old=observed.put(key,descriptor);
          if(old!=null && !GSON.toJsonTree(old).equals(GSON.toJsonTree(descriptor)))throw new Failure(2,"schema_changed_midstream:"+key);
          if(!expected.has(key) || !expected.get(key).equals(JsonParser.parseString(GSON.toJson(descriptor)))) mismatch=true;
          fieldCache.put(key,field);
        }
        Object value=e.getPropertyForFieldPath(fp);
        if(value instanceof Float f && !Float.isFinite(f) || value instanceof Double d && !Double.isFinite(d))throw new Failure(4,"nonfinite:"+name);
        if(required && value==null)throw new Failure(4,"null_required:"+name);
        return value;
    }
    Number number(Entity e,String name) {
        Object v=read(e,name,true);if(!(v instanceof Number))throw new Failure(2,"numeric_type:"+name);return (Number)v;
    }
    void gap(int tick,long epoch,String reason)throws IOException {
        line(gaps,obj("seq",gapCount++,"start_demo_tick",tick,"end_demo_tick",tick,"binding_epoch",epoch,
            "reason",reason,"affected_capabilities",List.of("actor_resources")));
    }
    @OnMessage(CNETMsg_Tick.class) public void tickMessage(CNETMsg_Tick msg){if(!msg.hasTick())throw new Failure(4,"missing_network_tick");serverTick=msg.getTick();}
    @OnCombatLogEntry public void combat(Context context,CombatLogEntry e)throws IOException {
        if(!heroName.equals(e.getTargetName()) && !heroName.equals(e.getAttackerName()))return;
        if(eventCount>=limit("max_events"))throw new Failure(6,"event_limit");
        line(events,obj("seq",eventCount++,"demo_tick",context.getTick(),"server_tick",serverTick<0?null:serverTick,
            "combat_timestamp",e.getTimestamp(),"game_seconds",null,"type",e.getType().name(),"target",e.getTargetName(),
            "attacker",e.getAttackerName(),"inflictor",e.getInflictorName(),"value",e.getValue(),
            "is_target_illusion",e.isTargetIllusion(),"full_entity_reference",null,"actor_link","candidate_name_only",
            "knowledge_scope","spectator_research"));
    }
    @OnTickEnd public void tick(Context context,boolean synthetic)throws IOException {
        lastTick=context.getTick();if(synthetic){syntheticTicks++;return;}realTicks++;
        if(realTicks>limit("max_states"))throw new Failure(6,"state_limit");
        Entities entities=context.getProcessor(Entities.class);
        List<TelemetryCore.HeroReference> candidates=new ArrayList<>();
        Map<Long,String> referencePaths=new HashMap<>();
        for(Entity resource:entities.stream().filter(e->e.getDtClass().getDtName().equals("CDOTA_PlayerResource")).toList()) {
            var it=resource.getState().fieldPathIterator();
            List<String> steamPaths=new ArrayList<>();
            while(it.hasNext()) {String name=resource.getNameForFieldPath(it.next());if(name!=null && STEAM.matcher(name).matches())steamPaths.add(name);}
            for(String name:steamPaths) {
                Object raw=read(resource,name,true);
                if(!(raw instanceof Long))throw new Failure(2,"steam_identifier_type");
                long id=(Long)raw;
                if((id&0xffffffffL)!=account)continue;
                if(!Long.toUnsignedString(id).equals(steamId))throw new Failure(3,"steam_identity_conflict");
                var matcher=STEAM.matcher(name);matcher.matches();String slot=matcher.group(1);
                for(String suffix:List.of("m_hSelectedHero","m_hAssignedHero")) {
                    String ref="m_vecPlayerTeamData."+slot+"."+suffix;
                    Object handle=read(resource,ref,false);if(handle==null)continue;
                    if(!(handle instanceof Integer))throw new Failure(2,"hero_reference_type");
                    int h=(Integer)handle;Entity hero=entities.getByHandle(h);
                    if(hero==null || hero.getHandle()!=h || !hero.isExistent())continue;
                    if(!hero.getDtClass().getDtName().startsWith("CDOTA_Unit_Hero_"))throw new Failure(3,"assigned_nonhero");
                    Object illusion=read(hero,"m_bIsIllusion",false);
                    if(illusion!=null && !(illusion instanceof Boolean))throw new Failure(2,"illusion_type");
                    var candidate=new TelemetryCore.HeroReference(account,steamId,Integer.toUnsignedLong(h),hero.getIndex(),hero.getSerial(),
                        hero.getDtClass().getDtName(),true,(Boolean)illusion,true);
                    if(!candidates.contains(candidate))candidates.add(candidate);
                    referencePaths.put(candidate.fullHandle(),ref);
                }
            }
        }
        var binding=core.updateBinding(new TelemetryCore.BindingObservation(lastTick,candidates));
        if(binding.actor()==null){unassigned++;gap(lastTick,binding.epoch(),binding.reason());return;}
        if(serverTick<0)throw new Failure(4,"missing_server_tick");
        var clocks=entities.stream().filter(e->e.getDtClass().getDtName().equals("CDOTAGamerulesProxy")).toList();
        if(clocks.size()!=1)throw new Failure(4,"ambiguous_clock");
        Entity clock=clocks.get(0);String prefix="m_pGameRules.";
        double start=number(clock,prefix+"m_flGameStartTime").doubleValue();
        int pauseTotal=number(clock,prefix+"m_nTotalPausedTicks").intValue();
        int pauseStart=number(clock,prefix+"m_nPauseStartTick").intValue();
        Object pausedValue=read(clock,prefix+"m_bGamePaused",true);
        if(!(pausedValue instanceof Boolean))throw new Failure(2,"paused_type");
        boolean paused=(Boolean)pausedValue;
        var time=core.clock(new TelemetryCore.ClockObservation(lastTick,serverTick,start,pauseTotal,pauseStart,paused,context.getMillisPerTick()/1000.0));
        var actor=binding.actor();Entity hero=entities.getByHandle((int)actor.fullHandle());
        Map<String,Object> resources=obj("hp",number(hero,"m_iHealth"),"max_hp",number(hero,"m_iMaxHealth"),
            "mana",number(hero,"m_flMana"),"max_mana",number(hero,"m_flMaxMana"));
        List<String> unknown=new ArrayList<>(List.of(binding.reason(),"player_id_semantics_unknown","fog_unknown","world_transform_unknown"));
        if(time.gameSeconds()==null)unknown.add("clock_unknown");
        Map<String,Object> row=obj("seq",stateCount++,"demo_tick",lastTick,"server_tick",serverTick,"binding_epoch",binding.epoch(),
            "clock_epoch",time.epoch(),"actor",obj("account32",account,"steam64",steamId,"full_handle",actor.fullHandle(),
                "index",actor.index(),"serial",actor.serial(),"class",actor.className(),"reference_path",referencePaths.get(actor.fullHandle())),
            "resources",resources,"clock",obj("start",start,"pause_total",pauseTotal,"pause_start",pauseStart,"paused",paused,"game_seconds",time.gameSeconds(),"tick_interval_seconds",context.getMillisPerTick()/1000.0),
            "phase_raw",read(clock,prefix+"m_nGameState",true),"raw_player_id",read(hero,"m_iPlayerID",false),
            "unknown_reasons",unknown,"knowledge_scope","spectator_research");
        if(requested.contains("raw_control")) {
            Object rawState=read(hero,"m_nUnitState64",false);
            row.put("raw_state64",rawState==null?null:TelemetryCore.uint64(((Number)rawState).longValue()));
            row.put("raw_life_state",read(hero,"m_lifeState",false));
            unknown.add("control_semantics_unknown");
            if(rawState==null)unknown.add("state64_missing");
            if(row.get("raw_life_state")==null)unknown.add("life_state_missing");
        }
        if(requested.contains("raw_position")) {
            Map<String,Object> position=new TreeMap<>();
            for(String prop:List.of("m_cellX","m_cellY","m_cellZ","m_vecX","m_vecY","m_vecZ")) {
                Object value=read(hero,"CBodyComponent."+prop,false);position.put(prop,value);if(value==null)unknown.add("position_missing:"+prop);
            }
            row.put("raw_position",position);
        }
        if(time.gameSeconds()==null)gap(lastTick,binding.epoch(),"clock_unknown");
        line(states,row);
    }
    public void close()throws IOException { states.close();events.close();gaps.close(); }
    static Map<String,String> args(String[] args) {
        Map<String,String> map=new HashMap<>();if(args.length%2!=0)throw new Failure(2,"argument_pairs_required");
        for(int i=0;i<args.length;i+=2)if(map.put(args[i],args[i+1])!=null)throw new Failure(2,"duplicate_argument");return map;
    }
    public static void main(String[] argv) {
        TelemetryEmitter emitter=null;int code=0;
        try {
            var a=args(argv);Path input=Path.of(a.get("--input")),out=Path.of(a.get("--staging"));
            JsonObject profile=JsonParser.parseString(Files.readString(Path.of(a.get("--schema")))).getAsJsonObject();
            JsonObject lim=JsonParser.parseString(Files.readString(Path.of(a.get("--limits-json")))).getAsJsonObject();
            var info=Clarity.infoForFile(input.toString());
            if(!info.hasGameInfo()||!info.getGameInfo().hasDota())throw new Failure(2,"dota_metadata_missing");
            var dota=info.getGameInfo().getDota();long match=Long.parseUnsignedLong(a.get("--match-id"));
            if(!dota.hasMatchId()||dota.getMatchId()!=match)throw new Failure(3,"match_identity_mismatch");
            long account=Long.parseLong(a.get("--account-id"));
            var players=dota.getPlayerInfoList().stream().filter(p->p.hasSteamid() && (p.getSteamid()&0xffffffffL)==account && p.hasIsFakeClient() && !p.getIsFakeClient()).toList();
            if(players.size()!=1||!players.get(0).hasHeroName())throw new Failure(3,"roster_identity_ambiguous");
            var player=players.get(0);
            emitter=new TelemetryEmitter(out,profile,lim,account,Long.toUnsignedString(player.getSteamid()),player.getHeroName());
            try(var source=new MappedFileSource(input.toString())) {new SimpleRunner(source).runWith(emitter);}
            emitter.close();
            Files.writeString(out.resolve("observed-schema.json"),GSON.toJson(obj("schema","dem-schema-v1","fields",emitter.observed))+"\n");
            if(emitter.mismatch)throw new Failure(2,"unsupported_schema_profile");
            if(emitter.stateCount==0)throw new Failure(3,"actor_never_assigned");
            Files.writeString(out.resolve("emitter-summary.json"),GSON.toJson(obj("eof",true,"match_id",Long.toUnsignedString(match),"account_id",account,
                "real_ticks",emitter.realTicks,"synthetic_ticks",emitter.syntheticTicks,"states",emitter.stateCount,"events",emitter.eventCount,
                "gaps",emitter.gapCount,"unassigned",emitter.unassigned,"last_tick",emitter.lastTick,"verified_actor_events",false))+"\n",StandardOpenOption.CREATE_NEW);
        } catch(Throwable ex) {
            Throwable cause=ex;while(cause.getCause()!=null)cause=cause.getCause();
            code=cause instanceof Failure f?f.code:2;
            System.err.println(GSON.toJson(obj("error",cause.getMessage()==null?cause.getClass().getName():cause.getMessage(),"code",code)));
            if(emitter!=null) {try{emitter.close();}catch(Exception ignored){} }
        }
        if(code!=0)System.exit(code);
    }
}
