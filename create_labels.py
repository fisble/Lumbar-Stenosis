import pandas as pd

# ===== LOAD EXCEL =====
file_path = "Radiologists Report.xlsx"
df = pd.read_excel(file_path)

# ===== CORRECT COLUMN NAMES =====
IMAGE_COL = "Patient ID"
REPORT_COL = "Clinician's Notes"

# ===== LABEL FUNCTION =====
def extract_labels(text):
    text = str(text).lower()

    return {
        "bulge": int("bulge" in text or "bulges" in text),
        "protrusion": int("protrusion" in text),
        "herniation": int("herniation" in text),
        "spasm": int("spasm" in text),
        "degeneration": int("degeneration" in text),
        "stenosis": int("stenosis" in text),
    }

# ===== APPLY =====
labels_df = df[REPORT_COL].apply(extract_labels).apply(pd.Series)

# ===== COMBINE =====
final_df = pd.concat([df[IMAGE_COL], labels_df], axis=1)

# ===== SAVE =====
final_df.to_csv("labels.csv", index=False)

print("✅ labels.csv created")
print(final_df.head())