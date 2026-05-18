from __future__ import annotations

from typing import Any, Dict

from .config import FUSION_CONFIG
from .fusion_client import FusionClient
from .phase3.catalog import OBJECT_CATALOG


class ObjectLookup:
    """
    Modular lookup service.
    - Uses ONLY centralized FUSION_CONFIG for connection and endpoint mappings.
    - Uses OBJECT_CATALOG (catalog.py) for object metadata (unique_columns etc.).
    - No hard-coded URLs, credentials, or endpoints in business logic.
    - Returns lookup result that can be attached to ValidationIssue or RunResult.
    """

    def __init__(self):
        self.client = FusionClient(config=FUSION_CONFIG)
        self.catalog = OBJECT_CATALOG

    def check_record_exists(
        self, object_name: str, row_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Checks if a record already exists in Fusion HCM for the given object.
        Returns a standardized result dict that can be merged into validation results
        without breaking existing local validation, duplicate detection, or HDL flow.
        """
        if object_name not in self.catalog:
            return {
                "fusion_exists": False,
                "lookup_success": False,
                "message": f"Object {object_name} not in catalog",
                "status": "warning",
            }

        # Use catalog metadata to validate we have the expected unique fields
        definition = self.catalog[object_name]
        lookup_fields = FUSION_CONFIG.get("lookup_mappings", {}).get(object_name, {}).get(
            "lookup_fields", definition.unique_columns
        )

        missing_fields = [f for f in lookup_fields if f not in row_data or not row_data[f]]
        if missing_fields:
            return {
                "fusion_exists": False,
                "lookup_success": False,
                "message": f"Missing lookup fields for {object_name}: {missing_fields}",
                "status": "warning",
            }

        lookup_result = self.client.check_exists(object_name, row_data)

        return {
            "fusion_exists": lookup_result.get("exists", False),
            "lookup_success": lookup_result.get("lookup_success", False),
            "message": lookup_result.get("message", "Lookup completed"),
            "status": "success" if lookup_result.get("lookup_success") else "warning",
            "count": lookup_result.get("count"),
            "error": lookup_result.get("error"),
        }