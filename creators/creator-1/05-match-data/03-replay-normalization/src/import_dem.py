"""Explicit offline DEM import CLI; importing this module does not run it."""
import argparse
import dataclasses
import sys
from pathlib import Path
from dem_inputs import validate_inputs
from dem_types import DemImportError, InputSpec, canonical_json
from dem_store import run_import

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['input','lock','config','output']: parser.add_argument('--'+key, type=Path, required=True)
    for key in ['match-id','account-id']: parser.add_argument('--'+key, type=int, required=True)
    args = parser.parse_args(argv)
    try:
        ctx = validate_inputs(InputSpec(args.input,args.match_id,args.account_id,args.lock,args.config,args.output))
        result = run_import(ctx)
        sys.stdout.buffer.write(canonical_json({'completed':True,**dataclasses.asdict(result)}))
        return 0
    except DemImportError as exc:
        sys.stdout.buffer.write(canonical_json({'completed':False,'code':exc.code,'reason':exc.reason}))
        return exc.code

if __name__ == '__main__': raise SystemExit(main())
