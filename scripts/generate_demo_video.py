from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, concatenate_videoclips
from pathlib import Path
import os
import traceback
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
DESKTOP = Path.home() / 'Desktop'
LOGO = ROOT / 'logo.png'
OUT = DESKTOP / 'IASi_demo_video.mp4'
WATERMARK = 'Generado con asistencia de IA'

slides = [
    ("IASi — Índice de Alerta Sísmica Inteligente", "Demostración breve\nEquipo: Roxana Andrea Salazar Marín; Greimar José Salazar Marín; Jhon Alexandre Meneses Ospina"),
    ("Problema", "Detectar señales tempranas y patrones asociados a eventos sísmicos usando datos satelitales y sensores.\nDatos heterogéneos y procesos manuales."),
    ("Qué desarrollamos", "Prototipo que ingiere CSVs satelitales, normaliza features y produce índices IASi.\nServidor de subida, adaptadores de ingest, pipeline y exportador JSON."),
    ("Flujo", "Upload CSV → Inbox (validación) → Ingest → Pipeline eval → outputs/indices/<EVENT>/iasi.json\nPersistencia: inbox/processed/invalid"),
    ("Interfaz y métricas", "UI web con mapa, gráficos, toasts y spinner.\nMétricas: AUC‑PR, F1, lead time, falsas alarmas/mes, Brier score."),
    ("Qué muestra la demo", "Sube un CSV de prueba → procesamiento background → ver iasi.json en Outputs y visualizar en la UI.\nIncluye E2E y scripts de despliegue."),
    ("Impacto y next steps", "Automatiza ingestión y evaluación reproducible. Próximos: cola persistente, TLS, despliegue en nube, calibración en terreno.\nRepo: https://github.com/Luciernaga-Sabionda/IASi_Entrega_SpaceApps")
]

W, H = 1280, 720
FONT_PATH = None
try:
    # Try to find a default TTF
    FONT_PATH = str(Path('C:/Windows/Fonts/arial.ttf'))
    ImageFont.truetype(FONT_PATH, 24)
except Exception:
    FONT_PATH = None


def make_slide(title, body, logo_path, idx):
    img = Image.new('RGB', (W, H), color=(10, 25, 49))
    draw = ImageDraw.Draw(img)
    title_font = ImageFont.truetype(FONT_PATH, 48) if FONT_PATH else ImageFont.load_default()
    body_font = ImageFont.truetype(FONT_PATH, 24) if FONT_PATH else ImageFont.load_default()
    wm_font = ImageFont.truetype(FONT_PATH, 18) if FONT_PATH else ImageFont.load_default()

    # Title
    draw.text((60, 40), title, font=title_font, fill=(255, 255, 255))
    # Body
    y = 120
    for line in body.split('\n'):
        draw.text((60, y), line, font=body_font, fill=(220, 220, 220))
        y += 36

    # Watermark bottom-left
    wm_w, wm_h = draw.textsize(WATERMARK, font=wm_font)
    draw.rectangle((20, H - 50, 30 + wm_w, H - 20), fill=(0,0,0,128))
    draw.text((25, H - 48), WATERMARK, font=wm_font, fill=(255,255,255))

    # Logo top-right
    if logo_path.exists():
        logo = Image.open(logo_path).convert('RGBA')
        logo.thumbnail((160, 160))
        img.paste(logo, (W - logo.width - 40, 40), logo)

    out_path = ROOT / f'.slide_{idx:02d}.png'
    img.save(out_path)
    return str(out_path)


def main():
    print('Starting demo video generation...')
    # ensure ffmpeg from imageio_ffmpeg is used
    try:
        ffpath = imageio_ffmpeg.get_ffmpeg_exe()
        os.environ['IMAGEIO_FFMPEG_EXE'] = ffpath
        print('Using ffmpeg:', ffpath)
    except Exception as e:
        print('Could not find imageio-ffmpeg exe:', e)

    slides_img = []
    for i, (t, b) in enumerate(slides):
        p = make_slide(t, b, LOGO, i)
        slides_img.append(p)
    print('Slides created:')
    for p in slides_img:
        print('  ', p)

    clips = []
    for img_path in slides_img:
        clip = ImageClip(img_path).set_duration(4)
        clip = clip.set_fps(24)
        clips.append(clip)

    final = concatenate_videoclips(clips, method='compose')
    try:
        print('Writing video to', OUT)
        final.write_videofile(str(OUT), codec='libx264', fps=24, audio=False)
        print('Created video at', OUT)
    except Exception as e:
        print('Error while writing video:')
        traceback.print_exc()

if __name__ == '__main__':
    main()
