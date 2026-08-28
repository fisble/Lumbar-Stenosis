import os
import shutil
import pandas as pd
import random

# ===== PATHS =====
DATASET_PATH = "final_sag_dataset"
CSV_PATH = "labels.csv"
OUTPUT_PATH = "multi_label_dataset"

label_cols = ["bulge","protrusion","herniation","spasm","degeneration","stenosis"]
TEST_COUNT = 20

# ===== LOAD CSV =====
df = pd.read_csv(CSV_PATH)
df["Patient ID"] = df["Patient ID"].astype(int)

# ===== CREATE FOLDERS =====
for split in ["train", "val"]:
    for label in label_cols:
        os.makedirs(os.path.join(OUTPUT_PATH, split, label), exist_ok=True)

os.makedirs(os.path.join(OUTPUT_PATH, "test"), exist_ok=True)

# ===== COLLECT ONLY ABNORMAL IMAGES =====
all_images = []

for split in ["train", "val"]:
    folder = os.path.join(DATASET_PATH, split, "abnormal")

    if not os.path.exists(folder):
        continue

    for img_name in os.listdir(folder):
        if img_name.endswith((".png", ".jpg", ".jpeg")):
            all_images.append((split, img_name))

print("Total abnormal images found:", len(all_images))

# ===== SHUFFLE =====
random.shuffle(all_images)

# ===== TEST SET =====
test_samples = all_images[:TEST_COUNT]
remaining_samples = all_images[TEST_COUNT:]

# ===== TRAIN / VAL SPLIT =====
split_idx = int(0.8 * len(remaining_samples))
train_samples = remaining_samples[:split_idx]
val_samples   = remaining_samples[split_idx:]

# ===== COPY TEST (NO LABELS) =====
for split, img_name in test_samples:
    src = os.path.join(DATASET_PATH, split, "abnormal", img_name)
    dst = os.path.join(OUTPUT_PATH, "test", img_name)
    shutil.copy(src, dst)

# ===== COPY TRAIN/VAL (MULTI-LABEL) =====
def copy_samples(samples, target_split):
    for split, img_name in samples:

        src = os.path.join(DATASET_PATH, split, "abnormal", img_name)

        # ===== FIXED ID EXTRACTION =====
        name = os.path.splitext(img_name)[0]
        parts = name.split("_")

        try:
            patient_id = int(parts[0])
        except:
            continue

        row = df[df["Patient ID"] == patient_id]

        if row.empty:
            continue

        row = row.iloc[0]

        for label in label_cols:
            if row[label] == 1:
                dst = os.path.join(OUTPUT_PATH, target_split, label, img_name)
                shutil.copy(src, dst)

copy_samples(train_samples, "train")
copy_samples(val_samples, "val")

# ===== DONE =====
print("✅ Dataset created successfully")
print("Train samples:", len(train_samples))
print("Val samples:", len(val_samples))
print("Test samples:", len(test_samples))