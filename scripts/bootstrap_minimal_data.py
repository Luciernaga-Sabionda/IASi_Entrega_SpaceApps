#!/usr/bin/env python3
"""
Crea carpetas necesarias y plantillas mínimas de catálogo/timelines si no existen.
Útil para demo rápido antes de cargar datos reales.
"""
from pathlib import Path
import csv, argparse, math, random
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_TIMELINES = ROOT / "outputs" / "timelines"
OUT_METRICS = ROOT / "outputs" / "metrics"
OUT_INDICES = ROOT / "outputs" / "indices"

for d in (OUT_TIMELINES, OUT_METRICS, OUT_INDICES):
    d.mkdir(parents=True, exist_ok=True)

CAT_DIR = DATA / "catalogs"
CAT_DIR.mkdir(parents=True, exist_ok=True)

def create_catalogs():
    catalogs = {
        "Valdivia_1960.csv": [("1960-05-22",9.5)],
        "Maule_2010.csv": [("2010-02-27",8.8)],
        "Illapel_2015.csv": [("2015-09-16",8.3)],
        "EC_CO_1906.csv": [("1906-01-31",8.8)],
    }
    for name, rows in catalogs.items():
        p = CAT_DIR / name
        if not p.exists():
            with p.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["date","mw"])
                for r in rows:
                    w.writerow(r)
            print(f"Creado catálogo de ejemplo: {p}")

def fetch_usgs_catalog(bbox=None, starttime='1900-01-01', endtime='2025-12-31', minmagnitude=6.5):
    # Consulta sencilla a la API de USGS (https://earthquake.usgs.gov/fdsnws/event/1/)
    import requests
    params = {
        'format': 'geojson',
        'starttime': starttime,
        'endtime': endtime,
        'minmagnitude': minmagnitude,
        'limit': 20000
    }
    if bbox:
        params.update({'minlatitude': bbox[0], 'minlongitude': bbox[1], 'maxlatitude': bbox[2], 'maxlongitude': bbox[3]})
    url = 'https://earthquake.usgs.gov/fdsnws/event/1/query'
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def usgs_to_csv(json_gj, out_path):
    # Extrae date,mw
    features = json_gj.get('features', [])
    rows = []
    for f in features:
        props = f.get('properties', {})
        t = props.get('time')
        if t is None: continue
        dt = datetime.utcfromtimestamp(t/1000).strftime('%Y-%m-%d')
        mw = props.get('mag')
        if mw is None: continue
        rows.append((dt, mw))
    rows = sorted(set(rows))
    with out_path.open('w', encoding='utf-8', newline='') as f:
        import csv as _csv
        w = _csv.writer(f)
        w.writerow(['date','mw'])
        for r in rows:
            w.writerow(r)

def create_demo_timelines():
    # crea timelines demo sencillos en outputs/timelines si no existen
    import csv
    for ev in ['Valdivia_1960','Maule_2010','Illapel_2015','EC_CO_1906']:
        p = OUT_TIMELINES / f"{ev}_iasi.csv"
        if p.exists(): continue
        with p.open('w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['date','A','R','D','M','S','IASi','estado'])
            from datetime import date, timedelta
            today = date.today()
            for i in range(30):
                d = today - timedelta(days=29-i)
                A = round(0.3+0.2*math.sin(i/5),4)
                R = round(0.4+0.15*math.cos(i/6),4)
                D = round(0.2+0.5*max(0,math.sin(i/9)),4)
                M = round(0.2+0.3*random.random(),4)
                S = round(0.3+0.2*math.cos(i/7),4)
                IASi = round(0.25*A+0.20*R+0.25*D+0.15*M+0.15*S,4)
                state = 'Observación' if IASi < 0.5 else ('Precaución' if IASi <= 0.69 else 'Alerta')
                w.writerow([d.isoformat(),A,R,D,M,S,IASi,state])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-usgs", action="store_true", help="Descargar catálogos USGS para eventos modernos")
    ap.add_argument("--with-demo", action="store_true", help="Crear timelines demo en outputs/timelines")
    args = ap.parse_args()
    create_catalogs()
    if args.with_usgs:
        try:
            from datetime import datetime
            print('Descargando catálogos USGS (esto puede tardar)...')
            # Ejemplo simple: descarga global para magnitudes >=6.5 en 1900-2025
            gj = fetch_usgs_catalog(starttime='1900-01-01', endtime='2025-12-31', minmagnitude=6.5)
            out = CAT_DIR / 'USGS_global_6.5plus.csv'
            usgs_to_csv(gj, out)
            print(f'Catálogo USGS guardado en {out}')
        except Exception as e:
            print('Error descargando USGS:', e)
    if args.with_demo:
        create_demo_timelines()
        print('Timelines demo creados en outputs/timelines')
    print('Bootstrap completado. Revisa data/catalogs/ y outputs/')

if __name__=="__main__":
    main()
