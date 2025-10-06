"""Create IASi_release.zip excluding specified directories.

Usage: python iasi_make_release_zip.py
"""
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'IASi_release.zip'
EXCLUDE = {'data', 'outputs', 'logs', 'venv', '.venv', 'node_modules', '__pycache__', '.git'}

def should_exclude(path: Path):
    for part in path.parts:
        if part in EXCLUDE:
            return True
    return False

with zipfile.ZipFile(OUT, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(ROOT):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if not should_exclude(root_path / d)]
        for f in files:
            fp = root_path / f
            if should_exclude(fp):
                continue
            rel = fp.relative_to(ROOT)
            z.write(fp, rel)

print(f'Created {OUT}')
