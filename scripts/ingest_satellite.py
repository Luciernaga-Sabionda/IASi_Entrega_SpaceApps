#!/usr/bin/env python3
"""
ingest_satellite.py
Simple adapter to convert satellite-derived tabular outputs into the CSV format
the IASi prototype expects for deformation/features (data/features/*.csv).

Usage examples:
  python scripts/ingest_satellite.py --input raw_sat.csv --event Valdivia_1960
  python scripts/ingest_satellite.py -i raw.csv -e Maule_2010 --mode append

The input CSV must contain at least a date column and either 'p95_defo_mm' and 'mean_coh'
or you can map your column names with --p95-col and --coh-col.

Output: writes to data/features/features_<event>.csv with header: date,mean_coh,p95_defo_mm
Dates are normalized to YYYY-MM-DD and invalid rows are skipped.
"""
import argparse
import csv
from pathlib import Path
from datetime import datetime


def parse_args():
    p = argparse.ArgumentParser(description='Ingest satellite table to IASi feature CSV')
    p.add_argument('-i', '--input', required=True, help='Input CSV path (satellite output)')
    p.add_argument('-e', '--event', required=True, help='Event name (used to name output file)')
    p.add_argument('--out-dir', default='data/features', help='Output directory for feature CSVs')
    p.add_argument('--mode', choices=['overwrite','append'], default='overwrite', help='Write mode')
    p.add_argument('--date-col', default='date', help='Column name for date (YYYY-MM-DD)')
    p.add_argument('--coh-col', default='mean_coh', help='Column name for coherence (0..1)')
    p.add_argument('--p95-col', default='p95_defo_mm', help='Column name for 95th percentile deformation (mm)')
    return p.parse_args()


def norm_date(s):
    # Try common date formats; return YYYY-MM-DD or None
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y'):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except Exception:
            continue
    # try ISO parse fallback
    try:
        return datetime.fromisoformat(s).date().isoformat()
    except Exception:
        return None


def ingest(in_path, event, out_dir, mode, date_col, coh_col, p95_col):
    inp = Path(in_path)
    if not inp.exists():
        raise FileNotFoundError(f'Input file not found: {in_path}')
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f'features_{event}.csv'

    rows = []
    with inp.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, r in enumerate(reader):
            raw_date = r.get(date_col) or r.get('date')
            if not raw_date:
                continue
            d = norm_date(raw_date)
            if not d:
                # skip malformed date
                continue
            try:
                coh = r.get(coh_col)
                p95 = r.get(p95_col)
                if coh is None or p95 is None:
                    # skip incomplete rows
                    continue
                coh_v = float(coh)
                p95_v = float(p95)
            except Exception:
                continue
            rows.append({'date': d, 'mean_coh': f'{coh_v:.4f}', 'p95_defo_mm': f'{p95_v:.4f}'})

    if not rows:
        print('No filas válidas encontradas en la entrada; no se escribirá archivo.')
        return

    # If append, read existing and merge by date (keep latest from input)
    if mode == 'append' and out_file.exists():
        existing = {}
        with out_file.open('r', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for rec in r:
                existing[rec['date']] = rec
        for rec in rows:
            existing[rec['date']] = rec
        merged = [existing[k] for k in sorted(existing.keys())]
        with out_file.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['date','mean_coh','p95_defo_mm'])
            writer.writeheader()
            writer.writerows(merged)
        print(f'Archivo actualizado (append) en: {out_file} ({len(merged)} filas)')
    else:
        # overwrite
        rows_sorted = sorted(rows, key=lambda x: x['date'])
        with out_file.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['date','mean_coh','p95_defo_mm'])
            writer.writeheader()
            writer.writerows(rows_sorted)
        print(f'Archivo escrito: {out_file} ({len(rows_sorted)} filas)')


def main():
    args = parse_args()
    ingest(args.input, args.event, args.out_dir, args.mode, args.date_col, args.coh_col, args.p95_col)


if __name__ == '__main__':
    main()
