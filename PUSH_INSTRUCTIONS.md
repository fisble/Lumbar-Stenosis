# How to push this project to GitHub

This workspace is prepared to push only the code and the `output/` images. Datasets and raw medical images are ignored by `.gitignore`.

Steps (PowerShell):

1. Initialize repository (if not already):

```powershell
cd path\to\spine  # e.g. d:\spine
git init
git remote add origin https://github.com/fisble/Lumbar-Stenosis.git
```

2. If you previously committed dataset files, remove them from the index (they will remain on disk):

```powershell
git rm -r --cached "01_MRI_Data" "converted_images" "final_dataset" "multi_label_dataset" || true
git commit -m "Remove dataset files from index"
```

3. Add, commit, and push (create `main` branch if necessary):

```powershell
git add .
git commit -m "Prepare code-only repository with output images"
git branch -M main
git push -u origin main
```

Notes:
- Review `git status` before committing to ensure only intended files are staged.
- If the remote already has content and you need to overwrite, coordinate carefully and use `git pull --rebase` or force push with caution.
