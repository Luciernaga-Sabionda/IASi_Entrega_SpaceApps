Write-Host "--- git push helper ---"

if(-not (Test-Path .\release.zip)){
  Write-Host "release.zip not found; generating via make_release_zip.py..."
  python .\scripts\make_release_zip.py
  if(-not (Test-Path .\release.zip)){
    Write-Host "Could not create release.zip. Check Python installation."; exit 1
  }
  Write-Host "release.zip created."
}

Write-Host "Git status:"; git status

Write-Host "To add a remote and push, run the following commands (replace URL):"
Write-Host "  git remote add origin https://github.com/<USER>/<REPO>.git"
Write-Host "  git branch -M main"
Write-Host "  git push -u origin main"

Write-Host "Or edit this script to set the repo URL and automate it."
