import os
import shutil
import json

# ===== LOAD LABELS (ML OUTPUT) =====
labels_path = r"D:\spine\labels.json"

with open(labels_path, "r") as f:
    labels = json.load(f)

# ===== PATHS =====
input_root = r"D:\spine\converted_images"
output_root = r"D:\spine\final_dataset"

normal_dir = os.path.join(output_root, "normal")
abnormal_dir = os.path.join(output_root, "abnormal")

os.makedirs(normal_dir, exist_ok=True)
os.makedirs(abnormal_dir, exist_ok=True)

# ===== COUNTERS =====
normal_count = 0
abnormal_count = 0
skipped_patients = 0

# ===== PROCESS =====
for patient in os.listdir(input_root):
    patient_path = os.path.join(input_root, patient)

    # Skip if not a folder
    if not os.path.isdir(patient_path):
        continue

    # Skip if no label
    if patient not in labels:
        skipped_patients += 1
        continue

    label = labels[patient]

    # Traverse all nested folders (your structure is deep)
    for root, dirs, files in os.walk(patient_path):
        for file in files:
            if file.endswith(".png"):
                src = os.path.join(root, file)

                # Unique filename to avoid overwrite
                new_name = f"{patient}_{file}"
                
                if label == 1:
                    dst = os.path.join(abnormal_dir, new_name)
                    abnormal_count += 1
                else:
                    dst = os.path.join(normal_dir, new_name)
                    normal_count += 1

                shutil.copy(src, dst)

# ===== OUTPUT =====
print("\nDone")
print("Normal images:", normal_count)
print("Abnormal images:", abnormal_count)
print("Skipped patients:", skipped_patients)