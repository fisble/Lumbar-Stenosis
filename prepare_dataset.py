import os
import random
import shutil

# ===== PATHS =====
input_dir = r"D:\spine\sag_dataset"
output_dir = r"D:\spine\final_sag_dataset"

train_ratio = 0.8

# ===== CREATE OUTPUT STRUCTURE =====
for split in ["train", "val"]:
    for cls in ["normal", "abnormal"]:
        os.makedirs(os.path.join(output_dir, split, cls), exist_ok=True)

# ===== LOAD FILES =====
normal_files = os.listdir(os.path.join(input_dir, "normal"))
abnormal_files = os.listdir(os.path.join(input_dir, "abnormal"))

# ===== BALANCE =====
min_count = min(len(normal_files), len(abnormal_files))

normal_files = random.sample(normal_files, min_count)
abnormal_files = random.sample(abnormal_files, min_count)

print(f"Balanced count per class: {min_count}")

# ===== SPLIT FUNCTION =====
def split_and_copy(files, cls):
    random.shuffle(files)
    split_idx = int(len(files) * train_ratio)

    train_files = files[:split_idx]
    val_files = files[split_idx:]

    for f in train_files:
        src = os.path.join(input_dir, cls, f)
        dst = os.path.join(output_dir, "train", cls, f)
        shutil.copy(src, dst)

    for f in val_files:
        src = os.path.join(input_dir, cls, f)
        dst = os.path.join(output_dir, "val", cls, f)
        shutil.copy(src, dst)

# ===== PROCESS =====
split_and_copy(normal_files, "normal")
split_and_copy(abnormal_files, "abnormal")

print("Done")