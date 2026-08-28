import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# ===== LOAD DATA =====
file_path = r"D:\spine\Radiologists Report.xlsx"
df = pd.read_excel(file_path)

# ===== CLEAN TEXT COLUMN =====
texts = df["Clinician's Notes"].fillna("").astype(str)

# ===== WEAK LABEL FUNCTION =====
def weak_label(text):
    text = str(text).lower()

    # Strong indicators of NORMAL
    normal_patterns = [
        "no evidence",
        "no significant",
        "normal study",
        "no disc herniation",
        "no stenosis"
    ]

    for phrase in normal_patterns:
        if phrase in text:
            return 0

    # Otherwise assume abnormal
    return 1

# Generate initial weak labels
y = texts.apply(weak_label)

# ===== TEXT → FEATURES =====
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(texts)

# ===== TRAIN MODEL =====
model = LogisticRegression(max_iter=1000)
model.fit(X, y)

# ===== PREDICT (REFINED LABELS) =====
predictions = model.predict(X)

# ===== STORE LABELS =====
labels = {}

for i, row in df.iterrows():
    patient_id = str(row["Patient ID"]).zfill(4)
    labels[patient_id] = int(predictions[i])

# ===== OUTPUT SAMPLE =====
print("\nSample labels:")
for k in list(labels.keys())[:10]:
    print(k, labels[k])

print("\nTotal patients:", len(labels))
print("Abnormal count:", sum(labels.values()))
print("Normal count:", len(labels) - sum(labels.values()))
import json

with open("labels.json", "w") as f:
    json.dump(labels, f)

print("Labels saved to labels.json")