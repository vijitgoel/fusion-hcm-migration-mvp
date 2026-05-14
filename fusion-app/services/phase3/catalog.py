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
        required_columns=["SOURCE_SYSTEM_OWNER", "SOURCE_SYSTEM_ID", "SET_CODE", "LOCATION_CODE", "EFFECTIVE_START_DATE" ], #by shalok
        #required_columns=["SOURCE_SYSTEM_OWNER", "SOURCE_SYSTEM_ID", "SET_CODE", "LOCATION_CODE", "LOCATION_NAME", "EFFECTIVE_START_DATE", "COUNTRY"],
        optional_columns=["CITY", "STATE", "STATUS","EFFECTIVE_END_DATE","ACTION_REASON_CODE","ACTIVE_STATUS","ADDRESS_LINE_1","ADDRESS_LINE_2","ADDRESS_LINE_3","COUNTRY","EMPLOYEE_LOCATION","FLOOR_NUMBER","LOCATION_NAME","REGION_1","REGION_2"], #by shalok
        #optional_columns=["CITY", "STATE", "STATUS"],
        unique_columns=["LOCATION_CODE", "SOURCE_SYSTEM_ID"],
        date_columns=["EFFECTIVE_START_DATE","EFFECTIVE_END_DATE"], #BY SHALOK
        #date_columns=["EFFECTIVE_START_DATE"],
        #column_aliases={
#           "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
#           "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
#           "SET_CODE": ["SetCode", "set_code"],
#           "LOCATION_CODE": ["LocationCode", "location_code"],
#           "COUNTRY": ["Country", "country"],
#           "CITY": ["City", "TownOrCity", "city", "town_or_city"],
#           "STATUS": ["Status", "ActiveStatus", "status", "active_status"],
#           "STATE": ["State", "Region1", "Province", "state", "region1", "province"],
#           "LOCATION_NAME": ["LocationName", "location_name"],
#           "EFFECTIVE_START_DATE": ["EffectiveStartDate", "effective_start_date"],
       #},
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "SET_CODE": ["SetCode", "set_code"],
            "LOCATION_CODE": ["LocationCode", "location_code"],
            "EFFECTIVE_START_DATE": ["EffectiveStartDate", "effective_start_date"],
            "CITY": ["City", "TownOrCity", "city", "town_or_city"],
            "STATE": ["State", "Province", "Region1", "state", "province", "region1"],
            "STATUS": ["Status", "status"],
            "EFFECTIVE_END_DATE": ["EffectiveEndDate", "effective_end_date"],
            "ACTION_REASON_CODE": ["ActionReasonCode", "action_reason_code"],
            "ACTIVE_STATUS": ["ActiveStatus", "active_status"],
            "ADDRESS_LINE_1": ["AddressLine1", "address_line_1"],
            "ADDRESS_LINE_2": ["AddressLine2", "address_line_2"],
            "ADDRESS_LINE_3": ["AddressLine3", "address_line_3"],
            "COUNTRY": ["Country", "country"],
            "EMPLOYEE_LOCATION": ["EmployeeLocation", "employee_location"],
            "FLOOR_NUMBER": ["FloorNumber", "floor_number"],
            "LOCATION_NAME": ["LocationName", "location_name"],
            "REGION_1": ["Region1", "region1"],
            "REGION_2": ["Region2", "region2"],
        },
#        validation_rules={
#            "SOURCE_SYSTEM_OWNER": {
#                "required": False,
#                "min_length": 1,
#                "max_length": 30,
#                "error_msg": "SOURCE_SYSTEM_OWNER must be 1-30 chars",
#            },
#            "SOURCE_SYSTEM_ID": {
#                "required": False,
#                "min_length": 1,
#                "max_length": 30,
#                "regex": r"^[A-Z0-9_-]+$",
#                "error_msg": "SOURCE_SYSTEM_ID must be alphanumeric with underscores/dashes, 1-30 chars if provided",
#            },
#            "SET_CODE": {
#                "required": True,
#                "min_length": 1,
#                "max_length": 30,
#                "regex": r"^[A-Z0-9_]+$",
#                "error_msg": "SET_CODE must be uppercase alphanumeric/underscore, 1-30 chars (e.g., COMMON)",
#            },
#            "LOCATION_CODE": {
#                "required": True,
#                "min_length": 1,
#                "max_length": 30,
#                "regex": r"^[A-Z0-9_-]+$",
#                "error_msg": "LOCATION_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
#            },
#            "LOCATION_NAME": {
#                "required": True,
#                "min_length": 1,
#                "max_length": 240,
#                "error_msg": "LOCATION_NAME must be 1-240 chars",
#            },
#            "EFFECTIVE_START_DATE": {
#                "required": True,
#                "data_type": "date",
#                "error_msg": "EFFECTIVE_START_DATE must be a valid date",
#            },
#            "COUNTRY": {
#                "required": True,
#                "min_length": 1,
#                "max_length": 240,
#                "error_msg": "COUNTRY must be 1-240 chars",
#            },
#            "STATUS": {
#                "required": True,
#                "regex": r"^[A]$|^I$",
#                "error_msg": "STATUS must be A (Active) or I (Inactive)",
#            },
#        },
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
               "error_msg": "SOURCE_SYSTEM_ID must be alphanumeric with underscores/dashes, 1-30 chars",
           },

          "SET_CODE": {
               "required": True,
               "min_length": 1,
               "max_length": 30,
               "regex": r"^[A-Z0-9_]+$",
               "error_msg": "SET_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
           },

           "LOCATION_CODE": {
               "required": True,
               "min_length": 1,
               "max_length": 30,
               "regex": r"^[A-Z0-9_-]+$",
               "error_msg": "LOCATION_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
            },

           "EFFECTIVE_START_DATE": {
               "required": True,
               "data_type": "date",
               "error_msg": "EFFECTIVE_START_DATE must be a valid date",
           },

           "CITY": {
               "required": False,
               "min_length": 1,
               "max_length": 60,
               "error_msg": "CITY must be 1-60 chars",
           },

           "STATE": {
               "required": False,
               "min_length": 1,
               "max_length": 60,
               "error_msg": "STATE must be 1-60 chars",
           },

           "STATUS": {
               "required": False,
               "regex": r"^[AI]$",
               "error_msg": "STATUS must be A (Active) or I (Inactive)",
           },

           "EFFECTIVE_END_DATE": {
               "required": False,
               "data_type": "date",
               "error_msg": "EFFECTIVE_END_DATE must be a valid date",
           },

           "ACTION_REASON_CODE": {
               "required": False,
               "min_length": 1,
               "max_length": 30,
               "regex": r"^[A-Z0-9_]+$",
               "error_msg": "ACTION_REASON_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
           },

           "ACTIVE_STATUS": {
               "required": False,
               "regex": r"^[AI]$",
               "error_msg": "ACTIVE_STATUS must be A (Active) or I (Inactive)",
           },

           "ADDRESS_LINE_1": {
               "required": False,
               "min_length": 1,
               "max_length": 240,
               "error_msg": "ADDRESS_LINE_1 must be 1-240 chars",
           },

           "ADDRESS_LINE_2": {
               "required": False,
               "min_length": 1,
               "max_length": 240,
               "error_msg": "ADDRESS_LINE_2 must be 1-240 chars",
           },

           "ADDRESS_LINE_3": {
               "required": False,
               "min_length": 1,
               "max_length": 240,
               "error_msg": "ADDRESS_LINE_3 must be 1-240 chars",
           },

           "COUNTRY": {
               "required": True,
               "min_length": 1,
               "max_length": 60,
               "error_msg": "COUNTRY must be 1-60 chars",
           },

           "EMPLOYEE_LOCATION": {
               "required": False,
               "regex": r"^[YN]$",
               "error_msg": "EMPLOYEE_LOCATION must be Y or N",
           },

           "FLOOR_NUMBER": {
               "required": False,
               "min_length": 1,
               "max_length": 30,
               "error_msg": "FLOOR_NUMBER must be 1-30 chars",
           },

           "LOCATION_NAME": {
               "required": True,
               "min_length": 1,
               "max_length": 240,
               "error_msg": "LOCATION_NAME must be 1-240 chars",
           },

           "REGION_1": {
               "required": False,
               "min_length": 1,
               "max_length": 120,
               "error_msg": "REGION_1 must be 1-120 chars",
           },

           "REGION_2": {
               "required": False,
               "min_length": 1,
               "max_length": 120,
               "error_msg": "REGION_2 must be 1-120 chars",
           },
       },
        default_source_system_owner = "HCMQA-001",
        default_source_system_id = "LOCATION_{row_index}",
        #output_filename_template="{source}_{name}.dat",
        output_filename_template="Location.dat",#we can hardcode the out file name template also like LOCATION.dat taaki koi kch bhi naam ho upload hone mai dikat na aaye.
        #output_filename_template="{name}.dat",
        #output_header="METADATA|Location|SOURCE_SYSTEM_OWNER|SOURCE_SYSTEM_ID|SET_CODE|LOCATION_CODE|LOCATION_NAME|EFFECTIVE_START_DATE|COUNTRY|CITY|STATE|STATUS",
        #output_template=(
        #    "MERGE|Location|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|{SET_CODE}|{LOCATION_CODE}|{LOCATION_NAME}|{EFFECTIVE_START_DATE}|"
        #    "{COUNTRY}|{CITY}|{STATE}|{STATUS}"
        output_header="METADATA|Location|SourceSystemOwner|SourceSystemId|SetCode|LocationCode|EffectiveStartDate|EffectiveEndDate|TownOrCity|ActionReasonCode|ActiveStatus|AddressLine1|AddressLine2|AddressLine3|Country|EmployeeLocationFlag|FloorNumber|LocationName|Region1|Region2",
        output_template=(
             "MERGE|Location|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|{SET_CODE}|{LOCATION_CODE}|"
             "{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}|{CITY}|"
             "{ACTION_REASON_CODE}|{ACTIVE_STATUS}|{ADDRESS_LINE_1}|{ADDRESS_LINE_2}|"
             "{ADDRESS_LINE_3}|{COUNTRY}|{EMPLOYEE_LOCATION}|{FLOOR_NUMBER}|"
             "{LOCATION_NAME}|{REGION_1}|{REGION_2}"
        ),
        #),
        description="Location object migration file.",
    ),
    "Organization": ObjectDefinition(
        name="Organization",
        aliases=["organization", "org", "organizations","Department","department"],
        required_columns=["SOURCE_SYSTEM_OWNER", "SOURCE_SYSTEM_ID", "NAME", "CLASSIFICATION_NAME","EFFECTIVE_START_DATE"],
        optional_columns=["EFFECTIVE_END_DATE","ACTION_REASON_CODE","ESTABLISHMENT_NAME","INTERNAL_ADDRESS_LINE", "LOCATION_CODE","LOCATION_SET_CODE","TITLE","GUID","SOURCE_REF_TABLE_NAME"],
        unique_columns=["NAME", "SOURCE_SYSTEM_ID"],
        date_columns=["EFFECTIVE_START_DATE","EFFECTIVE_END_DATE"],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "NAME": ["Name", "DepartmentName", "name", "department_name"],
            "CLASSIFICATION_NAME": ["ClassificationName", "classification_name"],
            "EFFECTIVE_START_DATE": ["EffectiveStartDate", "effective_start_date"],
            "EFFECTIVE_END_DATE": ["EffectiveEndDate", "EndDate", "effective_end_date", "end_date"],
            "ACTION_REASON_CODE": ["ActionReasonCode", "action_reason_code"],
            "ESTABLISHMENT_NAME": ["EstablishmentName", "establishment_name"],
            "INTERNAL_ADDRESS_LINE": ["InternalAddressLine", "internal_address_line"],
            "LOCATION_CODE": ["LocationCode", "location_code"],
            "LOCATION_SET_CODE": ["LocationSetCode", "location_set_code"],
            "TITLE": ["Title", "title"],
            "GUID": ["GUID", "guid"],
            "SOURCE_REF_TABLE_NAME": ["SourceRefTableName", "source_ref_table_name"],
        },
         validation_rules={
            "SOURCE_SYSTEM_OWNER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "SOURCE_SYSTEM_OWNER must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "SOURCE_SYSTEM_ID": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "SOURCE_SYSTEM_ID must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "CLASSIFICATION_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 80,
                "error_msg": "CLASSIFICATION_NAME must be 1-80 chars",
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
            "EFFECTIVE_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_END_DATE must be a valid date",
            },
            "ACTION_REASON_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ACTION_REASON_CODE must be uppercase alphanumeric/underscore, 1-30 chars"
            },
            "ESTABLISHMENT_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "ESTABLISHMENT_NAME must be 1-240 chars"
            },
            "INTERNAL_ADDRESS_LINE": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "INTERNAL_ADDRESS_LINE must be 1-240 chars"
            },
            "LOCATION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "LOCATION_CODE must be uppercase alphanumeric with underscores/dashes, 1-30 chars"
            },
            "LOCATION_SET_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "LOCATION_SET_CODE must be uppercase alphanumeric/underscore, 1-30 chars"
            },
            "TITLE": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "TITLE must be 1-240 chars"
            },
            "GUID": {
                "required": False,
                "regex": r"^[0-9a-fA-F-]{36}$",
                "error_msg": "GUID must be a valid UUID format"
            },
            "SOURCE_REF_TABLE_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 80,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "SOURCE_REF_TABLE_NAME must be uppercase alphanumeric/underscore, 1-80 chars"
            },

        }, 
        default_source_system_owner = "FUSION",
        default_source_system_id = "ORGANIZATION_{row_index}",
        output_filename_template="Organization.dat",
        output_header="METADATA|Organization|SourceSystemOwner|SourceSystemId|ActionReasonCode|ClassificationName|EffectiveStartDate|EffectiveEndDate|LocationCode|LocationSetCode|Name|SourceRefTableName|EstablishmentName|InternalAddressLine|Title|GUID",
        output_template=(
            "MERGE|Organization|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|"
            "{ACTION_REASON_CODE}|{CLASSIFICATION_NAME}|"
            "{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}|"
            "{LOCATION_CODE}|{LOCATION_SET_CODE}|"
            "{NAME}|{SOURCE_REF_TABLE_NAME}|"
            "{ESTABLISHMENT_NAME}|{INTERNAL_ADDRESS_LINE}"
            "{TITLE}|{GUID}"
        ),
        description="Organization  object migration file.",
    ),
"OrgUnitClassification": ObjectDefinition(
        name="OrgUnitClassification",
        aliases=["orgunitclassification", "org_unit_classification","org_classification"],
        required_columns=["SOURCE_SYSTEM_OWNER", "SOURCE_SYSTEM_ID", "ORGANIZATION_NAME", "CATEGORY_CODE", "CLASSIFICATION_NAME","EFFECTIVE_START_DATE","STATUS"],
        optional_columns=["EFFECTIVE_END_DATE","GUID","LEGISLATION_CODE","SET_CODE"],
        unique_columns=["NAME", "SOURCE_SYSTEM_ID"],
        date_columns=["EFFECTIVE_START_DATE","EFFECTIVE_END_DATE",],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "ORGANIZATION_NAME": ["OrganizationName", "organization_name", "name", "Name"],
            "CLASSIFICATION_NAME": ["ClassificationName", "classification_name"],
            "EFFECTIVE_START_DATE": ["EffectiveStartDate", "effective_start_date"],
            "EFFECTIVE_END_DATE": ["EffectiveEndDate", "EndDate", "effective_end_date", "end_date"],
            "CATEGORY_CODE": ["CategoryCode", "category_code"],
            "STATUS": ["Status", "status"],
            "LEGISLATION_CODE": ["LegislationCode", "legislation_code"],
            "SET_CODE": ["SetCode", "set_code"],
            "GUID": ["GUID", "guid"],
        },
         validation_rules={
            "SOURCE_SYSTEM_OWNER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex":  r"^[A-Z0-9_]+$",
                "error_msg": "SOURCE_SYSTEM_OWNER must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "SOURCE_SYSTEM_ID": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "SOURCE_SYSTEM_ID must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "ORGANIZATION_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "ORGANIZATION_NAME must be 1-240 chars",
            },
            "CATEGORY_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "CATEGORY_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date",
            },
            "EFFECTIVE_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_END_DATE must be a valid date",
            },
            "CLASSIFICATION_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 80,
                "error_msg": "CLASSIFICATION_NAME must be 1-80 chars"
            },
            "STATUS": {
                "required": True,
                "regex": r"^(A|I)$",
                "error_msg": "STATUS must be A (Active) or I (Inactive)"
            },
            "GUID": {
                "required": False,
                "regex": r"^[0-9a-fA-F-]{36}$",
                "error_msg": "GUID must be a valid UUID format"
            },
            "LEGISLATION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z]{2,30}$",
                "error_msg": "LEGISLATION_CODE must contain uppercase letters only, 2-30 chars"
            },
            "SET_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "SET_CODE must be uppercase alphanumeric/underscore, 1-30 chars"
            },
        }, 
        default_source_system_owner = "FUSION",
        default_source_system_id = "ORG_CLASSIFICATION_{row_index}",
        output_filename_template="Organization.dat",
        output_header="METADATA|OrganizationClassification|SourceSystemOwner|SourceSystemId|OrganizationName|ClassificationName|EffectiveStartDate|EffectiveEndDate|CategoryCode|Status|LegislationCode|SetCode|GUID",
        output_template=(
            "MERGE|OrgUnitClassification|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|"
            "{ORGANIZATION_NAME}|{CLASSIFICATION_NAME}|"
            "{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}|"
            "{CATEGORY_CODE}|{STATUS}|"
            "{LEGISLATION_CODE}|{SET_CODE}|"
            "{GUID}"
        ),
        description="OrgUnitClassification  object migration file.",
    ),
}


def get_object_catalog() -> Dict[str, ObjectDefinition]:
    return OBJECT_CATALOG