#!/usr/bin/env python3
# Consolida timelines CSV + metrics CSV → outputs/indices/<evento>/iasi.json
import csv, json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT_TIMELINES = ROOT / "outputs" / "timelines"
OUT_METRICS = ROOT / "outputs" / "metrics"
OUT_INDICES = ROOT / "outputs" / "indices"
OUT_INDICES.mkdir(parents=True, exist_ok=True)

EVENTS = [
    {"name":"Valdivia_1960","lat":-39.8,"lon":-73.2,"aoi_path":"config/aoi_valdivia.geojson"},
    {"name":"Maule_2010","lat":-35.0,"lon":-72.5,"aoi_path":"config/aoi_maule.geojson"},
    {"name":"Illapel_2015","lat":-31.6,"lon":-71.2,"aoi_path":"config/aoi_illapel.geojson"},
    {"name":"EC_CO_1906","lat":1.0,"lon":-80.0,"aoi_path":"config/aoi_ec_co_1906.geojson"}
]

def read_timeline_csv(path):
    if not Path(path).exists(): return []
    with open(path,"r",encoding="utf-8") as f:
        r=csv.DictReader(f)
        out=[]
        for row in r:
            out.append({
                "date": row["date"],
                "A": float(row["A"]),
                "R": float(row["R"]),
                "D": float(row["D"]),
                "M": float(row["M"]),
                "S": float(row["S"]),
                "IASi": float(row["IASi"])
            })
        return out

def read_metrics_csv(path):
    if not Path(path).exists(): return None
    with open(path,"r",encoding="utf-8") as f:
        r=csv.DictReader(f)
        rows=list(r)
        if not rows: return None
        row=rows[0]
        return {
            "auc_pr": float(row["AUC_PR"]),
            "f1": float(row["F1"]),
            "false_alarm_pm": float(row["false_alarms_per_month"]),
            "lead_time_days": float(row["lead_time_days"]),
            "brier": float(row["brier"]),
            "best_threshold": float(row["best_threshold"])
        }

def main():
    for ev in EVENTS:
        name = ev["name"]
        tl = read_timeline_csv(OUT_TIMELINES / f"{name}_iasi.csv")
        metrics = {}
        for win in ("7","14","30"):
            m = read_metrics_csv(OUT_METRICS / f"{name}_metrics_{win}d.csv")
            if m: metrics[win]=m
        # include config weights and thresholds if available
        cfg_dir = Path(__file__).resolve().parents[1] / "config"
        weights = None
        thresholds = None
        try:
            wfile = cfg_dir / "weights.yaml"
            if wfile.exists():
                with open(wfile, 'r', encoding='utf-8') as f:
                    weights = yaml.safe_load(f)
        except Exception:
            weights = None
        try:
            tfile = cfg_dir / "thresholds.yaml"
            if tfile.exists():
                with open(tfile, 'r', encoding='utf-8') as f:
                    thresholds = yaml.safe_load(f)
        except Exception:
            thresholds = None

        payload = {
            "meta": {
                "name": name,
                "lat": ev["lat"],
                "lon": ev["lon"],
                "aoi_path": ev["aoi_path"],
                "team": "Los Abejorros Científicos",
                "members": [
                    "Roxana Andrea Salazar Marín",
                    "Greimar José Salazar Marín",
                    "Jhon Alexandre Meneses Ospina"
                ],
                "weights": weights,
                "thresholds": thresholds
            },
            "timeline": tl,
            "metrics": metrics
        }
        outdir = OUT_INDICES / name
        outdir.mkdir(parents=True, exist_ok=True)
        with open(outdir/"iasi.json","w",encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    print("OK: iasi.json generado por evento en outputs/indices/")

if __name__=="__main__":
    main()
