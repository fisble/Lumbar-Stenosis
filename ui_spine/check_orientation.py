import pydicom
from pathlib import Path

patients_to_check = ["0232", "0288", "0008", "0045", "0055", "0085", "0092", "0104"]
dicom_root = Path("D:/spine/lab data/DICOM")

for pid in patients_to_check:
    folder = dicom_root / pid
    first_file = sorted(folder.glob("*.dcm"))[0]
    ds = pydicom.dcmread(str(first_file), stop_before_pixels=True)
    pos = getattr(ds, "PatientPosition", "MISSING")
    orient = getattr(ds, "ImageOrientationPatient", "MISSING")
    print(pid, "PatientPosition=" + str(pos), "ImageOrientationPatient=" + str(orient))
