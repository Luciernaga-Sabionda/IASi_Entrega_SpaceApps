#!/usr/bin/env python3
"""
Watcher simple para procesar archivos satelitales colocados en data/inbox_sat.
Coloca CSV en esa carpeta; el watcher los moverá a data/inbox_sat/processed y ejecutará
el adaptador + pipeline.

Uso:
  python scripts/watcher_ingest.py --run-pipeline
"""
import time
from pathlib import Path
import shutil
import subprocess
import argparse


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--inbox', default='data/inbox_sat')
    p.add_argument('--processed', default='data/inbox_sat/processed')
    p.add_argument('--poll', type=int, default=10, help='Polling seconds')
    p.add_argument('--run-pipeline', action='store_true', help='Run run_eval_batch.py after ingest')
    return p.parse_args()


def main():
    args = parse_args()
    inbox = Path(args.inbox)
    processed = Path(args.processed)
    inbox.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)
    print('Watcher started. Inbox:', inbox)
    while True:
        for f in list(inbox.glob('*.csv')):
            try:
                print('Processing', f)
                # call ingest script
                cmd = ['python', 'scripts/ingest_satellite.py', '-i', str(f), '-e', f.stem, '--mode', 'append']
                subprocess.check_call(cmd)
                # move to processed
                dest = processed / f.name
                shutil.move(str(f), str(dest))
                print('Moved to', dest)
                if args.run_pipeline:
                    subprocess.check_call(['python', 'scripts/run_eval_batch.py'])
                    subprocess.check_call(['python', 'scripts/export_iasi_json.py'])
            except Exception as e:
                print('Error processing', f, e)
        time.sleep(args.poll)


if __name__ == '__main__':
    main()
