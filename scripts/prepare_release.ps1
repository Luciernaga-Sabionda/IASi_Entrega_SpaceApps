# Prepara release.zip excluyendo carpetas de datos grandes
Param()
Write-Host "Preparando release.zip..."
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $root
if(Test-Path .\release.zip){ Remove-Item .\release.zip -Force }

$exclude = @('data','outputs','logs','venv','.venv','node_modules','__pycache__','release.zip')
$items = Get-ChildItem -Recurse -File | Where-Object {
    $p = $_.FullName.Substring($root.Length+1).Replace('/', '\')
    foreach($e in $exclude){ if($p -like "*\\$e\\*") { return $false } }
    return $true
}

if(-not $items){ Write-Host "No hay archivos para empaquetar"; Pop-Location; exit 1 }

$tmp = Join-Path $env:TEMP ("iasi_release_" + [int](Get-Date -UFormat %s))
New-Item -ItemType Directory -Path $tmp | Out-Null
foreach($it in $items){
    $rel = $it.FullName.Substring($root.Length+1)
    $dest = Join-Path $tmp $rel
    New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null
    Copy-Item $it.FullName -Destination $dest -Force
}

Compress-Archive -Path (Join-Path $tmp '*') -DestinationPath (Join-Path $root 'release.zip') -Force
Remove-Item -Recurse -Force $tmp
Write-Host "release.zip creado en: $root\release.zip"
Pop-Location
