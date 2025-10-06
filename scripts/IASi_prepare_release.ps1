Write-Host "Preparando IASi_release.zip..."
if(Test-Path .\IASi_release.zip){ Remove-Item .\IASi_release.zip -Force }
python .\scripts\iasi_make_release_zip.py
if(Test-Path .\IASi_release.zip){ Write-Host "IASi_release.zip creado." } else { Write-Host "Error creando IASi_release.zip" }
