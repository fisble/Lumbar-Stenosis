import pandas as pd
import os
import shutil
import random

# ===== PATHS =====
CSV_PATH = "labels.csv"
IMAGE_FOLDER = "images"
OUTPUT_FOLDER = "dataset"

label_cols = ["bulge","protrusion","herniation","spasm","degeneration","stenosis"]

# ===== LOAD CSV =====
df = pd.read_csv(CSV_PATH)

# ===== CREATE FOLDERS =====
for split in ["train", "val", "test"]:
    for label in label_cols:
        os.makedirs(os.path.join(OUTPUT_FOLDER, split, label), exist_ok=True)

# ===== CREATE IMAGE LIST =====
image_list = []

for _, row in df.iterrows():
    img_name = f"{row['Patient ID']}.png"
    labels = [label for label in label_cols if row[label] == 1]

    if len(labels) == 0:
        continue  # skip if no abnormality

    image_list.append((img_name, labels))

# ===== SHUFFLE =====
random.shuffle(image_list)

# ===== TEST SET (10 images) =====
test_samples = image_list[:10]
remaining = image_list[10:]

# ===== TRAIN / VAL SPLIT =====
split_idx = int(0.8 * len(remaining))
train_samples = remaining[:split_idx]
val_samples   = remaining[split_idx:]

# ===== COPY FUNCTION =====
def copy_multi_label(samples, split):
    for img_name, labels in samples:
        src = os.path.join(IMAGE_FOLDER, img_name)

        if not os.path.exists(src):
            continue

        for label in labels:
            dst = os.path.join(OUTPUT_FOLDER, split, label, img_name)
            shutil.copy(src, dst)

# ===== COPY FILES =====
copy_multi_label(train_samples, "train")
copy_multi_label(val_samples, "val")
copy_multi_label(test_samples, "test")

# ===== DONE =====
print("✅ Dataset created")
print("Train:", len(train_samples))
print("Val:", len(val_samples))
print("Test:", len(test_samples))