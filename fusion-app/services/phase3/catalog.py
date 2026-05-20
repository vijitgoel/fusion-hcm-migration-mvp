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
    "Grade": ObjectDefinition(
        name="Grade",
        aliases=["grade", "grades", "pay grade", "pay_grade"],
        required_columns=["SOURCE_SYSTEM_OWNER", "SOURCE_SYSTEM_ID", "SET_CODE", "GRADE_CODE", "GRADE_NAME","EFFECTIVE_START_DATE"],
        optional_columns=["EFFECTIVE_END_DATE","ACTIVE_STATUS","CATEGORY_CODE","CEILING_STEP","ACTION_REASON_CODE"],
        unique_columns=["GRADE_CODE", "SOURCE_SYSTEM_ID","SET_CODE", "SOURCE_SYSTEM_ID"],
        date_columns=["EFFECTIVE_START_DATE","EFFECTIVE_END_DATE"],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "SET_CODE": ["SetCode", "set_code"],
            "GRADE_CODE": ["GradeCode", "Code","grade_code","code"],
            "EFFECTIVE_START_DATE": ["EffectiveStartDate", "effective_start_date","StartDate","start_date"],
            "EFFECTIVE_END_DATE": ["EffectiveEndDate", "EndDate", "effective_end_date", "end_date"],
            "GRADE_LADDER_NAME": ["GradeLadderName", "grade_ladder_name"],
            "CEILING_STEP": ["CeilingStep", "ceiling_step"],
            "ACTION_REASON_CODE": ["ActionReasonCode", "actionreasoncode","action_reason_code","Action_Reason_Code","ActionReason_Code"],
            "CATEGORY_CODE": ["CategoryCode", "category_code"],
    
        },
         validation_rules={
            "SOURCE_SYSTEM_OWNER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex":  r"^[A-Z0-9_]+$",
                "error_msg": "SOURCE_SYSTEM_OWNER must be uppercase alphanumeric/underscore, 1-30 chars",
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
                "max_length": 240,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "GRADE_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "GRADE_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "GRADE_NAME must be 1-240 chars",
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
            "ACTIVE_STATUS": {
                "required": False,
                "regex": r"^[AI]$",
                "error_msg": "ACTIVE_STATUS must be A (Active) or I (Inactive)"
            },
            "CATEGORY_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 80,
                "error_msg": "CATEGORY_CODE must be GRADE_LEG — this is the EFF category code"
            },
            "CEILING_STEP": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "CEILING_STEP must be 1-30 chars"
            },
            "ACTION_REASON_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ACTION_REASON_CODE must be uppercase alphanumeric/underscore, 1-30 chars"
            },
        }, 
        default_source_system_owner = "HCMQA-001",
        default_source_system_id = "GRADE_{row_index}",
        output_filename_template="Grade.dat",
        output_header="METADATA|Grade|SourceSystemOwner|SourceSystemId|EffectiveStartDate|EffectiveEndDate|SetCode|GradeCode|GradeName|ActiveStatus|GradeLadderName|CeilingStep|ActionReasonCode|CategoryCode",
        output_template=(
            "MERGE|Grade|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|"
            "{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}|"
            "{SET_CODE}|{GRADE_CODE}|"
            "{GRADE_NAME}|{ACTIVE_STATUS}|"
            "{GRADE_LADDER_NAME}|{CEILING_STEP}|"
            "{ACTION_REASON_CODE}|{CATEGORY_CODE}"
        ),
        description="Grade object migration file for Oracle Fusion HCM Workforce Structures.",
    ),

    "GradeRate": ObjectDefinition( # type: ignore
        name="GradeRate",
        aliases=["grade rate", "graderate", "grade_rate", "salary rate", "pay rate"],
        required_columns=[
            "SOURCE_SYSTEM_OWNER",
            "SOURCE_SYSTEM_ID",
            "GRADE_RATE_NAME",
            "RATE_TYPE",
            "LEGISLATIVE_DATA_GROUP",
            "EFFECTIVE_START_DATE",
            "GRADE_CODE",              
        ],
        optional_columns=[
            "EFFECTIVE_END_DATE",
            "CURRENCY_CODE",
            "RATE_FREQUENCY",
            "ANNUALIZATION_FACTOR",
            "ACTIVE_STATUS",
            "ACTION_REASON_CODE",      
            "GRADE_LADDER_NAME",       
            "PROGRESSION_RATE_FLAG",     
            "GRADE_RATE_VALUE_SOURCE_SYSTEM_OWNER",
            "GRADE_RATE_VALUE_SOURCE_SYSTEM_ID",
            "RATE_ID",
            "RATE_OBJECT_ID",
            "MINIMUM_AMOUNT",
            "MAXIMUM_AMOUNT",
            "MID_VALUE_AMOUNT",
            "VALUE_AMOUNT",
        ],
        unique_columns=["GRADE_RATE_NAME", "LEGISLATIVE_DATA_GROUP", "SOURCE_SYSTEM_ID"],
        date_columns=["EFFECTIVE_START_DATE", "EFFECTIVE_END_DATE"],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "GRADE_RATE_NAME": [
                "GradeRateName", "RateName",
                "grade_rate_name", "rate_name",
            ],
            "RATE_TYPE": [
                "RateType", "rate_type",
                # 🔧 BUG FIXED: "grade_code" and "code" were wrongly placed here — removed
            ],
            "LEGISLATIVE_DATA_GROUP": [
                "LegislativeDataGroup", "LDG",
                "legislative_data_group", "ldg",
            ],
            "EFFECTIVE_START_DATE": [
                "EffectiveStartDate", "StartDate",
                "effective_start_date", "start_date",
            ],
            "EFFECTIVE_END_DATE": [
                "EffectiveEndDate", "EndDate",
                "effective_end_date", "end_date",
            ],
            "GRADE_CODE": [                          
                "GradeCode", "Grade", "Code",
                "grade_code", "grade", "code",
            ],
            "CURRENCY_CODE": [
                "CurrencyCode", "Currency",
                "currency_code", "currency",
            ],
            "RATE_FREQUENCY": [
                "RateFrequency", "Frequency",
                "rate_frequency", "frequency",
                
            ],
            "ANNUALIZATION_FACTOR": [
                "AnnualizationFactor", "annualization_factor",
            ],
            "ACTIVE_STATUS": [
                "ActiveStatus", "Status",
                "active_status", "status",
            ],
            "ACTION_REASON_CODE": [                  
                "ActionReasonCode", "ActionReason",
                "action_reason_code", "action_reason",
            ],
            "GRADE_LADDER_NAME": [                   
                "GradeLadderName", "LadderName",
                "grade_ladder_name", "ladder_name",
            ],
            "PROGRESSION_RATE_FLAG": [               
                "ProgressionRateFlag", "progression_rate_flag",
            ],
            "GRADE_RATE_VALUE_SOURCE_SYSTEM_OWNER": [
                "GradeRateValueSourceSystemOwner",
                "grade_rate_value_source_system_owner",
            ],
            "GRADE_RATE_VALUE_SOURCE_SYSTEM_ID": [
                "GradeRateValueSourceSystemId",
                "grade_rate_value_source_system_id",
            ],
            "RATE_ID": ["RateId", "rate_id"],
            "RATE_OBJECT_ID": [
                "RateObjectId", "GradeId",
                "rate_object_id", "grade_id",
            ],
            "MINIMUM_AMOUNT": [
                "MinimumAmount", "MinAmount",
                "minimum_amount", "min_amount",
            ],
            "MAXIMUM_AMOUNT": [
                "MaximumAmount", "MaxAmount",
                "maximum_amount", "max_amount",
            ],

            "MID_VALUE_AMOUNT": [
                "MidValueAmount", "MidpointAmount",
                "mid_value_amount", "midpoint_amount",
            ],
            "VALUE_AMOUNT": ["ValueAmount", "value_amount"],
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
            "GRADE_RATE_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "GRADE_RATE_NAME must be 1-240 chars",
            },
            "RATE_TYPE": {
                "required": True,
                "allowed_values": ["SALARY", "BONUS", "OVERTIME"],
                "error_msg": "RATE_TYPE must be SALARY, BONUS, or OVERTIME",
            },
            "LEGISLATIVE_DATA_GROUP": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "LEGISLATIVE_DATA_GROUP must be 1-240 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date (YYYY/MM/DD)",
            },
            "EFFECTIVE_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_END_DATE must be a valid date (YYYY/MM/DD)",
            },
            "GRADE_CODE": {                          
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "GRADE_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "CURRENCY_CODE": {
                "required": False,
                "min_length": 3,
                "max_length": 3,
                "regex": r"^[A-Z]{3}$",
                "error_msg": "CURRENCY_CODE must be a 3-letter ISO currency code (e.g. USD, INR)",
            },
            "RATE_FREQUENCY": {
                "required": False,
                "allowed_values": ["ANNUAL", "MONTHLY", "WEEKLY", "HOURLY", "DAILY"],
                "error_msg": "RATE_FREQUENCY must be ANNUAL, MONTHLY, WEEKLY, HOURLY, or DAILY",
            },
            "ANNUALIZATION_FACTOR": {
                
                "required": False,
                
                "data_type": "decimal",
                "error_msg": "ANNUALIZATION_FACTOR must be a numeric value (e.g. 1.00000)",
            },
            "ACTIVE_STATUS": {
                "required": False,
                "regex": r"^[AI]$",
                "error_msg": "ACTIVE_STATUS must be A (Active) or I (Inactive)",
            },
            "ACTION_REASON_CODE": {                  
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ACTION_REASON_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "GRADE_LADDER_NAME": {                   
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "GRADE_LADDER_NAME must be 1-240 chars",
            },
            "PROGRESSION_RATE_FLAG": {               
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "PROGRESSION_RATE_FLAG must be Y or N",
            },
            "MINIMUM_AMOUNT": {
                "required": False,
                "data_type": "decimal",
                "error_msg": "MINIMUM_AMOUNT must be a numeric value",
            },
            "MAXIMUM_AMOUNT": {
                "required": False,
                "data_type": "decimal",
                "error_msg": "MAXIMUM_AMOUNT must be a numeric value",
            },
            "MID_VALUE_AMOUNT": {
                "required": False,
                "data_type": "decimal",
                "error_msg": "MID_VALUE_AMOUNT must be a numeric value",
            },
            "VALUE_AMOUNT": {
                "required": False,
                "data_type": "decimal",
                "error_msg": "VALUE_AMOUNT must be a numeric value",
            },
        },
        default_source_system_owner="HCMQA-001",
        default_source_system_id="GRADE_RATE_{row_index}",
        output_filename_template="GradeRate.dat",
        output_header=(
            "METADATA|GradeRate|SourceSystemOwner|SourceSystemId"
            "|EffectiveStartDate|EffectiveEndDate"
            "|LegislativeDataGroup|RateType|GradeRateName"
            "|CurrencyCode|RateFrequency|AnnualizationFactor|ActiveStatus"
            "|ActionReasonCode|GradeLadderName|ProgressionRateFlag"  
            "\nMETADATA|GradeRateValue|SourceSystemOwner|SourceSystemId"
            "|EffectiveStartDate|EffectiveEndDate"
            "|RateId(SourceSystemId)|RateObjectId(SourceSystemId)"
            "|GradeCode|LegislativeDataGroup"                        
            "|MinimumAmount|MaximumAmount|MidValueAmount|ValueAmount"
        ),
        output_template=(
            "MERGE|GradeRate|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}"
            "|{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}"
            "|{LEGISLATIVE_DATA_GROUP}|{RATE_TYPE}|{GRADE_RATE_NAME}"
            "|{CURRENCY_CODE}|{RATE_FREQUENCY}|{ANNUALIZATION_FACTOR}|{ACTIVE_STATUS}"
            "|{ACTION_REASON_CODE}|{GRADE_LADDER_NAME}|{PROGRESSION_RATE_FLAG}"  
            "\nMERGE|GradeRateValue|{GRADE_RATE_VALUE_SOURCE_SYSTEM_OWNER}|{GRADE_RATE_VALUE_SOURCE_SYSTEM_ID}"
            "|{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}"
            "|{RATE_ID}|{RATE_OBJECT_ID}"
            "|{GRADE_CODE}|{LEGISLATIVE_DATA_GROUP}"                 
            "|{MINIMUM_AMOUNT}|{MAXIMUM_AMOUNT}|{MID_VALUE_AMOUNT}|{VALUE_AMOUNT}"
        ),
        description="GradeRate object migration file. Includes GradeRateValue child record for min/max/midpoint/value amounts. GradeCode links the rate value to a specific grade.",
    ),

    "Job": ObjectDefinition(  # type: ignore
        name="Job",
        aliases=["job", "jobs", "role", "roles"],
        required_columns=[
            "JOB_CODE",
            "SET_CODE",
            "EFFECTIVE_START_DATE",
            "SOURCE_SYSTEM_OWNER",
            "SOURCE_SYSTEM_ID",
            "ACTIVE_STATUS",
            "NAME",
        ],
        optional_columns=[
            "JOB_SUB_FAMILY",
            "FULL_PART_TIME",
            "JOB_FUNCTION_CODE",
            "MANAGER_LEVEL",
            "MEDICAL_CHECKUP_REQUIRED",
            "STANDARD_WORKING_HOURS",
            "STANDARD_WORKING_FREQUENCY",
            "STANDARD_ANNUAL_WORKING_DURATION",
            "ANNUAL_WORKING_DURATION_UNITS",
            "REGULAR_TEMPORARY",
            "EFFECTIVE_END_DATE",
            "APPROVAL_AUTHORITY",
            "SCHEDULING_GROUP",
            "BENCHMARK_JOB_CODE",
            "PROGRESSION_JOB_CODE",
            "JOB_FAMILY_NAME",
            "JOB_FAMILY_CODE",
            "ACTION_REASON_CODE",
            "CATEGORY_CODE",
            "GRADE_LADDER_NAME",
        ],
        unique_columns=["JOB_CODE", "SOURCE_SYSTEM_ID"],
        date_columns=[
            "EFFECTIVE_START_DATE",
            "EFFECTIVE_END_DATE",
        ],
        column_aliases={
            "JOB_CODE": ["JobCode", "job_code", "Code", "code"],
            "SET_CODE": ["SetCode", "set_code"],
            "EFFECTIVE_START_DATE": [
                "EffectiveStartDate", "StartDate",
                "effective_start_date", "start_date",
            ],
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "ACTIVE_STATUS": [
                "ActiveStatus", "Status",
                "active_status", "status",
            ],
            "NAME": [
                "Name", "JobName", "Title",
                "name", "job_name", "title",
            ],
            "JOB_SUB_FAMILY": ["JobSubFamily", "job_sub_family"],
            "FULL_PART_TIME": ["FullPartTime", "full_part_time"],
            "JOB_FUNCTION_CODE": [
                "JobFunctionCode", "FunctionCode",
                "job_function_code", "function_code",
            ],
            "MANAGER_LEVEL": ["ManagerLevel", "manager_level"],
            "MEDICAL_CHECKUP_REQUIRED": ["MedicalCheckupRequired", "medical_checkup_required"],
            "STANDARD_WORKING_HOURS": [
                "StandardWorkingHours", "WorkingHours",
                "standard_working_hours", "working_hours",
            ],
            "STANDARD_WORKING_FREQUENCY": [
                "StandardWorkingFrequency", "WorkingFrequency",
                "standard_working_frequency", "working_frequency",
            ],
            "STANDARD_ANNUAL_WORKING_DURATION": [
                "StandardAnnualWorkingDuration", "standard_annual_working_duration",
            ],
            "ANNUAL_WORKING_DURATION_UNITS": [
                "AnnualWorkingDurationUnits", "annual_working_duration_units",
            ],
            "REGULAR_TEMPORARY": ["RegularTemporary", "regular_temporary"],
            "EFFECTIVE_END_DATE": [
                "EffectiveEndDate", "EndDate",
                "effective_end_date", "end_date",
            ],
            "APPROVAL_AUTHORITY": ["ApprovalAuthority", "approval_authority"],
            "SCHEDULING_GROUP": ["SchedulingGroup", "scheduling_group"],
            "BENCHMARK_JOB_CODE": ["BenchmarkJobCode", "benchmark_job_code"],
            "PROGRESSION_JOB_CODE": ["ProgressionJobCode", "progression_job_code"],
            "JOB_FAMILY_NAME": ["JobFamilyName", "job_family_name"],
            "JOB_FAMILY_CODE": [
                "JobFamilyCode", "FamilyCode",
                "job_family_code", "family_code",
            ],
            "ACTION_REASON_CODE": ["ActionReasonCode", "action_reason_code"],
            "CATEGORY_CODE": ["CategoryCode", "category_code"],
            "GRADE_LADDER_NAME": ["GradeLadderName", "grade_ladder_name"],
        },
        validation_rules={
            "JOB_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "JOB_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "SET_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "SET_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date (YYYY/MM/DD)",
            },
            "SOURCE_SYSTEM_OWNER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SOURCE_SYSTEM_OWNER must be 1-30 chars",
            },
            "SOURCE_SYSTEM_ID": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "SOURCE_SYSTEM_ID must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "ACTIVE_STATUS": {
                "required": True,
                "regex": r"^[AI]$",
                "error_msg": "ACTIVE_STATUS must be A (Active) or I (Inactive)",
            },
            "NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "NAME (Job Name) must be 1-240 chars",
            },
            "JOB_SUB_FAMILY": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "JOB_SUB_FAMILY must be 1-30 chars",
            },
            "FULL_PART_TIME": {
                "required": False,
                "allowed_values": ["FULL_TIME", "PART_TIME"],
                "error_msg": "FULL_PART_TIME must be FULL_TIME or PART_TIME",
            },
            "JOB_FUNCTION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "JOB_FUNCTION_CODE must be 1-30 chars",
            },
            "MANAGER_LEVEL": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "MANAGER_LEVEL must be 1-30 chars",
            },
            "MEDICAL_CHECKUP_REQUIRED": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "MEDICAL_CHECKUP_REQUIRED must be Y or N",
            },
            "STANDARD_WORKING_HOURS": {
                "required": False,
                "data_type": "decimal",
                "error_msg": "STANDARD_WORKING_HOURS must be a numeric value",
            },
            "STANDARD_WORKING_FREQUENCY": {
                "required": False,
                "allowed_values": ["W", "M", "Y"],
                "error_msg": "STANDARD_WORKING_FREQUENCY must be W (Weekly), M (Monthly), or Y (Yearly)",
            },
            "STANDARD_ANNUAL_WORKING_DURATION": {
                "required": False,
                "data_type": "decimal",
                "error_msg": "STANDARD_ANNUAL_WORKING_DURATION must be a numeric value",
            },
            "ANNUAL_WORKING_DURATION_UNITS": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "ANNUAL_WORKING_DURATION_UNITS must be 1-30 chars",
            },
            "REGULAR_TEMPORARY": {
                "required": False,
                "allowed_values": ["R", "T"],
                "error_msg": "REGULAR_TEMPORARY must be R (Regular) or T (Temporary)",
            },
            "EFFECTIVE_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_END_DATE must be a valid date (YYYY/MM/DD)",
            },
            "APPROVAL_AUTHORITY": {
                "required": False,
                "data_type": "integer",
                "error_msg": "APPROVAL_AUTHORITY must be a numeric value",
            },
            "SCHEDULING_GROUP": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SCHEDULING_GROUP must be 1-30 chars",
            },
            "BENCHMARK_JOB_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "BENCHMARK_JOB_CODE must be 1-30 chars",
            },
            "PROGRESSION_JOB_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "PROGRESSION_JOB_CODE must be 1-30 chars",
            },
            "JOB_FAMILY_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "JOB_FAMILY_NAME must be 1-240 chars",
            },
            "JOB_FAMILY_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "JOB_FAMILY_CODE must be 1-30 chars",
            },
            "ACTION_REASON_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ACTION_REASON_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "CATEGORY_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "CATEGORY_CODE must be 1-30 chars",
            },
            "GRADE_LADDER_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "GRADE_LADDER_NAME must be 1-240 chars",
            },
        },
        default_source_system_owner="HCMQA-001",
        default_source_system_id="JOB_{row_index}",
        output_filename_template="Job.dat",
        output_header=(
            "METADATA|Job|SourceSystemOwner|SourceSystemId"
            "|EffectiveStartDate|EffectiveEndDate"
            "|SetCode|JobCode|Name|ActiveStatus|JobSubFamily|FullPartTime"
            "|JobFunctionCode|ManagerLevel|MedicalCheckupRequired"
            "|StandardWorkingHours|StandardWorkingFrequency"
            "|StandardAnnualWorkingDuration|AnnualWorkingDurationUnits"
            "|RegularTemporary|ApprovalAuthority|SchedulingGroup"
            "|BenchmarkJobCode|ProgressionJobCode"
            "|JobFamilyName|JobFamilyCode|ActionReasonCode|CategoryCode|GradeLadderName"
        ),
        output_template=(
            "MERGE|Job|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}"
            "|{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}"
            "|{SET_CODE}|{JOB_CODE}|{NAME}|{ACTIVE_STATUS}|{JOB_SUB_FAMILY}|{FULL_PART_TIME}"
            "|{JOB_FUNCTION_CODE}|{MANAGER_LEVEL}|{MEDICAL_CHECKUP_REQUIRED}"
            "|{STANDARD_WORKING_HOURS}|{STANDARD_WORKING_FREQUENCY}"
            "|{STANDARD_ANNUAL_WORKING_DURATION}|{ANNUAL_WORKING_DURATION_UNITS}"
            "|{REGULAR_TEMPORARY}|{APPROVAL_AUTHORITY}|{SCHEDULING_GROUP}"
            "|{BENCHMARK_JOB_CODE}|{PROGRESSION_JOB_CODE}"
            "|{JOB_FAMILY_NAME}|{JOB_FAMILY_CODE}|{ACTION_REASON_CODE}|{CATEGORY_CODE}|{GRADE_LADDER_NAME}"
        ),
        description="Job object migration file. Loads job definitions into Oracle Fusion HCM. Must load JobFamily.dat first if JOB_FAMILY_CODE or JOB_FAMILY_NAME is used.",
    ),

    "JobFamily": ObjectDefinition(  # type: ignore
        name="JobFamily",
        aliases=["job family", "jobfamily", "job_family", "family"],
        required_columns=[
            "JOB_FAMILY_CODE",
            "JOB_FAMILY_NAME",
            "EFFECTIVE_START_DATE",
            "ACTIVE_STATUS",
            "SOURCE_SYSTEM_OWNER",
            "SOURCE_SYSTEM_ID",
        ],
        optional_columns=[
            "ACTION_REASON_CODE",
            "EFFECTIVE_END_DATE",
        ],
        unique_columns=["JOB_FAMILY_CODE", "SOURCE_SYSTEM_ID"],
        date_columns=[
            "EFFECTIVE_START_DATE",
            "EFFECTIVE_END_DATE",
        ],
        column_aliases={
            "JOB_FAMILY_CODE": [
                "JobFamilyCode", "FamilyCode",
                "job_family_code", "family_code",
            ],
            "JOB_FAMILY_NAME": [
                "JobFamilyName", "FamilyName",
                "job_family_name", "family_name",
            ],
            "EFFECTIVE_START_DATE": [
                "EffectiveStartDate", "StartDate",
                "effective_start_date", "start_date",
            ],
            "ACTIVE_STATUS": [
                "ActiveStatus", "Status",
                "active_status", "status",
            ],
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "ACTION_REASON_CODE": ["ActionReasonCode", "action_reason_code"],
            "EFFECTIVE_END_DATE": [
                "EffectiveEndDate", "EndDate",
                "effective_end_date", "end_date",
            ],
        },
        validation_rules={
            "JOB_FAMILY_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "JOB_FAMILY_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "JOB_FAMILY_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "JOB_FAMILY_NAME must be 1-240 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date (YYYY/MM/DD)",
            },
            "ACTIVE_STATUS": {
                "required": True,
                "regex": r"^[AI]$",
                "error_msg": "ACTIVE_STATUS must be A (Active) or I (Inactive)",
            },
            "SOURCE_SYSTEM_OWNER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SOURCE_SYSTEM_OWNER must be 1-30 chars",
            },
            "SOURCE_SYSTEM_ID": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "SOURCE_SYSTEM_ID must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "ACTION_REASON_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ACTION_REASON_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "EFFECTIVE_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_END_DATE must be a valid date (YYYY/MM/DD)",
            },
        },
        default_source_system_owner="HCMQA-001",
        default_source_system_id="JOB_FAMILY_{row_index}",
        output_filename_template="JobFamily.dat",
        output_header=(
            "METADATA|JobFamily|SourceSystemOwner|SourceSystemId"
            "|EffectiveStartDate|EffectiveEndDate"
            "|JobFamilyCode|JobFamilyName|ActiveStatus|ActionReasonCode"
        ),
        output_template=(
            "MERGE|JobFamily|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}"
            "|{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}"
            "|{JOB_FAMILY_CODE}|{JOB_FAMILY_NAME}|{ACTIVE_STATUS}|{ACTION_REASON_CODE}"
        ),
        description="JobFamily object migration file. Loads job family definitions into Oracle Fusion HCM. Must be loaded before Job.dat.",
    ),
    "Position": ObjectDefinition(  # type: ignore
        name="Position",
        aliases=["position", "positions", "post", "posts"],
        required_columns=[
            "BUSINESS_UNIT_NAME",
            "POSITION_CODE",
            "EFFECTIVE_START_DATE",
            "ACTIVE_STATUS",
            "DEPARTMENT_NAME",
            "HIRING_STATUS",
            "JOB_CODE",
            "JOB_SET_CODE",
            "NAME",
            "SOURCE_SYSTEM_OWNER",
            "SOURCE_SYSTEM_ID",
        ],
        optional_columns=[
            "LOCATION_SET_CODE",
            "LOCATION_CODE",
            "ENTRY_GRADE_SET_CODE",
            "ENTRY_GRADE_CODE",
            "ENTRY_STEP_NAME",
            "SUPERVISOR_PERSON_NUMBER",
            "SUPERVISOR_ASSIGNMENT_NUMBER",
            "REGULAR_TEMPORARY",
            "FTE",
            "CALCULATE_FTE",
            "FULL_PART_TIME",
            "START_TIME",
            "END_TIME",
            "POSITION_TYPE",
            "HEAD_COUNT",
            "WORKING_HOURS",
            "FREQUENCY",
            "OVERLAP_ALLOWED_FLAG",
            "SEASONAL_FLAG",
            "SEASONAL_START_DATE",
            "SEASONAL_END_DATE",
            "PROBATION_PERIOD",
            "SECURITY_CLEARANCE",
            "ACTION_REASON_CODE",
            "GRADE_LADDER_NAME",
            "STANDARD_WORKING_HOURS",
            "STANDARD_WORKING_FREQUENCY",
            "STANDARD_ANNUAL_WORKING_DURATION",
            "ANNUAL_WORKING_DURATION_UNITS",
            "ANNUAL_WORKING_DURATION",
            "UNION_NAME",
            "UNION_CLASSIFICATION_CODE",
            "COLLECTIVE_AGREEMENT_CODE",
            "ASSIGNMENT_CATEGORY",
            "BUDGET_AMOUNT",
            "BUDGET_AMOUNT_CURRENCY",
            "BUDGETED_POSITION_FLAG",
            "COST_CENTER",
            "COST_CENTER_NAME",
            "REQUISITION_NUMBER",
            "EFFECTIVE_END_DATE",
        ],
        unique_columns=["POSITION_CODE", "SOURCE_SYSTEM_ID"],
        date_columns=[
            "EFFECTIVE_START_DATE",
            "EFFECTIVE_END_DATE",
            "SEASONAL_START_DATE",
            "SEASONAL_END_DATE",
        ],
        column_aliases={
            "BUSINESS_UNIT_NAME": [
                "BusinessUnitName", "BUName",
                "business_unit_name", "bu_name",
            ],
            "POSITION_CODE": [
                "PositionCode", "Code",
                "position_code", "code",
            ],
            "EFFECTIVE_START_DATE": [
                "EffectiveStartDate", "StartDate",
                "effective_start_date", "start_date",
            ],
            "ACTIVE_STATUS": [
                "ActiveStatus", "Status",
                "active_status", "status",
            ],
            "DEPARTMENT_NAME": [
                "DepartmentName", "Department",
                "department_name", "department",
            ],
            "HIRING_STATUS": [
                "HiringStatus", "hiring_status",
            ],
            "JOB_CODE": [
                "JobCode", "job_code",
            ],
            "JOB_SET_CODE": [
                "JobSetCode", "job_set_code",
            ],
            "NAME": [
                "Name", "PositionName", "Title",
                "name", "position_name", "title",
            ],
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "LOCATION_SET_CODE": ["LocationSetCode", "location_set_code"],
            "LOCATION_CODE": [
                "LocationCode", "Location",
                "location_code", "location",
            ],
            "ENTRY_GRADE_SET_CODE": ["EntryGradeSetCode", "entry_grade_set_code"],
            "ENTRY_GRADE_CODE": ["EntryGradeCode", "entry_grade_code"],
            "ENTRY_STEP_NAME": ["EntryStepName", "entry_step_name"],
            "SUPERVISOR_PERSON_NUMBER": [
                "SupervisorPersonNumber", "supervisor_person_number",
            ],
            "SUPERVISOR_ASSIGNMENT_NUMBER": [
                "SupervisorAssignmentNumber", "supervisor_assignment_number",
            ],
            "REGULAR_TEMPORARY": ["RegularTemporary", "regular_temporary"],
            "FTE": ["FTE", "fte"],
            "CALCULATE_FTE": ["CalculateFTE", "calculate_fte"],
            "FULL_PART_TIME": ["FullPartTime", "full_part_time"],
            "START_TIME": ["StartTime", "start_time"],
            "END_TIME": ["EndTime", "end_time"],
            "POSITION_TYPE": ["PositionType", "position_type"],
            "HEAD_COUNT": ["HeadCount", "head_count"],
            "WORKING_HOURS": ["WorkingHours", "working_hours"],
            "FREQUENCY": ["Frequency", "frequency"],
            "OVERLAP_ALLOWED_FLAG": ["OverlapAllowedFlag", "overlap_allowed_flag"],
            "SEASONAL_FLAG": ["SeasonalFlag", "seasonal_flag"],
            "SEASONAL_START_DATE": ["SeasonalStartDate", "seasonal_start_date"],
            "SEASONAL_END_DATE": ["SeasonalEndDate", "seasonal_end_date"],
            "PROBATION_PERIOD": ["ProbationPeriod", "probation_period"],
            "SECURITY_CLEARANCE": ["SecurityClearance", "security_clearance"],
            "ACTION_REASON_CODE": ["ActionReasonCode", "action_reason_code"],
            "GRADE_LADDER_NAME": ["GradeLadderName", "grade_ladder_name"],
            "STANDARD_WORKING_HOURS": [
                "StandardWorkingHours", "standard_working_hours",
            ],
            "STANDARD_WORKING_FREQUENCY": [
                "StandardWorkingFrequency", "standard_working_frequency",
            ],
            "STANDARD_ANNUAL_WORKING_DURATION": [
                "StandardAnnualWorkingDuration", "standard_annual_working_duration",
            ],
            "ANNUAL_WORKING_DURATION_UNITS": [
                "AnnualWorkingDurationUnits", "annual_working_duration_units",
            ],
            "ANNUAL_WORKING_DURATION": [
                "AnnualWorkingDuration", "annual_working_duration",
            ],
            "UNION_NAME": ["UnionName", "union_name"],
            "UNION_CLASSIFICATION_CODE": [
                "UnionClassificationCode", "union_classification_code",
            ],
            "COLLECTIVE_AGREEMENT_CODE": [
                "CollectiveAgreementCode", "collective_agreement_code",
            ],
            "ASSIGNMENT_CATEGORY": ["AssignmentCategory", "assignment_category"],
            "BUDGET_AMOUNT": ["BudgetAmount", "budget_amount"],
            "BUDGET_AMOUNT_CURRENCY": ["BudgetAmountCurrency", "budget_amount_currency"],
            "BUDGETED_POSITION_FLAG": ["BudgetedPositionFlag", "budgeted_position_flag"],
            "COST_CENTER": ["CostCenter", "cost_center"],
            "COST_CENTER_NAME": ["CostCenterName", "cost_center_name"],
            "REQUISITION_NUMBER": ["RequisitionNumber", "requisition_number"],
            "EFFECTIVE_END_DATE": [
                "EffectiveEndDate", "EndDate",
                "effective_end_date", "end_date",
            ],
        },
        validation_rules={
            "BUSINESS_UNIT_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "BUSINESS_UNIT_NAME must be 1-240 chars",
            },
            "POSITION_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "POSITION_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date (YYYY/MM/DD)",
            },
            "ACTIVE_STATUS": {
                "required": True,
                "regex": r"^[AI]$",
                "error_msg": "ACTIVE_STATUS must be A (Active) or I (Inactive)",
            },
            "DEPARTMENT_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "DEPARTMENT_NAME must be 1-240 chars",
            },
            "HIRING_STATUS": {
                "required": True,
                "allowed_values": ["ACTIVE", "FROZEN", "PROPOSED", "ELIMINATED"],
                "error_msg": "HIRING_STATUS must be ACTIVE, FROZEN, PROPOSED, or ELIMINATED",
            },
            "JOB_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "JOB_CODE must be 1-30 chars",
            },
            "JOB_SET_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "JOB_SET_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "NAME (Position Name) must be 1-240 chars",
            },
            "SOURCE_SYSTEM_OWNER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SOURCE_SYSTEM_OWNER must be 1-30 chars",
            },
            "SOURCE_SYSTEM_ID": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "SOURCE_SYSTEM_ID must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "LOCATION_SET_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "LOCATION_SET_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "LOCATION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "LOCATION_CODE must be 1-30 chars",
            },
            "ENTRY_GRADE_SET_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ENTRY_GRADE_SET_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "ENTRY_GRADE_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "ENTRY_GRADE_CODE must be 1-30 chars",
            },
            "ENTRY_STEP_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "ENTRY_STEP_NAME must be 1-240 chars",
            },
            "SUPERVISOR_PERSON_NUMBER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SUPERVISOR_PERSON_NUMBER must be 1-30 chars",
            },
            "SUPERVISOR_ASSIGNMENT_NUMBER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SUPERVISOR_ASSIGNMENT_NUMBER must be 1-30 chars",
            },
            "REGULAR_TEMPORARY": {
                "required": False,
                "allowed_values": ["R", "T"],
                "error_msg": "REGULAR_TEMPORARY must be R (Regular) or T (Temporary)",
            },
            "FTE": {
                "required": False,
                "data_type": "decimal",
                "error_msg": "FTE must be a numeric value",
            },
            "CALCULATE_FTE": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "CALCULATE_FTE must be Y or N",
            },
            "FULL_PART_TIME": {
                "required": False,
                "allowed_values": ["FULL_TIME", "PART_TIME"],
                "error_msg": "FULL_PART_TIME must be FULL_TIME or PART_TIME",
            },
            "START_TIME": {
                "required": False,
                "min_length": 1,
                "max_length": 10,
                "error_msg": "START_TIME must be 1-10 chars",
            },
            "END_TIME": {
                "required": False,
                "min_length": 1,
                "max_length": 10,
                "error_msg": "END_TIME must be 1-10 chars",
            },
            "POSITION_TYPE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "POSITION_TYPE must be 1-30 chars",
            },
            "HEAD_COUNT": {
                "required": False,
                "data_type": "integer",
                "error_msg": "HEAD_COUNT must be a numeric value",
            },
            "WORKING_HOURS": {
                "required": False,
                "data_type": "decimal",
                "error_msg": "WORKING_HOURS must be a numeric value",
            },
            "FREQUENCY": {
                "required": False,
                "allowed_values": ["W", "M", "Y"],
                "error_msg": "FREQUENCY must be W (Weekly), M (Monthly), or Y (Yearly)",
            },
            "OVERLAP_ALLOWED_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "OVERLAP_ALLOWED_FLAG must be Y or N",
            },
            "SEASONAL_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "SEASONAL_FLAG must be Y or N",
            },
            "SEASONAL_START_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "SEASONAL_START_DATE must be a valid date (YYYY/MM/DD)",
            },
            "SEASONAL_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "SEASONAL_END_DATE must be a valid date (YYYY/MM/DD)",
            },
            "PROBATION_PERIOD": {
                "required": False,
                "data_type": "integer",
                "error_msg": "PROBATION_PERIOD must be a numeric value",
            },
            "SECURITY_CLEARANCE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SECURITY_CLEARANCE must be 1-30 chars",
            },
            "ACTION_REASON_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ACTION_REASON_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "GRADE_LADDER_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "GRADE_LADDER_NAME must be 1-240 chars",
            },
            "STANDARD_WORKING_HOURS": {
                "required": False,
                "data_type": "decimal",
                "error_msg": "STANDARD_WORKING_HOURS must be a numeric value",
            },
            "STANDARD_WORKING_FREQUENCY": {
                "required": False,
                "allowed_values": ["W", "M", "Y"],
                "error_msg": "STANDARD_WORKING_FREQUENCY must be W (Weekly), M (Monthly), or Y (Yearly)",
            },
            "STANDARD_ANNUAL_WORKING_DURATION": {
                "required": False,
                "data_type": "decimal",
                "error_msg": "STANDARD_ANNUAL_WORKING_DURATION must be a numeric value",
            },
            "ANNUAL_WORKING_DURATION_UNITS": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "ANNUAL_WORKING_DURATION_UNITS must be 1-30 chars",
            },
            "ANNUAL_WORKING_DURATION": {
                "required": False,
                "data_type": "decimal",
                "error_msg": "ANNUAL_WORKING_DURATION must be a numeric value",
            },
            "UNION_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "UNION_NAME must be 1-240 chars",
            },
            "UNION_CLASSIFICATION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "UNION_CLASSIFICATION_CODE must be 1-30 chars",
            },
            "COLLECTIVE_AGREEMENT_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "COLLECTIVE_AGREEMENT_CODE must be 1-30 chars",
            },
            "ASSIGNMENT_CATEGORY": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "ASSIGNMENT_CATEGORY must be 1-30 chars",
            },
            "BUDGET_AMOUNT": {
                "required": False,
                "data_type": "decimal",
                "error_msg": "BUDGET_AMOUNT must be a numeric value",
            },
            "BUDGET_AMOUNT_CURRENCY": {
                "required": False,
                "min_length": 3,
                "max_length": 3,
                "regex": r"^[A-Z]{3}$",
                "error_msg": "BUDGET_AMOUNT_CURRENCY must be a 3-letter ISO currency code (e.g. USD, INR)",
            },
            "BUDGETED_POSITION_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "BUDGETED_POSITION_FLAG must be Y or N",
            },
            "COST_CENTER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "COST_CENTER must be 1-30 chars",
            },
            "COST_CENTER_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "COST_CENTER_NAME must be 1-240 chars",
            },
            "REQUISITION_NUMBER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "REQUISITION_NUMBER must be 1-30 chars",
            },
            "EFFECTIVE_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_END_DATE must be a valid date (YYYY/MM/DD)",
            },
        },
        default_source_system_owner="HCMQA-001",
        default_source_system_id="POSITION_{row_index}",
        output_filename_template="Position.dat",
        output_header=(
            "METADATA|Position|SourceSystemOwner|SourceSystemId"
            "|EffectiveStartDate|EffectiveEndDate"
            "|BusinessUnitName|PositionCode|Name|ActiveStatus"
            "|DepartmentName|HiringStatus|JobCode|JobSetCode"
            "|LocationSetCode|LocationCode|EntryGradeSetCode|EntryGradeCode|EntryStepName"
            "|SupervisorPersonNumber|SupervisorAssignmentNumber"
            "|RegularTemporary|FTE|CalculateFTE|FullPartTime"
            "|StartTime|EndTime|PositionType|HeadCount|WorkingHours|Frequency"
            "|OverlapAllowedFlag|SeasonalFlag|SeasonalStartDate|SeasonalEndDate"
            "|ProbationPeriod|SecurityClearance|ActionReasonCode|GradeLadderName"
            "|StandardWorkingHours|StandardWorkingFrequency"
            "|StandardAnnualWorkingDuration|AnnualWorkingDurationUnits|AnnualWorkingDuration"
            "|UnionName|UnionClassificationCode|CollectiveAgreementCode|AssignmentCategory"
            "|BudgetAmount|BudgetAmountCurrency|BudgetedPositionFlag"
            "|CostCenter|CostCenterName|RequisitionNumber"
        ),
        output_template=(
            "MERGE|Position|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}"
            "|{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}"
            "|{BUSINESS_UNIT_NAME}|{POSITION_CODE}|{NAME}|{ACTIVE_STATUS}"
            "|{DEPARTMENT_NAME}|{HIRING_STATUS}|{JOB_CODE}|{JOB_SET_CODE}"
            "|{LOCATION_SET_CODE}|{LOCATION_CODE}|{ENTRY_GRADE_SET_CODE}|{ENTRY_GRADE_CODE}|{ENTRY_STEP_NAME}"
            "|{SUPERVISOR_PERSON_NUMBER}|{SUPERVISOR_ASSIGNMENT_NUMBER}"
            "|{REGULAR_TEMPORARY}|{FTE}|{CALCULATE_FTE}|{FULL_PART_TIME}"
            "|{START_TIME}|{END_TIME}|{POSITION_TYPE}|{HEAD_COUNT}|{WORKING_HOURS}|{FREQUENCY}"
            "|{OVERLAP_ALLOWED_FLAG}|{SEASONAL_FLAG}|{SEASONAL_START_DATE}|{SEASONAL_END_DATE}"
            "|{PROBATION_PERIOD}|{SECURITY_CLEARANCE}|{ACTION_REASON_CODE}|{GRADE_LADDER_NAME}"
            "|{STANDARD_WORKING_HOURS}|{STANDARD_WORKING_FREQUENCY}"
            "|{STANDARD_ANNUAL_WORKING_DURATION}|{ANNUAL_WORKING_DURATION_UNITS}|{ANNUAL_WORKING_DURATION}"
            "|{UNION_NAME}|{UNION_CLASSIFICATION_CODE}|{COLLECTIVE_AGREEMENT_CODE}|{ASSIGNMENT_CATEGORY}"
            "|{BUDGET_AMOUNT}|{BUDGET_AMOUNT_CURRENCY}|{BUDGETED_POSITION_FLAG}"
            "|{COST_CENTER}|{COST_CENTER_NAME}|{REQUISITION_NUMBER}"
        ),
        description="Position object migration file. Loads position definitions into Oracle Fusion HCM. Must load Department.dat, Job.dat, and Location.dat first.",
    ),

    "GradeLadder": ObjectDefinition(  # type: ignore
        name="GradeLadder",
        aliases=["grade ladder", "gradeladder", "grade_ladder", "ladder"],
        required_columns=[
            "GRADE_LADDER_NAME",
            "EFFECTIVE_START_DATE",
            "GRADE_TYPE",
            "GRADE_SET_CODE",
            "ACTIVE_STATUS",
            "SOURCE_SYSTEM_ID",
            "SOURCE_SYSTEM_OWNER",
        ],
        optional_columns=[
            "EFFECTIVE_END_DATE",
            "ACTION_REASON_CODE",
            "PROG_ACTION_CODE",
            "ACTIONS",
            "PROG_ACTION_REASON_CODE",
            "ACTION_REASONS",
            "GRADE_LADDER_GRP_CODE",
            "AUTO_PROGRESSION_CODE",
            "PROGRESSION_STYLE_CODE",
            "PROGRESSION_DATE_CODE",
            "FORMULA",
            "PROGRESSION_DATE_RULE_NAME",
            "UPDATE_SALARY_FLAG",
            "LEGISLATIVE_DATA_GROUPS",
            "LEGISLATIVE_DATA_GROUP",
            "AUTO_SAL_CHANGE_CODE",
            "RATE_SYNC_ACTION_CODE",
            "RATE_SYNC_ACTION_ID",
            "RATE_SYNC_ACTION_REASON_CODE",
            "RATE_CHANGE_DATE_CODE",
            "SALARY_ACTION_CODE",
            "RATE_CHANGE_DATE_RULE_NAME",
            "SALARY_ACTION_REASON_CODE",
            "GUID",
        ],
        unique_columns=["GRADE_LADDER_NAME", "SOURCE_SYSTEM_ID"],
        date_columns=[
            "EFFECTIVE_START_DATE",
            "EFFECTIVE_END_DATE",
        ],
        column_aliases={
            "GRADE_LADDER_NAME": [
                "GradeLadderName", "LadderName",
                "grade_ladder_name", "ladder_name",
            ],
            "EFFECTIVE_START_DATE": [
                "EffectiveStartDate", "StartDate",
                "effective_start_date", "start_date",
            ],
            "GRADE_TYPE": [
                "GradeType", "grade_type",
            ],
            "GRADE_SET_CODE": [
                "GradeSetCode", "SetCode",
                "grade_set_code", "set_code",
            ],
            "ACTIVE_STATUS": [
                "ActiveStatus", "Status",
                "active_status", "status",
            ],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "EFFECTIVE_END_DATE": [
                "EffectiveEndDate", "EndDate",
                "effective_end_date", "end_date",
            ],
            "ACTION_REASON_CODE": ["ActionReasonCode", "action_reason_code"],
            "PROG_ACTION_CODE": ["ProgActionCode", "prog_action_code"],
            "ACTIONS": ["Actions", "actions"],
            "PROG_ACTION_REASON_CODE": ["ProgActionReasonCode", "prog_action_reason_code"],
            "ACTION_REASONS": ["ActionReasons", "action_reasons"],
            "GRADE_LADDER_GRP_CODE": [
                "GradeLadderGrpCode", "grade_ladder_grp_code",
            ],
            "AUTO_PROGRESSION_CODE": [
                "AutoProgressionCode", "auto_progression_code",
            ],
            "PROGRESSION_STYLE_CODE": [
                "ProgressionStyleCode", "progression_style_code",
            ],
            "PROGRESSION_DATE_CODE": [
                "ProgressionDateCode", "progression_date_code",
            ],
            "FORMULA": ["Formula", "formula"],
            "PROGRESSION_DATE_RULE_NAME": [
                "ProgressionDateRuleName", "progression_date_rule_name",
            ],
            "UPDATE_SALARY_FLAG": [
                "UpdateSalaryFlag", "update_salary_flag",
            ],
            "LEGISLATIVE_DATA_GROUPS": [
                "LegislativeDataGroups", "legislative_data_groups",
            ],
            "LEGISLATIVE_DATA_GROUP": [
                "LegislativeDataGroup", "LDG",
                "legislative_data_group", "ldg",
            ],
            "AUTO_SAL_CHANGE_CODE": [
                "AutoSalChangeCode", "auto_sal_change_code",
            ],
            "RATE_SYNC_ACTION_CODE": [
                "RateSyncActionCode", "rate_sync_action_code",
            ],
            "RATE_SYNC_ACTION_ID": [
                "RateSyncActionId", "rate_sync_action_id",
            ],
            "RATE_SYNC_ACTION_REASON_CODE": [
                "RateSyncActionReasonCode", "rate_sync_action_reason_code",
            ],
            "RATE_CHANGE_DATE_CODE": [
                "RateChangeDateCode", "rate_change_date_code",
            ],
            "SALARY_ACTION_CODE": [
                "SalaryActionCode", "salary_action_code",
            ],
            "RATE_CHANGE_DATE_RULE_NAME": [
                "RateChangeDateRuleName", "rate_change_date_rule_name",
            ],
            "SALARY_ACTION_REASON_CODE": [
                "SalaryActionReasonCode", "salary_action_reason_code",
            ],
            "GUID": ["GUID", "Guid", "guid"],
        },
        validation_rules={
            "GRADE_LADDER_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "GRADE_LADDER_NAME must be 1-240 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date (YYYY/MM/DD)",
            },
            "GRADE_TYPE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "GRADE_TYPE must be 1-30 chars",
            },
            "GRADE_SET_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "GRADE_SET_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "ACTIVE_STATUS": {
                "required": True,
                "regex": r"^[AI]$",
                "error_msg": "ACTIVE_STATUS must be A (Active) or I (Inactive)",
            },
            "SOURCE_SYSTEM_ID": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "SOURCE_SYSTEM_ID must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "SOURCE_SYSTEM_OWNER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SOURCE_SYSTEM_OWNER must be 1-30 chars",
            },
            "EFFECTIVE_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_END_DATE must be a valid date (YYYY/MM/DD)",
            },
            "ACTION_REASON_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ACTION_REASON_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "PROG_ACTION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "PROG_ACTION_CODE must be 1-30 chars",
            },
            "ACTIONS": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "ACTIONS must be 1-240 chars",
            },
            "PROG_ACTION_REASON_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "PROG_ACTION_REASON_CODE must be 1-30 chars",
            },
            "ACTION_REASONS": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "ACTION_REASONS must be 1-240 chars",
            },
            "GRADE_LADDER_GRP_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "GRADE_LADDER_GRP_CODE must be 1-30 chars",
            },
            "AUTO_PROGRESSION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "AUTO_PROGRESSION_CODE must be 1-30 chars",
            },
            "PROGRESSION_STYLE_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "PROGRESSION_STYLE_CODE must be 1-30 chars",
            },
            "PROGRESSION_DATE_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "PROGRESSION_DATE_CODE must be 1-30 chars",
            },
            "FORMULA": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "FORMULA must be 1-240 chars",
            },
            "PROGRESSION_DATE_RULE_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "PROGRESSION_DATE_RULE_NAME must be 1-240 chars",
            },
            "UPDATE_SALARY_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "UPDATE_SALARY_FLAG must be Y or N",
            },
            "LEGISLATIVE_DATA_GROUPS": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "LEGISLATIVE_DATA_GROUPS must be 1-240 chars",
            },
            "LEGISLATIVE_DATA_GROUP": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "LEGISLATIVE_DATA_GROUP must be 1-240 chars",
            },
            "AUTO_SAL_CHANGE_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "AUTO_SAL_CHANGE_CODE must be 1-30 chars",
            },
            "RATE_SYNC_ACTION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "RATE_SYNC_ACTION_CODE must be 1-30 chars",
            },
            "RATE_SYNC_ACTION_ID": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "RATE_SYNC_ACTION_ID must be 1-30 chars",
            },
            "RATE_SYNC_ACTION_REASON_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "RATE_SYNC_ACTION_REASON_CODE must be 1-30 chars",
            },
            "RATE_CHANGE_DATE_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "RATE_CHANGE_DATE_CODE must be 1-30 chars",
            },
            "SALARY_ACTION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SALARY_ACTION_CODE must be 1-30 chars",
            },
            "RATE_CHANGE_DATE_RULE_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "RATE_CHANGE_DATE_RULE_NAME must be 1-240 chars",
            },
            "SALARY_ACTION_REASON_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SALARY_ACTION_REASON_CODE must be 1-30 chars",
            },
            "GUID": {
                "required": False,
                "min_length": 1,
                "max_length": 64,
                "error_msg": "GUID must be 1-64 chars",
            },
        },
        default_source_system_owner="HCMQA-001",
        default_source_system_id="GRADE_LADDER_{row_index}",
        output_filename_template="GradeLadder.dat",
        output_header=(
            "METADATA|GradeLadder|SourceSystemOwner|SourceSystemId"
            "|EffectiveStartDate|EffectiveEndDate"
            "|GradeLadderName|GradeType|GradeSetCode|ActiveStatus"
            "|ActionReasonCode|ProgActionCode|Actions"
            "|ProgActionReasonCode|ActionReasons|GradeLadderGrpCode"
            "|AutoProgressionCode|ProgressionStyleCode|ProgressionDateCode"
            "|Formula|ProgressionDateRuleName|UpdateSalaryFlag"
            "|LegislativeDataGroups|LegislativeDataGroup"
            "|AutoSalChangeCode|RateSyncActionCode|RateSyncActionId"
            "|RateSyncActionReasonCode|RateChangeDateCode|SalaryActionCode"
            "|RateChangeDateRuleName|SalaryActionReasonCode|GUID"
        ),
        output_template=(
            "MERGE|GradeLadder|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}"
            "|{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}"
            "|{GRADE_LADDER_NAME}|{GRADE_TYPE}|{GRADE_SET_CODE}|{ACTIVE_STATUS}"
            "|{ACTION_REASON_CODE}|{PROG_ACTION_CODE}|{ACTIONS}"
            "|{PROG_ACTION_REASON_CODE}|{ACTION_REASONS}|{GRADE_LADDER_GRP_CODE}"
            "|{AUTO_PROGRESSION_CODE}|{PROGRESSION_STYLE_CODE}|{PROGRESSION_DATE_CODE}"
            "|{FORMULA}|{PROGRESSION_DATE_RULE_NAME}|{UPDATE_SALARY_FLAG}"
            "|{LEGISLATIVE_DATA_GROUPS}|{LEGISLATIVE_DATA_GROUP}"
            "|{AUTO_SAL_CHANGE_CODE}|{RATE_SYNC_ACTION_CODE}|{RATE_SYNC_ACTION_ID}"
            "|{RATE_SYNC_ACTION_REASON_CODE}|{RATE_CHANGE_DATE_CODE}|{SALARY_ACTION_CODE}"
            "|{RATE_CHANGE_DATE_RULE_NAME}|{SALARY_ACTION_REASON_CODE}|{GUID}"
        ),
        description="GradeLadder object migration file. Loads grade ladder definitions into Oracle Fusion HCM. Must load Grade.dat first.",
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