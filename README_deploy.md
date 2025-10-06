README de despliegue - Cómo publicar el demo (IASi)
===============================================

Objetivo
--------
Preparar y publicar la interfaz estática (`app/`) en GitHub Pages y dejar instrucciones para publicar el servidor de uploads por separado (recomendado: VPS o servicio con HTTPS). También incluimos un workflow de GitHub Actions que puede desplegar la carpeta `app/` a la rama `gh-pages` tras push a `main`.

Pasos rápidos (resumen)
------------------------
1. Cambia el token API en `config/server.yaml` (no dejar `devtoken`).
2. Apunta `window.SERVER_BASE` en `app/index.html` a la URL pública de tu servidor de uploads (ej: `https://api.mi-proyecto.org`).
3. Sube (push) el repositorio a GitHub (ramo `main`).
4. (Opcional) Habilita GitHub Pages desde la rama `gh-pages` o deja que el workflow despliegue automáticamente.

Detalles
--------

1) Token del servidor

Abre `config/server.yaml` y cambia `api_token: devtoken` por un token fuerte. Reinicia el servidor si está en ejecución.

2) Configurar la URL del servidor en la UI

La página usa `window.SERVER_BASE` para saber la URL del API. Edita `app/index.html` y pon tu URL de producción:

```html
<script>
  window.SERVER_BASE = 'https://api.mi-proyecto.org';
</script>
```

3) Subir a GitHub (comandos de ejemplo)

En PowerShell (desde la carpeta del repo):

```powershell
git add .
git commit -m "Prepara entrega: docs, workflow y zip helper"
git push origin main
```

4) Opcional: usar el workflow GitHub Actions

Se incluye `.github/workflows/deploy_app.yml` que, al hacer push a `main`, publicará automáticamente la carpeta `app/` a la rama `gh-pages`. Si quieres inyectar la URL del servidor automáticamente, configura en los Secrets del repo un secreto llamado `SERVER_BASE` con la URL (por ejemplo `https://api.mi-proyecto.org`).

5) Preparar ZIP de entrega

Ejecuta el script `scripts/prepare_release.ps1` para generar `release.zip` (excluye datos grandes y outputs reproducibles):

```powershell
.\scripts\prepare_release.ps1
# release.zip será creado en el directorio raíz
```

Notas de seguridad
------------------
- No incluyas `data/` ni `outputs/` en el repositorio público si contienen datos sensibles.
- Cambia el `api_token` antes de exponer el servidor.
- Considera usar HTTPS y un reverse proxy para producción.

Soporte
-------
Si quieres que yo: (A) cree el ZIP ahora, (B) haga el commit automático y genere el push, o (C) ajuste el workflow para otra rama, dime cuál y lo automatizo hasta donde tus credenciales lo permitan.

Crear el secret SERVER_BASE en GitHub
1. En GitHub, abre el repo -> Settings -> Secrets and variables -> Actions -> New repository secret.

Licencias
---------
El código fuente del proyecto se publica bajo la licencia MIT (archivo `LICENSE`).
Si distribuyes datos o resultados derivados, por defecto proponemos licencia CC BY 4.0 (ver `LICENSE_DATA.md`) — recuerda incluir la atribución sugerida.

2. Pon Name = SERVER_BASE y Value = https://api.tu-dominio.org (tu URL pública del servidor de uploads).
3. El workflow de despliegue reemplazará el placeholder __SERVER_BASE__ en `app/index.html` con este valor antes de publicar la carpeta `app/`.

