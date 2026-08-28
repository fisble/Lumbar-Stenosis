import os
import pydicom
import cv2
import numpy as np

input_root = r"D:\spine\01_MRI_Data"
output_root = r"D:\spine\converted_images"

os.makedirs(output_root, exist_ok=True)

def normalize_image(img):
    img = img.astype(np.float32)
    img = (img - np.min(img)) / (np.max(img) - np.min(img))
    img = (img * 255).astype(np.uint8)
    return img

count = 0

for patient in os.listdir(input_root):
    patient_path = os.path.join(input_root, patient)

    for root, dirs, files in os.walk(patient_path):
        for file in files:
            if file.endswith(".ima"):
                file_path = os.path.join(root, file)

                try:
                    dicom = pydicom.dcmread(file_path)
                    img = dicom.pixel_array
                    img = normalize_image(img)

                    # Create output path
                    relative_path = os.path.relpath(root, input_root)
                    save_dir = os.path.join(output_root, relative_path)
                    os.makedirs(save_dir, exist_ok=True)

                    save_path = os.path.join(save_dir, file.replace(".ima", ".png"))

                    cv2.imwrite(save_path, img)
                    count += 1

                except Exception as e:
                    print(f"Error: {file_path}")

print(f"Converted {count} images")