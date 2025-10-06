Write-Host "--- IASi git push helper ---"
if(-not (Test-Path .\IASi_release.zip)){
  Write-Host "IASi_release.zip not found; generating via iasi_make_release_zip.py..."
  python .\scripts\iasi_make_release_zip.py
  if(-not (Test-Path .\IASi_release.zip)){
    Write-Host "Could not create IASi_release.zip. Check Python installation."; exit 1
  }
  Write-Host "IASi_release.zip created."
}

Write-Host "Git status:"; git status
Write-Host "To push to GitHub:"
Write-Host "  git remote add origin https://github.com/<USER>/<REPO>.git"
Write-Host "  git branch -M main"
Write-Host "  git push -u origin main"
