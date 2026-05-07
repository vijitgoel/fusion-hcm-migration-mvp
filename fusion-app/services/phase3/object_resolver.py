from .catalog import OBJECT_CATALOG

def detect_object(file_path):
    file_lower = file_path.lower()

    for key, obj in OBJECT_CATALOG.items():
        for keyword in obj["file_keywords"]:
            if keyword in file_lower:
                return obj

    return None