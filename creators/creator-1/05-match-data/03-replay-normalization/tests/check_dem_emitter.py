"""Explicit real-input emitter check; never part of ordinary unittest discovery."""
import argparse
import json
import subprocess
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    for name in ['java-home','classpath','input','schema','staging']:p.add_argument('--'+name,required=True)
    p.add_argument('--match-id',default='9042986015');p.add_argument('--account-id',default='70388657')
    p.add_argument('--expect-code',type=int,required=True);a=p.parse_args()
    stage=Path(a.staging);stage.mkdir(exist_ok=False)
    limits=stage/'limits.json';limits.write_text(json.dumps({'max_states':2000000,'max_events':2000000,
        'max_line_bytes':65536,'max_output_bytes':536870912,'fields':['raw_position','raw_control']}))
    command=[str(Path(a.java_home)/'bin/java.exe'),'-Xmx512m','-cp',a.classpath,'TelemetryEmitter',
             '--input',a.input,'--schema',a.schema,'--staging',a.staging,'--limits-json',str(limits),
             '--match-id',a.match_id,'--account-id',a.account_id]
    result=subprocess.run(command,capture_output=True,timeout=300)
    (stage/'stdout.log').write_bytes(result.stdout);(stage/'stderr.log').write_bytes(result.stderr)
    assert result.returncode==a.expect_code,(result.returncode,result.stderr[-1200:].decode(errors='replace'))
    summary=stage/'emitter-summary.json'
    assert summary.exists()==(a.expect_code==0)
    print(json.dumps({'code':result.returncode,'staging':str(stage),'eof':summary.exists()}))

if __name__=='__main__':main()
