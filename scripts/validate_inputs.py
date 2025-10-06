#!/usr/bin/env python3
# Validador de entradas IASi (A/R/D/M/S + features por evento)
# Uso:
#   python scripts/validate_inputs.py
#   python scripts/validate_inputs.py --strict   # trata warnings como errores

import csv, sys, argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SCHEMAS = {
    "features": ["date","mean_defo_mm","p95_defo_mm","mean_coh","area_defo_gt10mm_km2"],
    "animals":  ["date","a_score","source"],
    "radon":    ["date","r_ppm","r_zscore"],
    "marine":   ["date","m_events_count","m_verified_ratio"],
    "sensors":  ["date","s_activity_z","s_duration_h"],
}

FEATURE_FILES = [
    DATA/"features"/"features_valdivia1960.csv",
    DATA/"features"/"features_maule2010.csv",
    DATA/"features"/"features_illapel2015.csv",
    DATA/"features"/"features_ec_co_1906.csv",
]

SIGNAL_FILES = {
    "animals": DATA/"signals"/"animals.csv",
    "radon":   DATA/"signals"/"radon.csv",
    "marine":  DATA/"signals"/"marine.csv",
    "sensors": DATA/"signals"/"sensors.csv",
}

WARN_COUNT = 0

def ok(msg): print(f"[OK] {msg}")

def warn(msg):
    global WARN_COUNT
    WARN_COUNT += 1
    print(f"[WARN] {msg}")

def err(msg): print(f"[ERROR] {msg}")

def read_csv(path: Path):
    if not path.exists():
        err(f"No existe el archivo: {path}")
        return None, []
    with path.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        headers = r.fieldnames or []
        rows = list(r)
    return headers, rows

def check_headers(file_path: Path, headers, required):
    missing = [h for h in required if h not in headers]
    extra = [h for h in headers if h not in required]
    if missing:
        err(f"{file_path.name}: faltan columnas: {missing}")
        return False
    if extra:
        warn(f"{file_path.name}: columnas extra ignoradas: {extra}")
    return True

def is_date(s):
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False

def check_dates(file_path: Path, rows):
    bad = [r.get("date","") for r in rows if not is_date(r.get("date",""))]
    if bad:
        err(f"{file_path.name}: fechas inválidas (YYYY-MM-DD): {bad[:5]}{' ...' if len(bad)>5 else ''}")
        return False
    return True

def check_numeric(file_path: Path, rows, cols, allow_nan=False):
    ok_all = True
    for c in cols:
        badv = []
        for i, r in enumerate(rows):
            v = r.get(c, "")
            if v == "" or v is None:
                if not allow_nan:
                    badv.append((i+2, v))  # +2 por header y 1-based
                continue
            try:
                float(v)
            except Exception:
                badv.append((i+2, v))
        if badv:
            err(f"{file_path.name}: columna '{c}' con valores no numéricos o vacíos en filas {badv[:5]}{' ...' if len(badv)>5 else ''}")
            ok_all = False
    return ok_all

def check_ranges(file_path: Path, rows, rules):
    """
    rules: dict col -> ('range', lo, hi) o ('min', m)
    """
    ok_all = True
    for c, rule in rules.items():
        if rule[0] == 'range':
            lo, hi = rule[1], rule[2]
            out = [(i+2, r.get(c,"")) for i,r in enumerate(rows)
                   if r.get(c,"")=="" or not is_float_between(r.get(c,""), lo, hi)]
            if out:
                warn(f"{file_path.name}: '{c}' fuera de [{lo},{hi}] o vacío en {out[:5]}{' ...' if len(out)>5 else ''}")
        elif rule[0] == 'min':
            m = rule[1]
            out = [(i+2, r.get(c,"")) for i,r in enumerate(rows)
                   if r.get(c,"")=="" or not is_float_ge(r.get(c,""), m)]
            if out:
                warn(f"{file_path.name}: '{c}' < {m} o vacío en {out[:5]}{' ...' if len(out)>5 else ''}")
    return ok_all

def is_float_between(v, lo, hi):
    try:
        x = float(v)
        return lo <= x <= hi
    except:
        return False

def is_float_ge(v, m):
    try:
        x = float(v)
        return x >= m
    except:
        return False

# Nuevas utilidades

def date_series(rows):
    out = []
    for r in rows:
        s = r.get("date","")
        try:
            out.append(datetime.strptime(s, "%Y-%m-%d").date())
        except Exception:
            pass
    return out

def check_duplicates_and_order(file_path: Path, rows):
    ds = [r.get("date","") for r in rows if r.get("date","")]
    dup = sorted(set([d for d in ds if ds.count(d) > 1]))
    ok_all = True
    if dup:
        err(f"{file_path.name}: fechas duplicadas: {dup[:10]}{' ...' if len(dup)>10 else ''}")
        ok_all = False
    try:
        d_objs = [datetime.strptime(d, "%Y-%m-%d").date() for d in ds]
        if any(d_objs[i] > d_objs[i+1] for i in range(len(d_objs)-1)):
            warn(f"{file_path.name}: fechas fuera de orden cronológico. Recomendado ordenar ascendente.")
    except Exception:
        pass
    return ok_all

def check_coverage(file_path: Path, rows, min_days=7):
    ds = date_series(rows)
    if not ds:
        err(f"{file_path.name}: no hay fechas válidas para evaluar cobertura temporal.")
        return False
    span = (max(ds) - min(ds)).days
    n = len(ds)
    if span < min_days:
        warn(f"{file_path.name}: cobertura temporal corta ({span} días). Mínimo recomendado: {min_days} días.")
    density = n / max(1, span if span > 0 else 1)
    if density < (1/14):
        warn(f"{file_path.name}: baja densidad temporal (≈ {density:.3f} puntos/día). Revisa huecos.")
    return True

def validate_features(path: Path):
    headers, rows = read_csv(path)
    if headers is None: return False, 1
    ok1 = check_headers(path, headers, SCHEMAS["features"])
    ok2 = check_dates(path, rows)
    ok3 = check_numeric(path, rows, ["mean_defo_mm","p95_defo_mm","mean_coh","area_defo_gt10mm_km2"])
    check_ranges(path, rows, {
        "mean_coh": ('range', 0.0, 1.0),
        "mean_defo_mm": ('min', 0.0),
        "p95_defo_mm": ('min', 0.0),
        "area_defo_gt10mm_km2": ('min', 0.0),
    })
    low_coh = sum(1 for r in rows if r.get("mean_coh","")!="" and float(r["mean_coh"]) < 0.3)
    if rows:
        ratio = low_coh / len(rows)
        if ratio > 0.5:
            warn(f"{path.name}: {ratio:.0%} de filas con mean_coh < 0.3, D' podría quedar casi apagado.")
    ok4 = check_duplicates_and_order(path, rows)
    ok5 = check_coverage(path, rows, min_days=14)
    return (ok1 and ok2 and ok3 and ok4 and ok5), 0

def validate_signals(name: str, path: Path):
    headers, rows = read_csv(path)
    if headers is None: return False, 1
    ok1 = check_headers(path, headers, SCHEMAS[name])
    ok2 = check_dates(path, rows)
    num_cols = {
        "animals": ["a_score"],
        "radon": ["r_ppm","r_zscore"],
        "marine": ["m_events_count","m_verified_ratio"],
        "sensors": ["s_activity_z","s_duration_h"],
    }[name]
    ok3 = check_numeric(path, rows, num_cols, allow_nan=False)
    if name == "animals":
        check_ranges(path, rows, {"a_score":('range', 0.0, 1.0)})
    if name == "marine":
        check_ranges(path, rows, {"m_verified_ratio":('range', 0.0, 1.0), "m_events_count":('min', 0.0)})
    if name == "sensors":
        pass
    if name == "radon":
        check_ranges(path, rows, {"r_ppm":('min', 0.0)})
    ok4 = check_duplicates_and_order(path, rows)
    ok5 = check_coverage(path, rows, min_days=14)
    return (ok1 and ok2 and ok3 and ok4 and ok5), 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="Trata warnings como errores")
    args = ap.parse_args()

    critical_errors = 0

    print("== Validando FEATURES por evento ==")
    for fp in FEATURE_FILES:
        okf, code = validate_features(fp)
        if not okf: critical_errors += 1
        else: ok(f"{fp.name}: esquema y valores básicos OK")
        if code != 0: critical_errors += 1

    print("\n== Validando SEÑALES A/R/M/S ==")
    for name, sp in SIGNAL_FILES.items():
        oks, code = validate_signals(name, sp)
        if not oks: critical_errors += 1
        else: ok(f"{sp.name}: esquema y valores básicos OK")
        if code != 0: critical_errors += 1

    if args.strict and WARN_COUNT > 0:
        err(f"Modo estricto: {WARN_COUNT} warning(s) tratados como error.")
        sys.exit(2)

    if critical_errors > 0:
        err(f"Validación falló con {critical_errors} archivo(s) problemático(s).")
        sys.exit(1)

    ok("Validación completada sin errores críticos.")
    sys.exit(0)

if __name__ == "__main__":
    main()
