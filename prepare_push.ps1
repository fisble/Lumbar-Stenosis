Param(
    [string]$RemoteUrl = "https://github.com/fisble/Lumbar-Stenosis.git"
)

Write-Host "Preparing repository for push..."

if (-not (Test-Path -Path .git)) {
    git init
    Write-Host "Initialized git repository."
}

$existing = & git remote get-url origin 2>$null
if (-not $existing) {
    & git remote add origin $RemoteUrl
    Write-Host "Added remote origin: $RemoteUrl"
} else {
    Write-Host "Remote origin already set to: $existing"
}

Write-Host "Removing common dataset folders from git index (cached only)..."
@("01_MRI_Data","converted_images","final_dataset","multi_label_dataset","multi_label_dataset.zip","final_sag_dataset","volumes","sample images","lab data") | ForEach-Object {
    if (Test-Path $_) {
        & git rm -r --cached "$_" -f 2>$null
        Write-Host "Untracked from index: $_"
    }
}

Write-Host "Staging all changes..."
git add .

$status = git status --porcelain
if (-not $status) {
    Write-Host "Nothing to commit."
    exit 0
}

& git commit -m "Prepare code-only repo (remove datasets from index)" 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "No new commit created." }

Write-Host "Pushing to origin main (create branch if needed)..."
git branch -M main
git push -u origin main

Write-Host "Done. Verify remote at: $RemoteUrl"
