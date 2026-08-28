import os
import cv2
import shutil
import numpy as np

# ===== PATHS =====
image_dir = r"D:\spine\05_Final_Ground_Truth_Data\Resized_Composite_Images"
mask_dir = r"D:\spine\05_Final_Ground_Truth_Data\Resized_Label_Images"
output_dir = r"D:\spine\processed_dataset"

normal_dir = os.path.join(output_dir, "normal")
abnormal_dir = os.path.join(output_dir, "abnormal")

# Ensure output directories exist
os.makedirs(normal_dir, exist_ok=True)
os.makedirs(abnormal_dir, exist_ok=True)

# ===== PROCESS =====
normal_count = 0
abnormal_count = 0

for filename in os.listdir(image_dir):

    img_path = os.path.join(image_dir, filename)
    mask_path = os.path.join(mask_dir, filename)

    # Skip if mask not found
    if not os.path.exists(mask_path):
        continue

    # Read mask (grayscale)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    if mask is None:
        continue

    # Check abnormality
    if np.sum(mask) > 0:
        label_dir = abnormal_dir
        abnormal_count += 1
    else:
        label_dir = normal_dir
        normal_count += 1

    # Copy image
    shutil.copy(img_path, os.path.join(label_dir, filename))

print("Done")
print(f"Normal: {normal_count}")
print(f"Abnormal: {abnormal_count}")