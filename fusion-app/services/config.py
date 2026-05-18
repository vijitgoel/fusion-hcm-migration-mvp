from __future__ import annotations

import os

# services/config.py
# Configurable rules for validation (legacy/local rules - UNCHANGED per requirements)

REQUIRED_COLUMNS = ['EmployeeNumber', 'FirstName', 'LastName', 'HireDate']

VALIDATION_RULES = {
    "EmployeeNumber": {"required": True, "unique": True},
    "FirstName": {"required": True},
    "LastName": {"required": True},
    "HireDate": {"required": True, "type": "date"}
}


# =============================================================================
# CENTRALIZED FUSION HCM SAAS CONFIGURATION (SINGLE SOURCE OF TRUTH)
# =============================================================================
# All connection details, credentials, and per-object REST lookup mappings live
# here ONLY. No other file may hard-code Fusion URLs, usernames, passwords,
# or endpoints. This satisfies all design constraints.
#
# In production replace the defaults with environment variables or a secrets
# manager. The lookup_mappings are aligned with OBJECT_CATALOG.unique_columns
# from catalog.py but kept separate so catalog remains metadata-only.
#
# The new existence check (additional validation layer) will import this dict.

FUSION_CONFIG = {
    "base_url": os.getenv(
        "FUSION_BASE_URL", "https://your-fusion-instance.oraclecloud.com"
    ),
    "username": os.getenv("FUSION_USERNAME", "your.username@domain.com"),
    "password": os.getenv("FUSION_PASSWORD", "your_password"),
    "timeout_seconds": int(os.getenv("FUSION_TIMEOUT_SECONDS", "30")),
    "lookup_mappings": {
        "Worker": {
            "endpoint": "/hcmRestApi/resources/11.13.18.05/workers",
            "lookup_fields": ["PERSON_NUMBER"],
            "query_param": "q",
            "query_template": "PersonNumber={PERSON_NUMBER}",
            "success_key": "items",
            "exists_if_count_gt": 0,
        },
        "Location": {
            "endpoint": "/hcmRestApi/resources/11.13.18.05/locations",
            "lookup_fields": ["LOCATION_CODE", "SET_CODE"],
            "query_param": "q",
            "query_template": "LocationCode={LOCATION_CODE};SetCode={SET_CODE}",
            "success_key": "items",
            "exists_if_count_gt": 0,
        },
        "Organization": {
            "endpoint": "/hcmRestApi/resources/11.13.18.05/organizations",
            "lookup_fields": ["NAME", "SOURCE_SYSTEM_ID"],
            "query_param": "q",
            "query_template": "Name={NAME};SourceSystemId={SOURCE_SYSTEM_ID}",
            "success_key": "items",
            "exists_if_count_gt": 0,
        },
        "OrgUnitClassification": {
            "endpoint": "/hcmRestApi/resources/11.13.18.05/orgUnitClassifications",
            "lookup_fields": ["ORGANIZATION_NAME", "CLASSIFICATION_NAME"],
            "query_param": "q",
            "query_template": "OrganizationName={ORGANIZATION_NAME};ClassificationName={CLASSIFICATION_NAME}",
            "success_key": "items",
            "exists_if_count_gt": 0,
        },
    },
}