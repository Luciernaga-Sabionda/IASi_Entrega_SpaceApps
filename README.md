# IASi — Índice de Anomalía Sísmica inteligente

IASi_Entrega_SpaceApps — Entrega SpaceApps NASA 2025

Equipo: Los Abejorros Científicos
Integrantes: Roxana Andrea Salazar Marín, Greimar José Salazar Marín, Jhon Alexandre Meneses Ospina

## Ejecutar en 5 minutos
1. python -m venv .venv && `# Windows: .\.venv\Scripts\Activate.ps1 or use Git Bash: source .venv/bin/activate`
2. pip install -r requirements.txt
3. Completa CSV en `data/` y AOI en `config/` (marcados como PENDIENTE)
4. python scripts/run_eval_batch.py
5. python scripts/export_iasi_json.py
6. cd app && python -m http.server 8080
7. Abre http://localhost:8080 y selecciona evento/ventana

## Estructura de outputs
- `outputs/timelines/<evento>_iasi.csv`
- `outputs/metrics/<evento>_metrics_{7|14|30}d.csv`
- `outputs/indices/<evento>/iasi.json`

## Mensaje de responsabilidad
Probabilidad, no determinismo; revisión humana. Trazabilidad por señal y umbrales auditables.

## Pendientes a completar antes del envío
- Datos reales en `data/features/` y `data/signals/` según evento
- AOI por evento en `config/aoi_*.geojson` si quieres polígonos precisos
- Recalcular métricas reales en lugar de placeholders en `run_eval_batch.py`
- Capturas reales y video 60–90 s
- Licencias y créditos en README y PDF

---

Si necesitas ayuda para resolver conflictos, hacer push o preparar la entrega final (ZIP y release), dime y te guío paso a paso.
