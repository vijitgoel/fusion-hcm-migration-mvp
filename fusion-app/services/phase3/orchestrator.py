import os
from .scanner import scan_folder
from .object_resolver import detect_object
from .processor import read_file, normalize, validate
from .hdl_writer import write_dat

def run_batch(root_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    files = scan_folder(root_folder)

    summary = {
        "total_files": len(files),
        "objects": {},
    }

    for file in files:
        obj = detect_object(file)

        if not obj:
            continue

        df = read_file(file)
        df = normalize(df)

        errors = validate(df, obj["required_columns"])

        clean_df = df if not errors else df.iloc[0:0]

        dat_file = write_dat(clean_df, obj["name"], output_folder)

        summary["objects"].setdefault(obj["name"], {
            "files": 0,
            "errors": 0
        })

        summary["objects"][obj["name"]]["files"] += 1
        summary["objects"][obj["name"]]["errors"] += len(errors)

    return summary