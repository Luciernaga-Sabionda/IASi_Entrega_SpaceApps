"""Simple E2E test: start upload_server, POST a CSV and verify processing."""
import subprocess, time, requests, os, sys
from pathlib import Path

# Variables globales
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
INCOMING = (ROOT / 'incoming' / 'sat_test.csv').resolve()
EVENT = 'TEST_EVENT'
URL = 'http://127.0.0.1:5001'
TOKEN = 'devtoken'

def wait_health(timeout=15):
    t0 = time.time()
    while time.time()-t0 < timeout:
        try:
            r = requests.get(URL + '/health', timeout=2)
            if r.status_code==200:
                print('server healthy')
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def main():
    # Use venv python for subprocess
    venv_python = str(ROOT / '.venv' / 'Scripts' / 'python.exe')
    if not Path(venv_python).exists():
        venv_python = sys.executable
    print('Launching server with:', venv_python)
    p = subprocess.Popen([venv_python, str(SCRIPTS/'upload_server.py')], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        if not wait_health(20):
            print('server did not start')
            p.kill()
            sys.exit(2)
        print('Server healthy, sending CSV...')
        files = {'sat': open(INCOMING,'rb')}
        headers = {'Authorization': f'Bearer {TOKEN}'}
        params = {'event': EVENT}
        r = requests.post(URL + '/upload_sat', files=files, params=params, headers=headers, timeout=10)
        print('POST status', r.status_code, r.text)
        print('Esperando archivo procesado en data/inbox_sat/processed...')
        # wait for processed file
        proc_dir = ROOT / 'data' / 'inbox_sat' / 'processed'
        target = None
        t0 = time.time()
        while time.time()-t0 < 30:
            if proc_dir.exists():
                lst = list(proc_dir.glob(f"{EVENT}_*.csv"))
                if lst:
                    target = lst[0]
                    break
            time.sleep(0.5)
        if not target:
            print('processed file not found')
            sys.exit(3)
        print('Archivo procesado:', target)
        feat = ROOT / 'data' / 'features' / f'features_{EVENT}.csv'
        if feat.exists():
            print('Archivo features generado:', feat)
            print(feat.read_text()[:400])
        else:
            print('Archivo features NO encontrado')
            sys.exit(4)
        print('Consultando /status en el servidor...')
        try:
            s = requests.get(URL+'/status', headers=headers)
            print('Server status:', s.status_code, s.text)
        except Exception as e:
            print('Error consultando /status:', e)
        print('Verificando outputs/indices/TEST_EVENT/iasi.json...')
        iasi = ROOT / 'outputs' / 'indices' / EVENT / 'iasi.json'
        if iasi.exists():
            print('iasi.json generado:', iasi)
            print(iasi.read_text()[:400])
        else:
            print('iasi.json NO encontrado')
    finally:
        # Try to query status before killing server (may fail if server already stopped)
        try:
            print('Consultando /status en el servidor...')
            s = requests.get(URL + '/status', headers={'Authorization': f'Bearer {TOKEN}'}, timeout=2)
            print('Server status:', s.status_code, s.text)
        except Exception as e:
            print('Error consultando /status (posible que el servidor ya se haya detenido):', e)
        # Kill the server process
        try:
            p.kill()
        except Exception:
            pass

if __name__ == '__main__':
    main()
