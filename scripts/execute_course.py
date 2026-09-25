"""Execute selected notebooks in fresh kernels; persist failures rather than hiding them."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import argparse
import json
import platform
import sqlite3
import subprocess
import time
import traceback
import importlib.metadata
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]

def execute_one(path_string):
    path = Path(path_string)
    nb = nbformat.read(path, as_version=4)
    record = {'id': nb.metadata.course.id, 'path':str(path.relative_to(ROOT)),
              'started_utc':datetime.now(timezone.utc).isoformat()}
    start = time.monotonic()
    try:
        nbformat.validate(nb)
        record['format_validation'] = 'passed'
        for cell in nb.cells:
            if cell.cell_type == 'code':
                cell.outputs = []
                cell.execution_count = None
        NotebookClient(nb, timeout=90, kernel_name='python3', allow_errors=False,
                       resources={'metadata':{'path':str(path.parent)}},
                       record_timing=False).execute()
        record['execution'] = 'passed'
        record['code_cells'] = sum(c.cell_type == 'code' for c in nb.cells)
        record['executed_code_cells'] = sum(c.cell_type == 'code' and c.execution_count is not None for c in nb.cells)
        assert record['code_cells'] == record['executed_code_cells']
        assert not any(o.output_type == 'error' for c in nb.cells if c.cell_type == 'code' for o in c.outputs)
    except Exception as error:
        record['execution'] = 'failed'
        record['error'] = f'{type(error).__name__}: {error}'
        record['traceback'] = traceback.format_exc()
    record['elapsed_seconds'] = round(time.monotonic()-start,3)
    record['finished_utc'] = datetime.now(timezone.utc).isoformat()
    nb.metadata.course.execution = record['execution']
    nbformat.write(nb, path)
    return record

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', nargs='*', help='e.g. N001 N002; default all existing notebooks')
    parser.add_argument('--workers',type=int,default=4)
    args = parser.parse_args()
    paths = sorted((ROOT/'notebooks').rglob('*.ipynb'))
    if args.ids:
        wanted = {x.upper() for x in args.ids}
        paths = [p for p in paths if 'N'+p.name[:3] in wanted]
        if len(paths) != len(wanted):
            raise SystemExit('One or more requested notebook IDs are missing')
    report_path = ROOT/'reports/execution.json'
    existing = json.loads(report_path.read_text()) if report_path.exists() else {'results':[]}
    records = {r['id']:r for r in existing['results']}
    env = {'python':platform.python_version(), 'platform':platform.platform(), 'sqlite':sqlite3.sqlite_version,
           'packages':{p:importlib.metadata.version(p) for p in ['nbformat','nbclient','ipykernel','pandas']}}
    try:
        env['node'] = subprocess.run(['node','--version'],text=True,capture_output=True,check=True).stdout.strip()
    except (FileNotFoundError,subprocess.CalledProcessError) as error:
        env['node'] = f'unavailable: {type(error).__name__}'
    env['bash'] = subprocess.run(['bash','--version'],text=True,capture_output=True,check=True).stdout.splitlines()[0]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(execute_one,str(p)) for p in paths]
        for future in as_completed(futures):
            record = future.result()
            records[record['id']] = record
            output = {'environment':env,'updated_utc':datetime.now(timezone.utc).isoformat(),
                      'results':sorted(records.values(),key=lambda r:r['id'])}
            report_path.parent.mkdir(exist_ok=True)
            report_path.write_text(json.dumps(output,ensure_ascii=False,indent=2))
            print(record['id'],record['execution'],record.get('error','').split('\n')[0],flush=True)
    if any(records['N'+p.name[:3]]['execution'] != 'passed' for p in paths):
        raise SystemExit(1)
