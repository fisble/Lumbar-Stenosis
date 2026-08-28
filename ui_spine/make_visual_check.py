import json
import random
from pathlib import Path
from PIL import Image, ImageDraw

roi_path = Path("D:/spine/roi_annotations_v2.json")
foramina_dir = Path("D:/spine/lab data/Foramina_Detection")
out_dir = Path("D:/spine/visual_check")
out_dir.mkdir(exist_ok=True)

with open(roi_path) as f:
    records = json.load(f)

successful = [r for r in records if r.get("seg_bbox") is not None]
print("Total successful records:", len(successful))

random.seed(42)
sample = random.sample(successful, min(8, len(successful)))

for i, rec in enumerate(sample):
    png_path = foramina_dir / rec["patient_id"] / (rec["slice_name"] + ".png")
    if not png_path.exists():
        print("missing png:", png_path)
        continue

    img = Image.open(png_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    ox = rec["original_bbox"]
    draw.rectangle(ox, outline="red", width=2)

    sx = rec["seg_bbox"]
    draw.rectangle(sx, outline="lime", width=2)

    label = rec["patient_id"] + "_" + rec["slice_name"] + "_" + rec["level"] + "_" + rec["side"]
    out_path = out_dir / (label + ".png")
    img.save(out_path)
    print("saved:", out_path.name, "| red=original green=seg-derived")
