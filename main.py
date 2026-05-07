from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
import pandas as pd
from io import BytesIO, StringIO
import io

# Create FastAPI app
app = FastAPI(title="Fusion HCM HDL Converter", description="Upload Excel/CSV to generate Oracle Fusion HCM HDL Worker file")

@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Simple HTML page with upload form.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Fusion HCM HDL Converter</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                form { border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
                input[type="file"] { margin-bottom: 10px; }
                input[type="submit"] { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                h1 { color: #333; }
            </style>
        </head>
        <body>
            <h1>Upload Employee Data (Excel .xlsx or CSV)</h1>
            <p>Required columns: EmployeeNumber, FirstName, LastName, HireDate</p>
            <form action="/upload" enctype="multipart/form-data" method="post">
                <input type="file" name="file" accept=".xlsx,.csv" required>
                <br>
                <input type="submit" value="Convert to HDL">
            </form>
        </body>
    </html>
    """
    return html_content

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload endpoint:
    1. Reads Excel or CSV using pandas
    2. Validates required columns
    3. Maps to HDL Worker format
    4. Returns downloadable CSV
    """
    # Validate file type
    if not file.filename.lower().endswith(('.xlsx', '.csv')):
        raise HTTPException(status_code=400, detail="Only .xlsx or .csv files are allowed!")

    # Read file content
    content = await file.read()

    try:
        # Handle Excel or CSV
        if file.filename.lower().endswith('.xlsx'):
            df = pd.read_excel(BytesIO(content))
        else:
            # Decode CSV content and read
            csv_content = io.StringIO(content.decode('utf-8'))
            df = pd.read_csv(csv_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error reading file. Ensure it's a valid Excel or CSV file.")

    # Validate required columns
    required_columns = ['EmployeeNumber', 'FirstName', 'LastName', 'HireDate']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required columns: {', '.join(missing_columns)}. Please include: {', '.join(required_columns)}"
        )

    # Generate HDL CSV content
    hdl_lines = []
    # Header row
    hdl_lines.append("METADATA|Worker|PersonNumber|FirstName|LastName|StartDate")
    
    # Data rows (MERGE operation)
    for index, row in df.iterrows():
        # Use str() to handle any data types safely
        employee_num = str(row['EmployeeNumber'])
        first_name = str(row['FirstName'])
        last_name = str(row['LastName'])
        hire_date = str(row['HireDate'])
        
        hdl_line = f"MERGE|Worker|{employee_num}|{first_name}|{last_name}|{hire_date}"
        hdl_lines.append(hdl_line)

    # Join lines with newlines
    hdl_csv_content = '\n'.join(hdl_lines)

    # Return as downloadable CSV file
    return StreamingResponse(
        iter([hdl_csv_content.encode('utf-8')]),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="worker.hdl.csv"'
        }
    )

# To run: uvicorn main:app --reload
# Visit http://127.0.0.1:8000/