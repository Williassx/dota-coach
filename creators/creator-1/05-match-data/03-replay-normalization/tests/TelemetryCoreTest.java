import java.util.*;

public class TelemetryCoreTest {
    static TelemetryCore.HeroReference hero(int serial, Boolean illusion) {
        return new TelemetryCore.HeroReference(42,"76561197960265770",1000L+serial,7,serial,"TEST_Hero",true,illusion,true);
    }
    public static void main(String[] args) {
        TelemetryCore core=new TelemetryCore();
        var a=core.updateBinding(new TelemetryCore.BindingObservation(1,List.of(hero(1,null))));
        assert a.actor()!=null;
        var b=core.updateBinding(new TelemetryCore.BindingObservation(2,List.of(hero(2,null))));
        assert b.epoch()>a.epoch() && b.actor().serial()==2 : "index reuse";
        assert core.updateBinding(new TelemetryCore.BindingObservation(3,List.of(hero(2,null),hero(3,false)))).actor()==null : "ambiguous";
        assert core.updateBinding(new TelemetryCore.BindingObservation(4,List.of(hero(3,true)))).actor()==null : "illusion";
        assert core.updateBinding(new TelemetryCore.BindingObservation(5,List.of())).actor()==null : "deleted";
        assert core.clock(new TelemetryCore.ClockObservation(0,463,null,0,null,false,1.0/30)).gameSeconds()==null;
        double unpaused=core.clock(new TelemetryCore.ClockObservation(10,1000,10.0,10,null,false,1.0/30)).gameSeconds();
        assert Math.abs(unpaused-23.0)<1e-9;
        double paused=core.clock(new TelemetryCore.ClockObservation(20,1300,10.0,10,1000,true,1.0/30)).gameSeconds();
        assert Math.abs(paused-unpaused)<1e-9 : "pause freeze";
        assert TelemetryCore.uint64(-1L).equals("18446744073709551615");
        assert TelemetryCore.uint64(Long.MIN_VALUE).equals("9223372036854775808");
        try { core.clock(new TelemetryCore.ClockObservation(21,1000,Double.NaN,0,null,false,1.0/30)); throw new AssertionError("NaN accepted"); }
        catch(IllegalArgumentException expected) {}
        var reset=core.updateBinding(new TelemetryCore.BindingObservation(0,List.of(hero(2,null))));
        assert reset.epoch()>b.epoch() : "seek epoch";
        System.out.println("TelemetryCore tests PASS: lifecycle/ambiguity/illusion/pause/unsigned/unknown/seek");
    }
}
