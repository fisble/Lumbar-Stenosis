import json
import SimpleITK as sitk
import numpy as np
from pathlib import Path

masks_dir = Path("D:/spine/verseg/experiments/SPIDER-Baseline/results/MyForamina")

def build_vertebra_order(mask_img, mask_arr):
    raw_labels = np.unique(mask_arr)
    vertebra_labels = set()
    for v in raw_labels:
        v = int(v)
        if v <= 0 or v >= 200:
            continue
        if v >= 100:
            v = v - 100
        vertebra_labels.add(v)

    centroids = {}
    for label in vertebra_labels:
        mask_this = np.logical_or(mask_arr == label, mask_arr == label + 100)
        if not mask_this.any():
            continue
        idx = np.argwhere(mask_this)
        centroid_idx = idx.mean(axis=0)
        phys = mask_img.TransformContinuousIndexToPhysicalPoint(
            (float(centroid_idx[2]), float(centroid_idx[1]), float(centroid_idx[0]))
        )
        centroids[label] = np.array(phys)

    coords = np.array(list(centroids.values()))
    spread = coords.max(axis=0) - coords.min(axis=0)
    axis = int(np.argmax(spread))
    sorted_labels = sorted(centroids.keys(), key=lambda l: centroids[l][axis])
    return sorted_labels, centroids, axis, spread

for pid in ["0232", "0288", "0045", "0055"]:
    mask_path = masks_dir / (pid + "_total_segmentation_original.mha")
    mask_img = sitk.ReadImage(str(mask_path))
    mask_arr = sitk.GetArrayFromImage(mask_img)

    sorted_labels, centroids, axis, spread = build_vertebra_order(mask_img, mask_arr)
    print("Patient", pid)
    print("  num vertebrae found:", len(sorted_labels))
    print("  sorted_labels (bottom to top, assumed):", sorted_labels)
    print("  chosen axis:", axis, "spread:", spread)
    for lbl in sorted_labels:
        print("    label", lbl, "centroid", centroids[lbl])
    print("")
