from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yaml
from pathlib import Path
import shutil
import time
from pathlib import Path
import json
import threading
import tempfile
import os
from importlib import import_module
import logging
import sys
import csv
import json as _json

ROOT = Path(__file__).resolve().parents[1]
OUT_INDICES = ROOT / 'outputs' / 'indices'
CFG = ROOT / 'config'
OUT_INDICES.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
# Enable CORS for all origins and allow Authorization header so the static UI
# hosted on a different origin can call the API. supports_credentials=True
# allows cookies/credentials if needed by future changes.
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"]) 

# Load server config (api token)
ROOT = Path(__file__).resolve().parents[1]
CFG_DIR = ROOT / 'config'
CFG_DIR.mkdir(parents=True, exist_ok=True)
SERVER_CFG = CFG_DIR / 'server.yaml'
DEFAULT_TOKEN = 'devtoken'
if not SERVER_CFG.exists():
    with open(SERVER_CFG, 'w', encoding='utf-8') as f:
        yaml.dump({'api_token': DEFAULT_TOKEN}, f)
SERVER = yaml.safe_load(SERVER_CFG.read_text()) or {}
API_TOKEN = SERVER.get('api_token', DEFAULT_TOKEN)

# Setup simple file + console logging
LOG_PATH = ROOT / 'logs'
LOG_PATH.mkdir(parents=True, exist_ok=True)
log_file = LOG_PATH / 'upload_server.log'
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh = logging.FileHandler(str(log_file), encoding='utf-8')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger = logging.getLogger('upload_server')
logger.setLevel(logging.INFO)
logger.addHandler(fh)
logger.addHandler(ch)

# Also set Flask's app.logger to use the same handlers
app.logger.handlers = logger.handlers
app.logger.setLevel(logger.level)

def check_token(req):
    auth = req.headers.get('Authorization') or req.headers.get('authorization')
    if not auth:
        return False
    if auth.startswith('Bearer '):
        return auth.split(' ',1)[1].strip() == API_TOKEN
    return auth.strip() == API_TOKEN

def validate_iasi_json(data):
    # Basic schema checks
    if not isinstance(data, dict):
        return False, 'Payload debe ser un objeto JSON'
    meta = data.get('meta')
    if not meta or not isinstance(meta, dict):
        return False, 'Falta meta (objeto)'
    name = meta.get('name')
    if not name or not isinstance(name, str):
        return False, 'meta.name requerido y debe ser string'
    lat = meta.get('lat')
    lon = meta.get('lon')
    if lat is not None and not isinstance(lat, (int,float)):
        return False, 'meta.lat debe ser numérico'
    if lon is not None and not isinstance(lon, (int,float)):
        return False, 'meta.lon debe ser numérico'
    timeline = data.get('timeline')
    if not isinstance(timeline, list):
        return False, 'timeline debe ser una lista'
    for i, r in enumerate(timeline[:20]):
        if not isinstance(r, dict) or 'date' not in r or 'IASi' not in r:
            return False, f'timeline[{i}] inválido: requiere date e IASi'
    metrics = data.get('metrics')
    if not isinstance(metrics, dict):
        return False, 'metrics debe ser un objeto'
    return True, None

@app.route('/upload_iasi', methods=['POST'])
def upload_iasi():
    if not check_token(request):
        return jsonify({'ok': False, 'error': 'Unauthorized - invalid token'}), 401
    data = request.get_json()
    valid, reason = validate_iasi_json(data)
    if not valid:
        return jsonify({'ok': False, 'error': f'JSON inválido: {reason}'}), 400
    name = data['meta']['name']
    outdir = OUT_INDICES / name
    outdir.mkdir(parents=True, exist_ok=True)
    target = outdir / 'iasi.json'
    # backup previous
    if target.exists():
        bak = outdir / f'iasi.json.bak.{int(time.time())}'
        shutil.copy2(target, bak)
    with open(target, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({'ok': True, 'path': str(target)})

@app.route('/upload_aoi', methods=['POST'])
def upload_aoi():
    if not check_token(request):
        return jsonify({'ok': False, 'error': 'Unauthorized - invalid token'}), 401
    if 'aoi' not in request.files:
        return jsonify({'ok': False, 'error': 'Se requiere archivo aoi'}), 400
    f = request.files['aoi']
    name = request.form.get('name', 'uploaded')
    outp = CFG_DIR / f'aoi_{name}.geojson'
    # backup
    if outp.exists():
        outp.rename(CFG_DIR / f'aoi_{name}.geojson.bak.{int(time.time())}')
    f.save(outp)
    return jsonify({'ok': True, 'path': str(outp)})


@app.route('/upload_sat', methods=['POST'])
def upload_sat():
    """Endpoint to receive satellite table (CSV or JSON) and ingest into data/features.
    Accepts multipart file named 'sat' or JSON payload with keys: event, rows[] or csv text.
    Optional query param: run_pipeline=true to trigger run_eval_batch.py (background).
    """
    if not check_token(request):
        return jsonify({'ok': False, 'error': 'Unauthorized - invalid token'}), 401

    event = request.form.get('event') or request.args.get('event') or (request.json.get('event') if request.is_json else None)
    if not event:
        return jsonify({'ok': False, 'error': 'event name required (form/event or json.event)'}), 400

    # Ensure inbox exists
    inbox = ROOT / 'data' / 'inbox_sat'
    inbox.mkdir(parents=True, exist_ok=True)

    try:
        saved = None
        if 'sat' in request.files:
            f = request.files['sat']
            fname = f"{event}_{int(time.time())}.csv"
            saved = inbox / fname
            f.save(str(saved))
            logger.info('Saved uploaded sat file %s for event %s', saved, event)
        elif request.is_json:
            j = request.get_json()
            rows = j.get('rows')
            if rows and isinstance(rows, list) and len(rows) > 0:
                keys = list(rows[0].keys())
                fname = f"{event}_{int(time.time())}.csv"
                saved = inbox / fname
                with saved.open('w', encoding='utf-8', newline='') as fh:
                    w = csv.writer(fh)
                    w.writerow(keys)
                    for r in rows:
                        w.writerow([r.get(k, '') for k in keys])
                logger.info('Saved JSON rows to %s', saved)
            elif j.get('csv'):
                fname = f"{event}_{int(time.time())}.csv"
                saved = inbox / fname
                saved.write_text(j['csv'], encoding='utf-8')
                logger.info('Saved csv text payload to %s', saved)
            else:
                return jsonify({'ok': False, 'error': 'JSON payload must include rows[] or csv text'}), 400
        else:
            return jsonify({'ok': False, 'error': 'No sat file or JSON payload found'}), 400

        # respond quickly and process in background
        run_pipeline = (request.args.get('run_pipeline','false').lower() == 'true') or (request.form.get('run_pipeline','false').lower()=='true')

        # column mapping (optional) - allow clients to specify which CSV columns map to date, mean coherence and p95 defo
        date_col = request.form.get('date_col') or request.args.get('date_col') or 'date'
        coh_col = request.form.get('coh_col') or request.args.get('coh_col') or 'mean_coh'
        p95_col = request.form.get('p95_col') or request.args.get('p95_col') or 'p95_defo_mm'

        # prepare inbox subdirs for invalid/processed
        invalid_dir = inbox / 'invalid'
        processed_dir = inbox / 'processed'
        invalid_dir.mkdir(parents=True, exist_ok=True)
        processed_dir.mkdir(parents=True, exist_ok=True)

        # quick validation of CSV headers (if saved file is present)
        if saved and saved.exists():
            try:
                with saved.open('r', encoding='utf-8') as fh:
                    first = fh.readline()
                hdr = first.strip()
                header_cols = [c.strip() for c in hdr.split(',') if c.strip()]
                missing = [c for c in (date_col, coh_col, p95_col) if c not in header_cols]
                if missing:
                    # move to invalid and return error
                    bad = invalid_dir / saved.name
                    saved.rename(bad)
                    logger.warning('Uploaded sat file %s missing cols: %s -> moved to %s', saved.name, missing, bad)
                    # update status
                    try:
                        status_file = inbox / 'status.json'
                        st = {'processed':0,'invalid':0,'queued':0,'last':None}
                        if status_file.exists():
                            st = _json.loads(status_file.read_text(encoding='utf-8'))
                        st['invalid'] = st.get('invalid',0) + 1
                        st['last'] = str(bad)
                        status_file.write_text(_json.dumps(st), encoding='utf-8')
                    except Exception:
                        logger.exception('Could not update status.json')
                    return jsonify({'ok': False, 'error': f'Missing required columns: {missing}', 'moved_to': str(bad)}), 400
            except Exception as e:
                logger.exception('Error reading uploaded CSV header')
                bad = invalid_dir / saved.name
                try:
                    if saved.exists():
                        saved.rename(bad)
                except Exception:
                    logger.exception('Could not move bad file %s', saved)
                try:
                    status_file = inbox / 'status.json'
                    st = {'processed':0,'invalid':0,'queued':0,'last':None}
                    if status_file.exists():
                        st = _json.loads(status_file.read_text(encoding='utf-8'))
                    st['invalid'] = st.get('invalid',0) + 1
                    st['last'] = str(bad)
                    status_file.write_text(_json.dumps(st), encoding='utf-8')
                except Exception:
                    logger.exception('Could not update status.json')
                return jsonify({'ok': False, 'error': 'Error reading CSV header', 'detail': str(e)}), 400

        def _bg_process(path, ev, do_pipeline, date_col_local=date_col, coh_col_local=coh_col, p95_col_local=p95_col):
            try:
                pkg_root = Path(__file__).resolve().parents[1]
                # call ingest script to append into data/features
                cmd_ingest = [sys.executable, str(pkg_root / 'scripts' / 'ingest_satellite.py'), '-i', str(path), '-e', ev, '--mode', 'append']
                # pass column mapping to ingest script if it supports it
                cmd_ingest.extend(['--date-col', date_col_local, '--coh-col', coh_col_local, '--p95-col', p95_col_local])
                logger.info('Running ingest command: %s', ' '.join(cmd_ingest))
                os.system(' '.join(f'"{c}"' if ' ' in str(c) else str(c) for c in cmd_ingest))
                if do_pipeline:
                    cmd_run = [sys.executable, str(pkg_root / 'scripts' / 'run_eval_batch.py')]
                    cmd_export = [sys.executable, str(pkg_root / 'scripts' / 'export_iasi_json.py')]
                    logger.info('Running pipeline commands')
                    os.system(' '.join(f'"{c}"' if ' ' in str(c) else str(c) for c in cmd_run))
                    os.system(' '.join(f'"{c}"' if ' ' in str(c) else str(c) for c in cmd_export))
                # move processed file to processed dir
                try:
                    dest = processed_dir / Path(path).name
                    Path(path).rename(dest)
                    logger.info('Moved processed file to %s', dest)
                    # update status
                    try:
                        status_file = inbox / 'status.json'
                        st = {'processed':0,'invalid':0,'queued':0,'last':None}
                        if status_file.exists():
                            st = _json.loads(status_file.read_text(encoding='utf-8'))
                        st['processed'] = st.get('processed',0) + 1
                        st['last'] = str(dest)
                        status_file.write_text(_json.dumps(st), encoding='utf-8')
                    except Exception:
                        logger.exception('Could not update status.json after processing')
                except Exception:
                    logger.exception('Could not move processed file %s', path)
                logger.info('Background processing finished for %s', path)
            except Exception as e:
                logger.exception('Error in background processing: %s', e)

        # update queued counter
        try:
            status_file = inbox / 'status.json'
            st = {'processed':0,'invalid':0,'queued':0,'last':None}
            if status_file.exists():
                st = _json.loads(status_file.read_text(encoding='utf-8'))
            st['queued'] = st.get('queued',0) + 1
            st['last'] = str(saved)
            status_file.write_text(_json.dumps(st), encoding='utf-8')
        except Exception:
            logger.exception('Could not update status.json queued counter')

        t = threading.Thread(target=_bg_process, args=(saved, event, run_pipeline), daemon=True)
        t.start()

        return jsonify({'ok': True, 'queued': True, 'path': str(saved)}), 200
    except Exception as e:
        logger.exception('upload_sat error')
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    try:
        return jsonify({'ok': True, 'status': 'running', 'pid': os.getpid()}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    if not check_token(request):
        return jsonify({'ok': False, 'error': 'Unauthorized - invalid token'}), 401
    inbox = ROOT / 'data' / 'inbox_sat'
    status_file = inbox / 'status.json'
    if not status_file.exists():
        return jsonify({'ok': True, 'status': {}, 'note': 'no status yet'}), 200
    try:
        data = _json.loads(status_file.read_text(encoding='utf-8'))
        return jsonify({'ok': True, 'status': data}), 200
    except Exception as e:
        logger.exception('Error reading status.json')
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/list_indices', methods=['GET'])
def list_indices():
    items = [p.name for p in OUT_INDICES.iterdir() if p.is_dir()]
    return jsonify({'ok': True, 'indices': items})


@app.route('/get_iasi/<name>', methods=['GET'])
def get_iasi(name):
    target = OUT_INDICES / name / 'iasi.json'
    if not target.exists():
        return jsonify({'ok': False, 'error': 'Not found'}), 404
    try:
        data = json.loads(target.read_text(encoding='utf-8'))
        return jsonify({'ok': True, 'data': data})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

if __name__ == '__main__':
    logger.info('Starting upload_server on 0.0.0.0:5001 (API_TOKEN=%s)', API_TOKEN)
    app.run(host='0.0.0.0', port=5001)
