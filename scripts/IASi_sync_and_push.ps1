<#
IASi_sync_and_push.ps1

Usage: Run this script from the repository root in PowerShell:
  .\scripts\IASi_sync_and_push.ps1
<#
IASi_sync_and_push.ps1

Usage: Run this script from the repository root in PowerShell:
  .\scripts\IASi_sync_and_push.ps1

What it does:
- Verifies git is available
- Shows current branch and remotes
- Fetches origin
- Tries `git pull --rebase origin main` (keeps history linear)
- If rebase fails, falls back to `git pull origin main --allow-unrelated-histories`
- If conflicts appear, lists them and exits for manual resolution
- If pull succeeds, runs `git push -u origin main` and reports result

Note: When `git push` prompts for credentials, use your GitHub username and
for password paste the Personal Access Token (PAT).
#>

function Abort($msg){ Write-Host $msg -ForegroundColor Red; exit 1 }

Write-Host "== IASi sync & push helper ==" -ForegroundColor Cyan

# Ensure we're in a git repo
if (-not (Test-Path .git)){
  Abort "This does not look like a Git repository (no .git folder). Run from the repo root."
}

# Check git availability
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git){ Abort "Git not found in PATH. Install Git for Windows and try again." }

Write-Host "Current branch:" -NoNewline; git rev-parse --abbrev-ref HEAD
Write-Host "Remotes:"; git remote -v

$origin = git remote get-url origin 2>$null
if (-not $origin){
  Write-Host "No origin remote configured." -ForegroundColor Yellow
  $url = Read-Host "Enter the HTTPS URL of your GitHub repo (eg https://github.com/USER/REPO.git), or press Enter to abort"
  if (-not $url){ Abort "No origin configured. Aborting." }
  git remote add origin $url
  Write-Host "Added origin -> $url"
}

Write-Host "Fetching origin..."
$fetchOut = git fetch origin 2>&1
if ($LASTEXITCODE -ne 0){ Abort "git fetch failed:`n$fetchOut" }

Write-Host "Attempting rebase: git pull --rebase origin main"
$pull = git pull --rebase origin main 2>&1
if ($LASTEXITCODE -eq 0){
  Write-Host "Pull (rebase) succeeded." -ForegroundColor Green
} else {
  Write-Host "Rebase failed or not possible. Falling back to merge with --allow-unrelated-histories" -ForegroundColor Yellow
  Write-Host $pull
  Write-Host "Running: git pull origin main --allow-unrelated-histories"
  $pull2 = git pull origin main --allow-unrelated-histories 2>&1
  if ($LASTEXITCODE -ne 0){
    Write-Host $pull2
    # detect conflicts
    Write-Host "Pull failed. Checking for conflicts..." -ForegroundColor Red
    git status --porcelain
    Write-Host "If there are conflicts, resolve them manually, then run:`n  git add <files>
  git commit` (if merge) or `git rebase --continue` (if rebase)." -ForegroundColor Yellow
    Abort "Pull could not be completed automatically. Resolve conflicts and retry." 
  } else {
    Write-Host "Pull (merge) succeeded." -ForegroundColor Green
  }
}

Write-Host "Now pushing local main to origin..."
$pushOut = git push -u origin main 2>&1
if ($LASTEXITCODE -eq 0){ Write-Host "Push succeeded." -ForegroundColor Green }
else { Write-Host "Push returned non-zero exit code. Output:"; Write-Host $pushOut; Write-Host "Check output above and ensure credentials (PAT) are correct." -ForegroundColor Red }

Write-Host "Done. If push failed due to auth, ensure you used your GitHub username and PAT when prompted." -ForegroundColor Cyan
