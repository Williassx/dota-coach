import java.util.*;

/** Pure replay identity/clock logic. Raw field semantics are deliberately limited. */
public final class TelemetryCore {
    public record HeroReference(long accountId,String steamId,long fullHandle,int index,int serial,
                                String className,boolean existent,Boolean illusion,boolean authoritativeReference) {}
    public record BindingObservation(int demoTick,List<HeroReference> candidates) {}
    public record BindingResult(long epoch,HeroReference actor,String reason) {}
    public record ClockObservation(int demoTick,int serverTick,Double startSeconds,int pauseTotalTicks,
                                   Integer pauseStartTick,boolean paused,double tickSeconds) {}
    public record ClockResult(long epoch,Double gameSeconds,String reason) {}
    private HeroReference actor;
    private long bindingEpoch=0,clockEpoch=0;
    private int lastBindingTick=-1,lastClockTick=-1,lastServer=-1;
    private Double lastStart;
    public static String uint64(long bits) { return Long.toUnsignedString(bits); }
    public BindingResult updateBinding(BindingObservation o) {
        var eligible=o.candidates().stream().filter(h->h.existent() && h.authoritativeReference() && !Boolean.TRUE.equals(h.illusion())).toList();
        HeroReference next=eligible.size()==1?eligible.get(0):null;
        if(o.demoTick()<lastBindingTick || !Objects.equals(actor,next)) bindingEpoch++;
        actor=next;lastBindingTick=o.demoTick();
        return new BindingResult(bindingEpoch,next,next==null?(eligible.isEmpty()?"unassigned":"ambiguous"):
            (next.illusion()==null?"clone_classification_unknown":"assigned_reference"));
    }
    public ClockResult clock(ClockObservation o) {
        if(!Double.isFinite(o.tickSeconds()) || o.tickSeconds()<=0 || o.serverTick()<0 || o.pauseTotalTicks()<0 ||
           (o.startSeconds()!=null&&!Double.isFinite(o.startSeconds()))) throw new IllegalArgumentException("invalid_clock");
        if(o.demoTick()<lastClockTick || o.serverTick()<lastServer || !Objects.equals(lastStart,o.startSeconds())) clockEpoch++;
        lastClockTick=o.demoTick();lastServer=o.serverTick();lastStart=o.startSeconds();
        if(o.startSeconds()==null || o.startSeconds()==0) return new ClockResult(clockEpoch,null,"clock_unknown");
        if(o.paused() && (o.pauseStartTick()==null || o.pauseStartTick()<0 || o.pauseStartTick()>o.serverTick()))
            throw new IllegalArgumentException("invalid_pause_clock");
        long tick=o.paused()?o.pauseStartTick():o.serverTick();
        double seconds=(tick-o.pauseTotalTicks())*o.tickSeconds()-o.startSeconds();
        if(!Double.isFinite(seconds)) throw new IllegalArgumentException("nonfinite_clock");
        return new ClockResult(clockEpoch,seconds,"observed_network_clock");
    }
}
