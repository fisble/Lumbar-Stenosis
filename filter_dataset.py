import os
import shutil
import json

# ===== PATHS =====
source_dir = r"D:\spine\converted_images"
labels_path = r"D:\spine\labels.json"
output_dir = r"D:\spine\filtered_dataset"

# ===== LOAD LABELS =====
with open(labels_path, "r") as f:
    labels = json.load(f)

# ===== CREATE OUTPUT FOLDERS =====
normal_dir = os.path.join(output_dir, "normal")
abnormal_dir = os.path.join(output_dir, "abnormal")

os.makedirs(normal_dir, exist_ok=True)
os.makedirs(abnormal_dir, exist_ok=True)

# ===== FILTER FUNCTION =====
def is_valid_image(filename):
    filename = filename.upper()
    return ("SAG" in filename) or ("TRA" in filename)

# ===== COUNTERS =====
normal_count = 0
abnormal_count = 0
skipped_patients = 0

# ===== PROCESS =====
for patient_id in os.listdir(source_dir):
    patient_path = os.path.join(source_dir, patient_id)

    if not os.path.isdir(patient_path):
        continue

    # Skip if label not found
    if patient_id not in labels:
        skipped_patients += 1
        continue

    label = labels[patient_id]

    for root, dirs, files in os.walk(patient_path):
        for file in files:
            if not file.lower().endswith(".png"):
                continue

            # Keep only SAG / TRA
            if not is_valid_image(file):
                continue

            src = os.path.join(root, file)

            # SAFE filename (prevents overwrite)
            new_filename = f"{patient_id}_{file}"

            if label == 0:
                dst = os.path.join(normal_dir, new_filename)
                normal_count += 1
            else:
                dst = os.path.join(abnormal_dir, new_filename)
                abnormal_count += 1

            shutil.copy(src, dst)

# ===== OUTPUT =====
print("\nDone")
print("Normal images:", normal_count)
print("Abnormal images:", abnormal_count)
print("Skipped patients:", skipped_patients)