def write_dat(df, object_name, output_path):
    file_path = f"{output_path}/{object_name}.dat"

    with open(file_path, "w") as f:
        f.write("METADATA|...\n")
        for _, row in df.iterrows():
            f.write("|".join([str(x) for x in row]) + "\n")

    return file_path