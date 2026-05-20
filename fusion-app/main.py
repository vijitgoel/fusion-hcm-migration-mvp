from __future__ import annotations

import logging
import sys
import time
from io import BytesIO, StringIO

import pandas as pd
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from services.hdl_generator import generate_hdl
from services.phase3.engine import process_folder
from services.phase3.utils import sanitize_for_json
from services.validator import validate_columns, validate_data
from pathlib import Path

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logger = logging.getLogger("fusion_hcm_hdl_converter")
logger.setLevel(logging.INFO)
logger.propagate = False

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)

# -----------------------------------------------------------------------------
# App
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Fusion HCM HDL Converter",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Request models
# -----------------------------------------------------------------------------
class BatchRequest(BaseModel):
    folder: str

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def make_preview(df: pd.DataFrame, rows: int = 10):
    """
    Convert preview rows into JSON-safe records.
    Handles timestamps, dates, NaN, and numpy/pandas types safely.
    """
    preview_df = df.head(rows).copy()

    for col in preview_df.columns:
        if pd.api.types.is_datetime64_any_dtype(preview_df[col]):
            preview_df[col] = preview_df[col].dt.strftime("%Y-%m-%d")
        else:
            preview_df[col] = preview_df[col].apply(
                lambda x: x.strftime("%Y-%m-%d")
                if hasattr(x, "strftime")
                else (None if pd.isna(x) else x)
            )

    return jsonable_encoder(preview_df.to_dict(orient="records"))

# -----------------------------------------------------------------------------
# Middleware: request logging
# -----------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    client_host = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path

    logger.info(f"Incoming request | {method} {path} | client={client_host}")

    try:
        response = await call_next(request)
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.exception(
            f"Request failed | {method} {path} | client={client_host} | "
            f"elapsed={elapsed_ms:.2f}ms | error={exc}"
        )
        raise

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        f"Outgoing response | {method} {path} | "
        f"status={response.status_code} | elapsed={elapsed_ms:.2f}ms"
    )
    return response

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Fusion HCM HDL Converter API",
        "docs": "/docs",
        "health": "/health",
        "batch": "/batch",
        "upload": "/upload",
    }


@app.post("/batch")
async def batch_process(req: BatchRequest):
    try:
        folder = req.folder.strip()

        if not folder:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Missing required field: folder",
                    "errors": ["folder is required"],
                    "summary": None,
                },
            )

        # Use modern engine (process_folder) for /batch as the single pipeline.
        # It now includes the additional Fusion existence check via ObjectLookup.
        # Config is pulled centrally from services/config.py (FUSION_CONFIG).
        # Legacy orchestrator is no longer used for new batch requests.
        summary = process_folder(Path(folder))
        # CENTRAL SANITIZER: converts NaN→None, numpy→native, Timestamp→ISO, Path→str,
        # recurses into dataclasses/dicts/lists. Prevents JSON serialization failures
        # (HTTP 500) while preserving ALL validation details, row_values, issues, etc.
        # Applied immediately before JSONResponse per requirements. Covers /batch,
        # future /phase3/* endpoints, and any summary/download responses.
        summary = sanitize_for_json(summary)

        return JSONResponse(
            content={
                "status": "success",
                "message": "Batch processing completed successfully.",
                **jsonable_encoder(summary)
            }
        )

    except Exception as e:
        logger.exception(f"Unhandled error in /batch | error={e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Server error while running batch: {str(e)}",
                "errors": [str(e)],
                "summary": None,
            },
        )


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Upload received | filename={file.filename}")

    try:
        if not file.filename.lower().endswith((".xlsx", ".csv")):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Only .xlsx or .csv files are allowed!",
                    "errors": ["Invalid file type"],
                    "preview": [],
                    "hdl": "",
                    "stats": {"total": 0, "valid": 0, "errors": 1},
                },
            )

        content = await file.read()

        if not content:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Uploaded file is empty.",
                    "errors": ["No file content found"],
                    "preview": [],
                    "hdl": "",
                    "stats": {"total": 0, "valid": 0, "errors": 1},
                },
            )

        if file.filename.lower().endswith(".xlsx"):
            df = pd.read_excel(BytesIO(content))
        else:
            csv_content = StringIO(content.decode("utf-8"))
            df = pd.read_csv(csv_content)

        logger.info(f"File parsed | rows={len(df)} | cols={len(df.columns)}")

        df.columns = df.columns.str.strip()
        df.columns = [col.replace(" ", "") for col in df.columns]

        logger.info(f"Normalized columns: {list(df.columns)}")

        missing_cols = validate_columns(df)
        if missing_cols:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "validation_error",
                    "message": "Missing required columns",
                    "errors": [f"Missing columns: {', '.join(missing_cols)}"],
                    "preview": make_preview(df),
                    "hdl": "",
                    "stats": {
                        "total": len(df),
                        "valid": 0,
                        "errors": len(missing_cols),
                    },
                },
            )

        errors = validate_data(df)
        preview = make_preview(df)

        if errors:
            valid_count = max(0, len(df) - len(errors))
            return JSONResponse(
                status_code=400,
                content={
                    "status": "validation_error",
                    "message": "Validation errors found",
                    "errors": errors,
                    "preview": preview,
                    "hdl": "",
                    "stats": {
                        "total": len(df),
                        "valid": valid_count,
                        "errors": len(errors),
                    },
                },
            )

        hdl_content = generate_hdl(df)

        return JSONResponse(
            content={
                "status": "success",
                "message": "Validation successful!",
                "errors": [],
                "preview": preview,
                "hdl": hdl_content,
                "stats": {"total": len(df), "valid": len(df), "errors": 0},
            }
        )

    except UnicodeDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "CSV file could not be decoded. Please save it as UTF-8.",
                "errors": ["Unicode decode error"],
                "preview": [],
                "hdl": "",
                "stats": {"total": 0, "valid": 0, "errors": 1},
            },
        )

    except Exception as e:
        logger.exception(f"Unhandled error in /upload | error={e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Server error while processing file: {str(e)}",
                "errors": [str(e)],
                "preview": [],
                "hdl": "",
                "stats": {"total": 0, "valid": 0, "errors": 1},
            },
        )


@app.post("/download")
async def download(hdl: str = Form(...)):
    return StreamingResponse(
        iter([hdl.encode("utf-8")]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="worker.hdl.csv"'},
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    
# To run:
# uvicorn main:app --reload
# Visit http://127.0.0.1:8000/