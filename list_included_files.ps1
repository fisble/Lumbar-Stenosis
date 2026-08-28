# Lists files that would be included in the commit, excluding large dataset folders
$exclude = @(
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

Get-ChildItem -Path . -Recurse -File | Where-Object {
    $full = $_.FullName
    $skip = $false
    foreach ($d in $exclude) {
        if ($full -like "*\\$d\\*") { $skip = $true; break }
    }
    -not $skip
} | Sort-Object FullName | ForEach-Object { $_.FullName }
