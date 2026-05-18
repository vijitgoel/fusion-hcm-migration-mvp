from __future__ import annotations

import base64
import logging
from typing import Any, Dict

import requests

from .config import FUSION_CONFIG

logger = logging.getLogger(__name__)


class FusionClient:
    """
    Reusable REST client for Oracle Fusion HCM SaaS.
    ALL connection details, credentials, and endpoints are pulled exclusively
    from the centralized FUSION_CONFIG in services/config.py.
    No hard-coded URLs, usernames, or passwords appear in this file or
    anywhere else in the lookup/validation logic.
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or FUSION_CONFIG
        self.base_url = self.config["base_url"].rstrip("/")
        self.username = self.config["username"]
        self.password = self.config["password"]
        self.timeout = self.config.get("timeout_seconds", 30)
        self.session = self._create_authenticated_session()

    def _create_authenticated_session(self) -> requests.Session:
        session = requests.Session()
        # Basic Auth for Fusion HCM REST (standard pattern)
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        session.headers.update(
            {
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        return session

    def check_exists(
        self, object_name: str, row_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform existence lookup for a given object and row.
        Returns a dict with:
            - exists: bool
            - message: str (user-facing)
            - lookup_success: bool
            - error: Optional[str]
        Lookup configuration is taken ONLY from FUSION_CONFIG["lookup_mappings"].
        """
        mapping = self.config.get("lookup_mappings", {}).get(object_name)
        if not mapping:
            return {
                "exists": False,
                "message": f"No lookup mapping configured for {object_name}",
                "lookup_success": False,
                "error": "No mapping",
            }

        endpoint = mapping["endpoint"]
        query_param = mapping["query_param"]
        template = mapping["query_template"]
        success_key = mapping["success_key"]
        exists_threshold = mapping.get("exists_if_count_gt", 0)

        # Build query by substituting values from row_data using the configured lookup_fields
        try:
            query_values = {
                field: row_data.get(field, "")
                for field in mapping.get("lookup_fields", [])
            }
            query_str = template.format(**query_values)
        except KeyError as e:
            err = f"Missing lookup field {e} for {object_name}"
            logger.warning(err)
            return {
                "exists": False,
                "message": err,
                "lookup_success": False,
                "error": str(e),
            }

        url = f"{self.base_url}{endpoint}?{query_param}={query_str}"

        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()

            count = len(data.get(success_key, []))
            exists = count > exists_threshold

            message = (
                f"Record already exists in Fusion ({count} match(es) found)"
                if exists
                else "Record does not exist in Fusion"
            )

            return {
                "exists": exists,
                "message": message,
                "lookup_success": True,
                "error": None,
                "count": count,
            }

        except requests.exceptions.RequestException as e:
            err_msg = f"Fusion lookup failed for {object_name}: {str(e)}"
            logger.error(err_msg, exc_info=True)
            return {
                "exists": False,
                "message": "Fusion lookup failed (treated as warning)",
                "lookup_success": False,
                "error": str(e),
            }
        except Exception as e:
            logger.exception("Unexpected error during Fusion lookup")
            return {
                "exists": False,
                "message": "Fusion lookup error",
                "lookup_success": False,
                "error": str(e),
            }