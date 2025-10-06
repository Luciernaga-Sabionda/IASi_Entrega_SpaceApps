IASi - Guía rápida de demo

Objetivo
- Servir la interfaz `app/index.html` localmente y mostrar los índices `outputs/indices/<evento>/iasi.json` generados por los scripts.

Preparación (ya realizada)
- Se creó un entorno virtual `.venv` en la raíz usando Python 3.13.
- Se instalaron las dependencias desde `requirements.txt`.
- Se ejecutó `scripts/validate_inputs.py` y se corrigieron comentarios inválidos en `data/signals/*`.
- Se añadieron filas sintéticas a `data/features/*` para mejorar la densidad temporal en la demo.
- Se ejecutaron `scripts/run_eval_batch.py` y `scripts/export_iasi_json.py` para generar timelines, métricas y `outputs/indices/*/iasi.json`.

Comandos útiles para la demo (PowerShell)
# Si la política de ejecución bloquea la activación del venv, ejecuta primero:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activar el entorno virtual (opcional, puedes usar .venv\Scripts\python directamente)
.\.venv\Scripts\Activate.ps1

# Servir la carpeta `app/` en http://localhost:8000
python -m http.server 8000 --directory .\app

# Abrir en el navegador:
# http://localhost:8000/index.html

Archivos importantes
- outputs/indices/<evento>/iasi.json  -> JSON consumido por la UI.
- outputs/timelines/<evento>_iasi.csv -> timelines usados para calcular métricas.
- outputs/metrics/*_metrics_{7|14|30}d.csv -> métricas calculadas.
- scripts/validate_inputs.py -> validador de CSVs.
- scripts/run_eval_batch.py -> pipeline que genera timelines y métricas.
- scripts/export_iasi_json.py -> consolida `iasi.json`.

Nuevas utilidades para integrar datos satelitales
- `scripts/ingest_satellite.py` -> adaptador: convierte CSV/JSON satelitales en `data/features/features_<EVENT>.csv`.
- `scripts/watcher_ingest.py` -> watcher simple que vigila `data/inbox_sat` y procesa archivos nuevos (usa `ingest_satellite.py`).
- `scripts/stream_http_producer.py` -> ejemplo que envía un CSV al endpoint HTTP `/upload_sat`.
- Endpoint `/upload_sat` en el servidor Flask (`scripts/upload_server.py`) acepta multipart/form-data (campo 'sat') o JSON con `rows[]` o `csv` fields. Puedes pasar `run_pipeline=true` para que ejecute `run_eval_batch.py` en background.

Ejemplo de uso (PowerShell):
```powershell
# Arrancar servidor de uploads (en un terminal)
python .\scripts\upload_server.py

# En otro terminal, enviar CSV por HTTP al servidor (usa token devtoken por defecto)
python .\scripts\stream_http_producer.py --file .\incoming\sat_test.csv --event TEST_EVENT --token devtoken

# Para pruebas E2E automatizadas (lanza servidor temporalmente y verifica procesamiento):
python .\scripts\test_e2e.py

# Alternativa: usar el watcher para procesar manualmente archivos en data/inbox_sat
python .\scripts\watcher_ingest.py --run-pipeline
```

Notas y recomendaciones
- Los datos sintéticos se añadieron solo para la demo; reemplaza `data/features/*` y `data/signals/*` con tus datos reales antes de la exposición si los tienes.
- Si quieres persistir `iasi.json` desde la UI (upload), puedo añadir un endpoint Flask simple para guardar archivos en `outputs/`.
- Si la instalación en tu máquina tarda o falla en paquetes binarios (geopandas/pyogrio), recomiendo usar Conda para instalar geopandas rápidamente.

Contacto
- Si quieres que ajuste thresholds, pesos o genere gráficas PNG para tu presentación, dime qué evento y ventana quieres y lo preparo.
