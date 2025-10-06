from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESKTOP = Path.home() / 'Desktop'
OUT1 = ROOT / 'IASi_demo.pdf'
OUT2 = DESKTOP / 'IASi_demo_on_desktop.pdf'

slides = [
    ("IASi — Índice de Alerta Sísmica Inteligente", "Demostración breve\nEquipo: [Tu nombre] — SpaceApps NASA 2025"),
    ("Problema", "Detectar señales tempranas y patrones asociados a eventos sísmicos usando datos satelitales y sensores.\nDatos heterogéneos y procesos manuales."),
    ("Qué desarrollamos", "Prototipo que ingiere CSVs satelitales, normaliza features y produce índices IASi.\nServidor de subida, adaptadores de ingest, pipeline y exportador JSON."),
    ("Flujo", "Upload CSV → Inbox (validación) → Ingest → Pipeline eval → outputs/indices/<EVENT>/iasi.json\nPersistencia: inbox/processed/invalid"),
    ("Interfaz y métricas", "UI web con mapa, gráficos, toasts y spinner.\nMétricas: AUC‑PR, F1, lead time, falsas alarmas/mes, Brier score."),
    ("Qué muestra la demo", "Sube un CSV de prueba → procesamiento background → ver iasi.json en Outputs y visualizar en la UI.\nIncluye E2E y scripts de despliegue."),
    ("Impacto y next steps", "Automatiza ingestión y evaluación reproducible. Próximos: cola persistente, TLS, despliegue en nube, calibración en terreno.\nRepo: https://github.com/Luciernaga-Sabionda/IASi_Entrega_SpaceApps")
]


def make_pdf(path):
    c = canvas.Canvas(str(path), pagesize=landscape(A4))
    width, height = landscape(A4)
    for title, body in slides:
        c.setFont('Helvetica-Bold', 28)
        c.drawString(2*cm, height - 2.5*cm, title)
        c.setFont('Helvetica', 14)
        text = c.beginText(2*cm, height - 4*cm)
        for line in body.split('\n'):
            text.textLine(line)
        c.drawText(text)
        c.showPage()
    c.save()


if __name__ == '__main__':
    make_pdf(OUT1)
    make_pdf(OUT2)
    print('Created:', OUT1)
    print('Created:', OUT2)
