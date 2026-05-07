from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class FolderProcessRequest(BaseModel):
    folder_path: str = Field(..., description="Absolute path to the parent folder to scan")
    output_mode: Literal["flat", "mirrored"] = Field(
        default="flat",
        description="flat = single output folder, mirrored = preserve folder hierarchy",
    )


class Phase3RunSummaryRequest(BaseModel):
    run_id: str


class CatalogObjectOut(BaseModel):
    name: str
    aliases: list[str]
    required_columns: list[str]
    optional_columns: list[str]
    unique_columns: list[str]
    date_columns: list[str]
    output_header: str
    description: str
