import yaml
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / 'config'

def write_yaml(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

def apply_and_regen(weights=None, thresholds=None):
    if weights:
        write_yaml(CFG / 'weights.yaml', weights)
    if thresholds:
        write_yaml(CFG / 'thresholds.yaml', thresholds)
    # run pipeline
    py = sys.executable
    subprocess.check_call([py, str(ROOT / 'scripts' / 'run_eval_batch.py')])
    subprocess.check_call([py, str(ROOT / 'scripts' / 'export_iasi_json.py')])

if __name__=='__main__':
    # ejemplo: cambia ligeramente los pesos
    w = {'alpha':0.3,'beta':0.2,'gamma':0.2,'delta':0.15,'epsilon':0.15}
    t = {'observation':0.48,'caution_min':0.48,'caution_max':0.68,'alert':0.72}
    apply_and_regen(w,t)
