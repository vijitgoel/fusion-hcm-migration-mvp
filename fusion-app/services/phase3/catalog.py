from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any

from .utils import canonical_column_name

SOURCE_SYSTEM_OWNER = "FUSION"
SOURCE_SYSTEM_ID = "FUSION"


@dataclass(frozen=True)
class ObjectDefinition:
    name: str
    aliases: List[str]
    required_columns: List[str]
    optional_columns: List[str] = field(default_factory=list)
    unique_columns: List[str] = field(default_factory=list)
    date_columns: List[str] = field(default_factory=list)
    column_aliases: Dict[str, List[str]] = field(default_factory=dict)
    validation_rules: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    default_source_system_owner: str = "FUSION"
    default_source_system_id: str = "FUSION"
    output_filename_template: str = "{source}_{name}.dat"
    output_header: str = ""
    output_template: str = ""
    description: str = ""

    @property
    def all_columns(self) -> List[str]:
        seen = []
        for col in [*self.required_columns, *self.optional_columns]:
            if col not in seen:
                seen.append(col)
        return seen

    @property
    def normalized_aliases(self) -> List[str]:
        return [canonical_column_name(alias) for alias in self.aliases]

    @property
    def normalized_columns(self) -> Dict[str, str]:
        return {canonical_column_name(col): col for col in self.all_columns}


OBJECT_CATALOG: Dict[str, ObjectDefinition] = {
    "Worker": ObjectDefinition(
        name="Worker",
        aliases=["worker", "workers", "emp", "employee", "person"],
        required_columns=["SOURCE_SYSTEM_OWNER", "SOURCE_SYSTEM_ID", "PERSON_NUMBER", "FIRST_NAME", "LAST_NAME", "START_DATE"],
        optional_columns=["EMAIL", "BUSINESS_UNIT", "DEPARTMENT", "LOCATION", "NATIONALITY"],
        unique_columns=["PERSON_NUMBER", "SOURCE_SYSTEM_ID"],
        date_columns=["START_DATE"],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "PERSON_NUMBER": ["PersonNumber", "EmployeeNumber", "person_number", "employee_number"],
            "START_DATE": ["StartDate", "HireDate", "start_date", "hire_date"],
            "DEPARTMENT": ["Department", "DepartmentCode", "DeptCode", "department", "department_code"],
            "BUSINESS_UNIT": ["BusinessUnit", "BU", "business_unit"],
            "LOCATION": ["Location", "LocCode", "location", "loc_code"],
            "NATIONALITY": ["Nationality", "Country", "nationality", "country"],
            "EMAIL": ["Email", "email"],
            "FIRST_NAME": ["FirstName", "first_name"],
            "LAST_NAME": ["LastName", "last_name"],
        },
        validation_rules={
            "SOURCE_SYSTEM_OWNER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SOURCE_SYSTEM_OWNER must be 1-30 chars",
            },
            "SOURCE_SYSTEM_ID": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "SOURCE_SYSTEM_ID must be alphanumeric with underscores/dashes, 1-30 chars if provided",
            },
            "PERSON_NUMBER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "PERSON_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "FIRST_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 50,
                "regex": r"^[A-Za-z\s]+$",
                "error_msg": "FIRST_NAME must contain only letters and spaces, 1-50 chars",
            },
            "LAST_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 50,
                "regex": r"^[A-Za-z\s]+$",
                "error_msg": "LAST_NAME must contain only letters and spaces, 1-50 chars",
            },
            "START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "START_DATE must be a valid date",
            },
            "EMAIL": {
                "required": False,
                "regex": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "error_msg": "EMAIL must be a valid email address",
            },
        },
        default_source_system_owner = "FUSION",
        default_source_system_id = "FUSION_WORKER_ROW_{row_index}",
        output_filename_template="{source}_{name}.dat",
        output_header="METADATA|Worker|SOURCE_SYSTEM_OWNER|SOURCE_SYSTEM_ID|PERSON_NUMBER|FIRST_NAME|LAST_NAME|START_DATE|EMAIL|BUSINESS_UNIT|DEPARTMENT|LOCATION|NATIONALITY",
        output_template=(
            "MERGE|Worker|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|{PERSON_NUMBER}|{FIRST_NAME}|{LAST_NAME}|{START_DATE}|"
            "{EMAIL}|{BUSINESS_UNIT}|{DEPARTMENT}|{LOCATION}|{NATIONALITY}"
        ),
        description="Worker object migration file.",
    ),
    "Location": ObjectDefinition(
        name="Location",
        aliases=["location", "locations", "site", "office"],
        required_columns=["SOURCE_SYSTEM_OWNER", "SOURCE_SYSTEM_ID", "SET_CODE", "LOCATION_CODE", "LOCATION_NAME", "EFFECTIVE_START_DATE", "COUNTRY"],
        optional_columns=["CITY", "STATE", "STATUS"],
        unique_columns=["LOCATION_CODE", "SOURCE_SYSTEM_ID"],
        date_columns=["EFFECTIVE_START_DATE"],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "SET_CODE": ["SetCode", "set_code"],
            "LOCATION_CODE": ["LocationCode", "location_code"],
            "COUNTRY": ["Country", "country"],
            "CITY": ["City", "TownOrCity", "city", "town_or_city"],
            "STATUS": ["Status", "ActiveStatus", "status", "active_status"],
            "STATE": ["State", "Region1", "Province", "state", "region1", "province"],
            "LOCATION_NAME": ["LocationName", "location_name"],
            "EFFECTIVE_START_DATE": ["EffectiveStartDate", "effective_start_date"],
        },
        validation_rules={
            "SOURCE_SYSTEM_OWNER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SOURCE_SYSTEM_OWNER must be 1-30 chars",
            },
            "SOURCE_SYSTEM_ID": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "SOURCE_SYSTEM_ID must be alphanumeric with underscores/dashes, 1-30 chars if provided",
            },
            "SET_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "SET_CODE must be uppercase alphanumeric/underscore, 1-30 chars (e.g., COMMON)",
            },
            "LOCATION_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "LOCATION_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "LOCATION_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "LOCATION_NAME must be 1-240 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date",
            },
            "COUNTRY": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "COUNTRY must be 1-240 chars",
            },
            "STATUS": {
                "required": True,
                "regex": r"^[A]$|^I$",
                "error_msg": "STATUS must be A (Active) or I (Inactive)",
            },
        },
        default_source_system_owner = "FUSION",
        default_source_system_id = "FUSION_LOCATION_ROW_{row_index}",
        output_filename_template="{source}_{name}.dat",
        output_header="METADATA|Location|SOURCE_SYSTEM_OWNER|SOURCE_SYSTEM_ID|SET_CODE|LOCATION_CODE|LOCATION_NAME|EFFECTIVE_START_DATE|COUNTRY|CITY|STATE|STATUS",
        output_template=(
            "MERGE|Location|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|{SET_CODE}|{LOCATION_CODE}|{LOCATION_NAME}|{EFFECTIVE_START_DATE}|"
            "{COUNTRY}|{CITY}|{STATE}|{STATUS}"
        ),
        description="Location object migration file.",
    ),
    "Department": ObjectDefinition(
        name="Department",
        aliases=["department", "dept", "departments"],
        required_columns=["SOURCE_SYSTEM_OWNER", "SOURCE_SYSTEM_ID", "DEPARTMENT_CODE", "DEPARTMENT_NAME", "EFFECTIVE_START_DATE"],
        optional_columns=["MANAGER", "BUSINESS_UNIT", "STATUS"],
        unique_columns=["DEPARTMENT_CODE", "SOURCE_SYSTEM_ID"],
        date_columns=["EFFECTIVE_START_DATE"],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "DEPARTMENT_CODE": ["DepartmentCode", "Code", "ClassificationCode", "department_code", "code", "classification_code"],
            "DEPARTMENT_NAME": ["DepartmentName", "Name", "DeptName", "department_name", "name", "dept_name"],
            "EFFECTIVE_START_DATE": ["EffectiveStartDate", "StartDate", "effective_start_date", "start_date"],
            "MANAGER": ["Manager", "manager"],
            "BUSINESS_UNIT": ["BusinessUnit", "BU", "business_unit"],
            "STATUS": ["Status", "ActiveStatus", "status", "active_status"],
        },
        validation_rules={
            "SOURCE_SYSTEM_OWNER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SOURCE_SYSTEM_OWNER must be 1-30 chars",
            },
            "SOURCE_SYSTEM_ID": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "SOURCE_SYSTEM_ID must be alphanumeric with underscores/dashes, 1-30 chars if provided",
            },
            "DEPARTMENT_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "DEPARTMENT_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "DEPARTMENT_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "DEPARTMENT_NAME must be 1-240 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date",
            },
            "STATUS": {
                "required": False,
                "regex": r"^[A]$|^I$",
                "error_msg": "STATUS must be A (Active) or I (Inactive)",
            },
        },
        default_source_system_owner = "FUSION",
        default_source_system_id = "FUSION_DEPARTMENT_ROW_{row_index}",
        output_filename_template="{source}_{name}.dat",
        output_header="METADATA|Department|SOURCE_SYSTEM_OWNER|SOURCE_SYSTEM_ID|DEPARTMENT_CODE|DEPARTMENT_NAME|EFFECTIVE_START_DATE|MANAGER|BUSINESS_UNIT|STATUS",
        output_template=(
            "MERGE|Department|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|{DEPARTMENT_CODE}|{DEPARTMENT_NAME}|{EFFECTIVE_START_DATE}|"
            "{MANAGER}|{BUSINESS_UNIT}|{STATUS}"
        ),
        description="Department object migration file.",
    ),
}


def get_object_catalog() -> Dict[str, ObjectDefinition]:
    return OBJECT_CATALOG