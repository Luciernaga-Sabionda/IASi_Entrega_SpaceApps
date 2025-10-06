#!/usr/bin/env python3
# Equipo: Los Abejorros Científicos
# Evalúa 4 eventos andinos y exporta timelines y métricas
import csv, math, os
from pathlib import Path
import json
from datetime import datetime, timedelta
from collections import defaultdict
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config"
DATA = ROOT / "data"
OUT_TIMELINES = ROOT / "outputs" / "timelines"
OUT_METRICS = ROOT / "outputs" / "metrics"
OUT_TIMELINES.mkdir(parents=True, exist_ok=True)
OUT_METRICS.mkdir(parents=True, exist_ok=True)

# Try to read weights and thresholds from config YAMLs; fall back to defaults
WEIGHTS = {"alpha":0.25,"beta":0.20,"gamma":0.25,"delta":0.15,"epsilon":0.15}
TH = {"observation":0.50,"caution_min":0.50,"caution_max":0.69,"alert":0.70}
try:
	wpath = CFG / "weights.yaml"
	if wpath.exists():
		with open(wpath, 'r', encoding='utf-8') as f:
			w = yaml.safe_load(f)
			# normalize keys
			WEIGHTS.update({k: float(v) for k, v in (w.items() if isinstance(w, dict) else [])})
	tpath = CFG / "thresholds.yaml"
	if tpath.exists():
		with open(tpath, 'r', encoding='utf-8') as f:
			t = yaml.safe_load(f)
			if isinstance(t, dict):
				TH.update({k: float(v) for k, v in t.items() if k in TH})
except Exception:
	# ignore and keep defaults
	pass

EVENTS = [
	{"name":"Valdivia_1960","lat":-39.8,"lon":-73.2,"aoi":"config/aoi_valdivia.geojson","feat":"data/features/features_valdivia1960.csv"},
	{"name":"Maule_2010","lat":-35.0,"lon":-72.5,"aoi":"config/aoi_maule.geojson","feat":"data/features/features_maule2010.csv"},
	{"name":"Illapel_2015","lat":-31.6,"lon":-71.2,"aoi":"config/aoi_illapel.geojson","feat":"data/features/features_illapel2015.csv"},
	{"name":"EC_CO_1906","lat":1.0,"lon":-80.0,"aoi":"config/aoi_ec_co_1906.geojson","feat":"data/features/features_ec_co_1906.csv"},
]

def sigmoid(x): return 1.0/(1.0+math.exp(-x))
def clip(x, lo=0.0, hi=1.0): return max(lo, min(hi, x))

def read_csv(path):
	p=Path(path); 
	if not p.exists(): return []
	with p.open("r", encoding="utf-8") as f:
		rows=list(csv.DictReader(f))
	return rows

def join_by_date(dicts):
	"""Une listas de dict por 'date' con 'última observación válida' simple."""
	dates=set()
	for d in dicts:
		for r in d: dates.add(r["date"])
	dates=sorted(dates)
	lastA=lastR=lastM=lastS=None
	lastD=None
	out=[]
	A, R, M, S = dicts[0], dicts[1], dicts[2], dicts[3]
	D = dicts[4]
	A_by={r["date"]:r for r in A}
	R_by={r["date"]:r for r in R}
	M_by={r["date"]:r for r in M}
	S_by={r["date"]:r for r in S}
	D_by={r["date"]:r for r in D}
	for dt in dates:
		if dt in A_by: lastA=A_by[dt]
		if dt in R_by: lastR=R_by[dt]
		if dt in M_by: lastM=M_by[dt]
		if dt in S_by: lastS=S_by[dt]
		if dt in D_by: lastD=D_by[dt]
		out.append({"date":dt,"A":lastA,"R":lastR,"M":lastM,"S":lastS,"D":lastD})
	return out

def build_signal_tables():
	A = read_csv(DATA/"signals"/"animals.csv")
	R = read_csv(DATA/"signals"/"radon.csv")
	M = read_csv(DATA/"signals"/"marine.csv")
	S = read_csv(DATA/"signals"/"sensors.csv")
	return A,R,M,S

def compute_row(sig):
	# Transformaciones
	A_ = clip(float(sig["A"]["a_score"])) if sig["A"] else 0.0
	R_ = sigmoid(float(sig["R"]["r_zscore"])) if sig["R"] else 0.0
	if sig["D"]:
		coh = float(sig["D"]["mean_coh"])
		d95 = float(sig["D"]["p95_defo_mm"])
		D_ = clip(d95/20.0) if coh >= 0.3 else 0.0
	else:
		D_ = 0.0
	M_ = clip(float(sig["M"]["m_verified_ratio"])) if sig["M"] else 0.0
	S_ = sigmoid(float(sig["S"]["s_activity_z"])) if sig["S"] else 0.0
	IASi = WEIGHTS["alpha"]*A_ + WEIGHTS["beta"]*R_ + WEIGHTS["gamma"]*D_ + WEIGHTS["delta"]*M_ + WEIGHTS["epsilon"]*S_
	state = "Observación" if IASi < TH["observation"] else ("Precaución" if IASi <= TH["caution_max"] else "Alerta")
	return A_,R_,D_,M_,S_,IASi,state

def export_timeline(event, rows):
	out = OUT_TIMELINES / f"{event['name']}_iasi.csv"
	with out.open("w", newline="", encoding="utf-8") as f:
		w = csv.writer(f); 
		w.writerow(["date","A","R","D","M","S","IASi","estado"])
		for r in rows:
			A_,R_,D_,M_,S_,IASi,state = compute_row(r)
			w.writerow([r["date"], f"{A_:.4f}", f"{R_:.4f}", f"{D_:.4f}", f"{M_:.4f}", f"{S_:.4f}", f"{IASi:.4f}", state])

def fake_metrics():
	# Placeholder simple: pon valores realistas cuando tengas etiquetas
	return {
		"7":{"auc_pr":0.58,"f1":0.50,"false_alarm_pm":1.5,"lead_time_days":3,"brier":0.23,"best_threshold":0.72},
		"14":{"auc_pr":0.62,"f1":0.52,"false_alarm_pm":1.4,"lead_time_days":3,"brier":0.21,"best_threshold":0.70},
		"30":{"auc_pr":0.55,"f1":0.49,"false_alarm_pm":1.8,"lead_time_days":2,"brier":0.26,"best_threshold":0.73}
	}

# === Métricas y etiquetado ===
def parse_date(s):
	return datetime.strptime(s, "%Y-%m-%d").date()

def load_eq_catalog(path_csv, mw_min=6.5):
	"""
	CSV esperado: date, mw [, lat, lon, depth]
	date en YYYY-MM-DD
	"""
	rows = read_csv(path_csv)
	out = []
	for r in rows:
		try:
			d = parse_date(r["date"])
			mw = float(r.get("mw", "0"))
			if mw >= mw_min:
				out.append({"date": d, "mw": mw})
		except Exception:
			continue
	return sorted(out, key=lambda x: x["date"])

def labels_from_catalog(timeline_dates, eq_catalog, window_days):
	"""
	timeline_dates: lista de date() en orden ascendente
	eq_catalog: lista de {"date": date, "mw": float}
	Devuelve y_true por día: 1 si hay sismo ≥ Mw_min en próximos N días, 0 si no.
	"""
	eq_dates = [e["date"] for e in eq_catalog]
	y_true = [0]*len(timeline_dates)
	for i, d in enumerate(timeline_dates):
		end = d + timedelta(days=window_days)
		has_eq = any((d < ed <= end) for ed in eq_dates)
		y_true[i] = 1 if has_eq else 0
	return y_true

def auc_pr(y_true, y_score):
	pairs = sorted(zip(y_score, y_true), key=lambda p: p[0], reverse=True)
	tp = 0
	fp = 0
	fn = sum(y_true)
	prev_recall = 0.0
	prev_prec = 1.0
	area = 0.0

	for score, y in pairs:
		if y == 1:
			tp += 1
			fn -= 1
		else:
			fp += 1
		recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
		precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
		area += (recall - prev_recall) * ((precision + prev_prec) / 2.0)
		prev_recall, prev_prec = recall, precision
	return area

def f1_at_threshold(y_true, y_score, thr):
	tp = fp = fn = 0
	for t, s in zip(y_true, y_score):
		yhat = 1 if s >= thr else 0
		if yhat == 1 and t == 1: tp += 1
		if yhat == 1 and t == 0: fp += 1
		if yhat == 0 and t == 1: fn += 1
	prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
	rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
	if prec + rec == 0: return 0.0
	return 2*prec*rec/(prec+rec)

def best_threshold_f1(y_true, y_score, grid=None):
	if grid is None:
		grid = [round(x/100, 2) for x in range(30, 86)]
	best_thr, best_f1 = 0.5, -1
	for thr in grid:
		f1 = f1_at_threshold(y_true, y_score, thr)
		if f1 > best_f1:
			best_f1, best_thr = f1, thr
	return best_thr, best_f1

def false_alarms_per_month(y_true, y_score, thr, dates):
	if not dates: return 0.0
	yhat = [1 if s >= thr else 0 for s in y_score]
	alarms_idx = [i for i in range(1, len(yhat)) if yhat[i]==1 and yhat[i-1]==0]
	fa = 0
	for i in alarms_idx:
		future_positive = any(y_true[j]==1 for j in range(i, len(y_true)))
		if not future_positive:
			fa += 1
	months = max(1, (dates[-1] - dates[0]).days / 30.4375)
	return fa / months

def lead_time_days(y_true, y_score, thr, dates):
	yhat = [1 if s >= thr else 0 for s in y_score]
	event_days = [i for i, t in enumerate(y_true) if t==1]
	if not event_days: return 0.0
	last_on = -1
	last_on_idx = []
	for i, h in enumerate(yhat):
		if h==1: last_on = i
		last_on_idx.append(last_on)
	deltas = []
	for i in event_days:
		j = last_on_idx[i]
		if j == -1:
			continue
		dt = (dates[i] - dates[j]).days
		deltas.append(dt)
	return sum(deltas)/len(deltas) if deltas else 0.0

def brier_score(y_true, y_score):
	n = len(y_true)
	if n == 0: return 0.0
	return sum((float(t) - float(s))**2 for t, s in zip(y_true, y_score)) / n

def evaluate_timeline_metrics(timeline_rows, eq_catalog_csv, window_days, thr_grid=None):
	dates = [parse_date(r["date"]) for r in timeline_rows]
	scores = [float(r["IASi"]) for r in timeline_rows]
	cat = load_eq_catalog(eq_catalog_csv, mw_min=6.5)
	y_true = labels_from_catalog(dates, cat, window_days)
	pr = auc_pr(y_true, scores)
	if thr_grid is None:
		thr_grid = [round(x/100, 2) for x in range(65, 81)]
	best_thr, best_f1 = best_threshold_f1(y_true, scores, thr_grid)
	fa_pm = false_alarms_per_month(y_true, scores, best_thr, dates)
	lt_days = lead_time_days(y_true, scores, best_thr, dates)
	brier = brier_score(y_true, scores)
	return {
		"auc_pr": round(pr, 4),
		"f1": round(best_f1, 4),
		"false_alarm_pm": round(fa_pm, 3),
		"lead_time_days": round(lt_days, 2),
		"brier": round(brier, 4),
		"best_threshold": round(best_thr, 2)
	}

# Directorio de catálogos sísmicos por evento (puedes crear data/catalogs/)
CAT_DIR = DATA / "catalogs"

def metrics_for_event(ev_name, timeline_csv_path):
	tl = read_csv(timeline_csv_path)
	tl_rows = [{"date": r["date"], "IASi": r["IASi"]} for r in tl if "date" in r and "IASi" in r]
	eq_csv = CAT_DIR / f"{ev_name}.csv"
	out = {}
	for win in (7, 14, 30):
		out[str(win)] = evaluate_timeline_metrics(tl_rows, str(eq_csv), win)
	return out

def export_metrics(event, metrics):
	for win, m in metrics.items():
		out = OUT_METRICS / f"{event['name']}_metrics_{win}d.csv"
		with out.open("w", newline="", encoding="utf-8") as f:
			w = csv.writer(f)
			w.writerow(["AUC_PR","F1","false_alarms_per_month","lead_time_days","brier","best_threshold"])
			w.writerow([m["auc_pr"],m["f1"],m["false_alarm_pm"],m["lead_time_days"],m["brier"],m["best_threshold"]])


def main():
	A,R,M,S = build_signal_tables()
	for ev in EVENTS:
		D = read_csv(ev["feat"])
		union = join_by_date([A,R,M,S,D])
		export_timeline(ev, union)
	# Calcula métricas reales usando catálogo en data/catalogs/<evento>.csv
		tl_path = OUT_TIMELINES / f"{ev['name']}_iasi.csv"
		m = metrics_for_event(ev["name"], str(tl_path))
		export_metrics(ev, m)
	print("OK: timelines y métricas exportadas en outputs/")

if __name__=="__main__":
	main()
