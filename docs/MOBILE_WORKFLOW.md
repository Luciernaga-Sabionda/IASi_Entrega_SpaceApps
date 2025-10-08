## Flujo rápido para trabajar desde el móvil

Este documento explica cómo revisar, editar y verificar el repositorio desde un teléfono móvil o tablet.

1) Ver repositorio y commits
- Abre la app de GitHub o el navegador en: https://github.com/Luciernaga-Sabionda/IASi_Entrega_SpaceApps
- Usa la vista `Code` para navegar archivos y la pestaña `Commits` para ver historial.

2) Ediciones rápidas desde el navegador
- Para ediciones pequeñas (README, docs) toca `.` en la vista del repositorio para abrir la versión web de VS Code (github.dev) o abre https://github.dev/Luciernaga-Sabionda/IASi_Entrega_SpaceApps
- Edita archivos y guarda. GitHub creará un fork/branch y te dará la opción de abrir un Pull Request.

3) Editar con Codespaces (si disponible)
- Si tu cuenta tiene Codespaces, abre `Code -> Codespaces -> New codespace` para disponer de un entorno completo con terminal y editor.

4) Ver/descargar artefactos (ZIP, PDF, MP4)
- En la pestaña `Releases` o `Actions` puedes descargar artefactos generados por workflows.
- También puedes navegar la rama `main` y descargar archivos individuales con el botón `Download`.

5) Comandos para usar en una terminal móvil o remota (SSH/Termux)
```powershell
# actualizar rama local
git fetch origin; git pull --rebase origin main

# ver últimos commits
git log --oneline -n 10

# crear commit y push (si editas desde una terminal remota)
git add -A; git commit -m "docs: cambio rápido desde móvil"; git push origin main
```

6) Seguridad y buenas prácticas
- No subas tokens, contraseñas ni archivos grandes desde el móvil.
- Para cambios importantes crea un branch y un Pull Request para revisión.

7) Soporte y seguimiento
- Si encuentras conflictos al empujar, copia el mensaje de error y pégalo en el chat para obtener ayuda rápida.

--
Documento generado automáticamente para facilitar trabajo móvil.
# Flujo de trabajo desde el móvil

Este documento explica formas rápidas y seguras de revisar, editar y seguir el proyecto `IASi_Entrega_SpaceApps` desde un teléfono móvil.

Opciones recomendadas (de menos a más capacidad):

- Web (rápido, sin instalación):
  - Abre el repositorio en el navegador: https://github.com/Luciernaga-Sabionda/IASi_Entrega_SpaceApps
  - Presiona `.` en el navegador del repositorio para abrir la versión web de VS Code (github.dev). Ideal para cambios rápidos en archivos de texto.

- App GitHub / revisión de commits:
  - Instala la app GitHub en iOS/Android para revisar issues, commits y archivos.
  - Puedes navegar por ramas y ver la pestaña `Actions` para comprobar despliegues.

- Codespaces / Gitpod (recomendado si necesitas terminal):
  - Si tu cuenta tiene acceso a Codespaces, abre `Code -> Open with Codespaces` para un entorno VS Code completo en la nube.
  - Alternativamente, usa Gitpod: https://gitpod.io/#https://github.com/Luciernaga-Sabionda/IASi_Entrega_SpaceApps

- Edición remota en tu máquina (más control):
  - Conecta por SSH a tu PC donde tengas el repositorio y usa VS Code Remote o code-server.

Comandos útiles para ejecutar en PowerShell cuando vuelvas al equipo:

```powershell
# ver estado y últimos commits
git status
git fetch origin
git log --oneline -n 5

# actualizar con rebase
git pull --rebase origin main

# empujar cambios locales
git add -A
git commit -m "Breves cambios desde móvil"
git push origin main
```

Consejos de seguridad y buen uso:
- No subas credenciales ni secretos. Usa variables de entorno o secretos de GitHub Actions.
- Para cambios que afecten a la publicación en GitHub Pages revisa la acción `.github/workflows/deploy_app.yml` y la variable `SERVER_BASE`.
- Si el push falla por divergencia, ejecuta `git fetch origin; git rebase origin/main` y luego `git push --force-with-lease origin main` sólo si confirmas que no pierdes trabajo remoto.

Contacto rápido:
- Cuando vuelvas, dime si quieres que genere el ZIP de release, ejecute el test E2E o genere el PDF/MP4 de demostración y lo dejo listo.

---
Archivo creado automáticamente para facilitar trabajo desde dispositivos móviles.
