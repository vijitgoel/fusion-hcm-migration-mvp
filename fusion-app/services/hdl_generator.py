def generate_hdl(df):
    """
    Generate a simple HDL-style CSV content for Worker.
    """
    lines = []
    lines.append("METADATA|Worker|PersonNumber|FirstName|LastName|StartDate")

    for _, row in df.iterrows():
        employee_num = str(row["EmployeeNumber"])
        first_name = str(row["FirstName"])
        last_name = str(row["LastName"])
        hire_date = str(row["HireDate"])

        lines.append(
            f"MERGE|Worker|{employee_num}|{first_name}|{last_name}|{hire_date}"
        )

    return "\n".join(lines)