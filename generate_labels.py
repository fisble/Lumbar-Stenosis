import pandas as pd
import re

file_path = r"D:\spine\Radiologists Report.xlsx"

df = pd.read_excel(file_path)

def is_abnormal(report):
    report = str(report).lower()

    # keywords indicating abnormality
    keywords = [
        "bulge", "herniation", "protrusion",
        "stenosis", "degenerative", "tear"
    ]

    for word in keywords:
        if word in report:
            return 1

    return 0

labels = {}

for _, row in df.iterrows():
    patient_id = str(row["Patient ID"]).zfill(4)
    report = row["Clinician's Notes"]

    labels[patient_id] = is_abnormal(report)

# Show sample
for k in list(labels.keys())[:10]:
    print(k, labels[k])

print("Total patients:", len(labels))