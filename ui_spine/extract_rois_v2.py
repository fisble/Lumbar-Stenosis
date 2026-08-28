import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import SimpleITK as sitk



GRADE_MAP = {"0": 0, "1": 1, "2": 2, "3": 3}
PAD = 5
LEVELS_BOTTOM_UP = ["L5-S1", "L4-L5", "L3-L4", "L2-L3", "L1-L2"]
VERTEBRA_NAMES_BOTTOM_UP = ["L5", "L4", "L3", "L2", "L1"]


def parse_xml(xml_path):
    records = []
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError:
        return records

    slice_name = Path(root.findtext("filename", "")).stem
    patient_id = xml_path.parent.name

    for obj in root.findall("object"):
        name = obj.findtext("name", "")
        level = obj.findtext("level", "")
        if len(name) < 4 or level not in LEVELS_BOTTOM_UP:
            continue

        side = name[:3]
        grade_char = name[3]
        if grade_char not in GRADE_MAP:
            continue

        bb = obj.find("bndbox")
        if bb is None:
            continue
        try:
            bbox = (
                int(bb.findtext("xmin")), int(bb.findtext("ymin")),
                int(bb.findtext("xmax")), int(bb.findtext("ymax")),
            )
        except (TypeError, ValueError):
            continue

        records.append({
            "patient_id": patient_id,
            "slice_name": slice_name,
            "side": side,
            "grade": GRADE_MAP[grade_char],
            "level": level,
            "original_bbox": bbox,
        })
    return records


def build_vertebra_order(mask_img, mask_arr):
    raw_labels = np.unique(mask_arr)
    vertebra_labels = set()
    for v in raw_labels:
        v = int(v)
        if v <= 0 or v >= 200:
            continue
        if v == 100:
            continue
        if v >= 101:
            v = v - 100
        vertebra_labels.add(v)

    if not vertebra_labels:
        return []

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

    if len(centroids) < 2:
        return []

    coords = np.array(list(centroids.values()))
    spread = coords.max(axis=0) - coords.min(axis=0)
    axis = int(np.argmax(spread))

    sorted_labels = sorted(centroids.keys(), key=lambda l: centroids[l][axis])
    return sorted_labels


def get_bbox_for_labels_in_slice(mask_slice, primary_label):
    combined = np.logical_or(mask_slice == primary_label, mask_slice == primary_label + 100)
    if not combined.any():
        return None
    ys, xs = np.nonzero(combined)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def combine_bboxes(b1, b2):
    if b1 is None:
        return b2
    if b2 is None:
        return b1
    return (min(b1[0], b2[0]), min(b1[1], b2[1]), max(b1[2], b2[2]), max(b1[3], b2[3]))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--foramina_dir", required=True)
    p.add_argument("--volumes_dir", required=True)
    p.add_argument("--masks_dir", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    foramina_dir = Path(args.foramina_dir)
    volumes_dir = Path(args.volumes_dir)
    masks_dir = Path(args.masks_dir)

    all_records = []
    n_ok = 0
    n_no_mask_file = 0
    n_no_slice_map = 0
    n_slice_not_found = 0
    n_labels_missing = 0

    xml_paths = sorted(foramina_dir.rglob("*.xml"))
    print("Found " + str(len(xml_paths)) + " XML annotation files")
    print("")

    patient_cache = {}

    for xml_path in xml_paths:
        for rec in parse_xml(xml_path):
            patient_id = rec["patient_id"]

            if patient_id not in patient_cache:
                mask_path = masks_dir / (patient_id + "_total_segmentation_original.mha")
                slice_map_path = volumes_dir / (patient_id + "_slice_map.json")

                if not mask_path.exists():
                    patient_cache[patient_id] = None
                    n_no_mask_file += 1
                elif not slice_map_path.exists():
                    patient_cache[patient_id] = None
                    n_no_slice_map += 1
                else:
                    try:
                        mask_img = sitk.ReadImage(str(mask_path))
                        mask_arr = sitk.GetArrayFromImage(mask_img)
                        with open(slice_map_path) as f:
                            slice_map = json.load(f)
                        name_to_index = {v: int(k) for k, v in slice_map.items()}
                        sorted_labels = build_vertebra_order(mask_img, mask_arr)
                        patient_cache[patient_id] = {
                            "mask_arr": mask_arr,
                            "name_to_index": name_to_index,
                            "sorted_labels": sorted_labels,
                        }
                    except RuntimeError:
                        print("  [corrupt] " + patient_id + ": unreadable mask, skipping")
                        patient_cache[patient_id] = None
                        n_no_mask_file += 1

            cached = patient_cache[patient_id]
            if cached is None:
                continue

            mask_arr = cached["mask_arr"]
            name_to_index = cached["name_to_index"]
            sorted_labels = cached["sorted_labels"]

            slice_idx = name_to_index.get(rec["slice_name"])
            if slice_idx is None or slice_idx >= mask_arr.shape[0]:
                n_slice_not_found += 1
                continue

            level = rec["level"]
            ordinal = LEVELS_BOTTOM_UP.index(level)

            if ordinal + 1 >= len(sorted_labels):
                n_labels_missing += 1
                rec["seg_bbox"] = None
                all_records.append(rec)
                continue

            label_a = sorted_labels[ordinal]
            label_b = sorted_labels[ordinal + 1]

            search_order = [0, -1, 1, -2, 2, -3, 3]
            seg_bbox = None
            for offset in search_order:
                candidate_idx = slice_idx + offset
                if 0 <= candidate_idx < mask_arr.shape[0]:
                    ms = mask_arr[candidate_idx]
                    b1 = get_bbox_for_labels_in_slice(ms, label_a)
                    b2 = get_bbox_for_labels_in_slice(ms, label_b)
                    combined = combine_bboxes(b1, b2)
                    if combined is not None:
                        seg_bbox = combined
                        break

            if seg_bbox is None:
                n_labels_missing += 1
                rec["seg_bbox"] = None
            else:
                xmin, ymin, xmax, ymax = seg_bbox
                rec["seg_bbox"] = (
                    max(0, xmin - PAD), max(0, ymin - PAD),
                    xmax + PAD, ymax + PAD,
                )
                n_ok += 1

            all_records.append(rec)

    with open(args.out, "w") as f:
        json.dump(all_records, f, indent=2)

    print("Total annotations processed: " + str(len(all_records)))
    print("  seg_bbox successfully derived: " + str(n_ok))
    print("  missing mask file:             " + str(n_no_mask_file))
    print("  missing slice_map.json:        " + str(n_no_slice_map))
    print("  slice index not in mask:       " + str(n_slice_not_found))
    print("  vertebra labels not found:     " + str(n_labels_missing))
    print("")
    print("Output written to " + args.out)


if __name__ == "__main__":
    main()
