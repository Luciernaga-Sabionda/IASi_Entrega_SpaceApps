import requests, json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
print('ROOT', ROOT)
# Test upload iasi
p = {
    'meta': {'name': 'TEST_EVENT', 'lat': -12.0, 'lon': -75.0},
    'timeline': [{'date':'2025-10-01','A':0.1,'R':0.2,'D':0.3,'M':0.1,'S':0.05,'IASi':0.155}],
    'metrics': {'7': {'auc_pr':0.5,'f1':0.4,'false_alarm_pm':1.0,'lead_time_days':2}}
}
try:
    r = requests.post('http://localhost:5001/upload_iasi', json=p, timeout=10)
    print('UPLOAD_IASI', r.status_code, r.text)
except Exception as e:
    print('UPLOAD_IASI ERROR', e)

# Test upload AOI
geo = {
  "type": "FeatureCollection",
  "features": [
    {"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-75,-12],[-75,-11],[-74,-11],[-74,-12],[-75,-12]]]}}]
}
try:
    files = {'aoi': ('test_aoi.geojson', json.dumps(geo), 'application/geo+json')}
    data = {'name': 'TEST_EVENT'}
    r2 = requests.post('http://localhost:5001/upload_aoi', files=files, data=data, timeout=10)
    print('UPLOAD_AOI', r2.status_code, r2.text)
except Exception as e:
    print('UPLOAD_AOI ERROR', e)

# Check saved files
idx = ROOT / 'outputs' / 'indices' / 'TEST_EVENT' / 'iasi.json'
aoi = ROOT / 'config' / 'aoi_TEST_EVENT.geojson'
print('EXISTS iasi:', idx.exists(), 'path:', idx)
print('EXISTS aoi:', aoi.exists(), 'path:', aoi)
