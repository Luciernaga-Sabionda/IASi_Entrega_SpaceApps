import csv
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT_METRICS = ROOT / 'outputs' / 'metrics'
OUT_DIR = ROOT / 'outputs' / 'figures'
OUT_DIR.mkdir(parents=True, exist_ok=True)

def read_metric_csv(path):
    with open(path, 'r', encoding='utf-8') as f:
        r = csv.DictReader(f)
        rows = list(r)
        if not rows:
            return None
        return rows[0]

def plot_summary():
    events = []
    aucs = { '7':[], '14':[], '30':[] }
    for f in OUT_METRICS.glob('*_metrics_7d.csv'):
        name = f.name.split('_metrics_')[0]
        events.append(name)
        for win in ('7','14','30'):
            p = OUT_METRICS / f"{name}_metrics_{win}d.csv"
            m = read_metric_csv(p)
            aucs[win].append(float(m['AUC_PR']) if m else 0.0)
    x = range(len(events))
    plt.figure(figsize=(9,4))
    plt.plot(x, aucs['7'], marker='o', label='AUC_PR 7d')
    plt.plot(x, aucs['14'], marker='o', label='AUC_PR 14d')
    plt.plot(x, aucs['30'], marker='o', label='AUC_PR 30d')
    plt.xticks(x, events, rotation=45)
    plt.ylabel('AUC-PR')
    plt.legend()
    plt.tight_layout()
    out = OUT_DIR / 'metrics_summary_aucpr.png'
    plt.savefig(out, dpi=150)
    print('Saved', out)

if __name__=='__main__':
    plot_summary()
