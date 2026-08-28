Write-Host "Removing dataset/image folders from git index..."
$dirs = @(
    '01_MRI_Data',
    '03_Manual_Label_Data',
    '04_Intermediary_Ground_Truth_Data',
    '05_Final_Ground_Truth_Data',
    'converted_images',
    'filtered_dataset',
    'final_dataset',
    'final_sag_dataset',
    'multi_label_dataset',
    'processed',
    'sag_dataset',
    'volumes',
    'sample images',
    'lab data',
    'visual_check',
    'visual_check_v2',
    'verseg'
)

foreach ($d in $dirs) {
    Write-Host "Processing: $d"
    & git rm -r --cached --ignore-unmatch -- "$d" 2>$null
}

Write-Host "Staging changes..."
& git add .

Write-Host "Committing..."
& git commit -m "Remove dataset and image folders from index" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "No new commit created (no changes staged)."
    exit 0
}

Write-Host "Pushing to origin main..."
& git push origin main
Write-Host "Done."
