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

    "GradeRate": ObjectDefinition( 
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

    "Job": ObjectDefinition(  
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

    "JobFamily": ObjectDefinition(  
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
    "Position": ObjectDefinition(  
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

    "GradeLadder": ObjectDefinition(  
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
    
    "Worker": ObjectDefinition( # type: ignore
        name="Worker",
        aliases=["worker", "workers", "employee", "employees", "person", "persons"],
        required_columns=[
            "SOURCE_SYSTEM_OWNER",
            "SOURCE_SYSTEM_ID",
            "PERSON_NUMBER",
            "EFFECTIVE_START_DATE",
            "START_DATE",
        ],
        optional_columns=[
            "EFFECTIVE_END_DATE",
            "BLOOD_TYPE",
            "PERSON_DUPLICATE_CHECK",
            "DATE_OF_BIRTH",
            "DATE_OF_DEATH",
            "COUNTRY_OF_BIRTH",
            "REGION_OF_BIRTH",
            "TOWN_OF_BIRTH",
            "GUID",
            "ACTION_CODE",
            "REASON_CODE",
            "CORRESPONDENCE_LANGUAGE",
        ],
        unique_columns=[
            "PERSON_NUMBER",
            "SOURCE_SYSTEM_ID",
        ],
        date_columns=[
            "EFFECTIVE_START_DATE",
            "EFFECTIVE_END_DATE",
            "START_DATE",
            "DATE_OF_BIRTH",
            "DATE_OF_DEATH",
        ],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "PERSON_NUMBER": ["PersonNumber", "person_number", "Person_Number"],
            "EFFECTIVE_START_DATE": ["EffectiveStartDate", "effective_start_date", "StartDate", "start_date"],
            "START_DATE": ["StartDate", "start_date", "HireDate", "hire_date"],
            "EFFECTIVE_END_DATE": ["EffectiveEndDate", "effective_end_date", "EndDate", "end_date"],
            "BLOOD_TYPE": ["BloodType", "blood_type", "Blood_Type"],
            "PERSON_DUPLICATE_CHECK": [
                "PersonDuplicateCheck", "person_duplicate_check",
                "Person_Duplicate_Check", "DuplicateCheck", "duplicate_check",
            ],
            "DATE_OF_BIRTH": ["DateOfBirth", "date_of_birth", "DOB", "dob", "BirthDate", "birth_date"],
            "DATE_OF_DEATH": ["DateOfDeath", "date_of_death", "DOD", "dod", "DeathDate", "death_date"],
            "COUNTRY_OF_BIRTH": [
                "CountryOfBirth", "country_of_birth", "Country_Of_Birth",
                "BirthCountry", "birth_country",
            ],
            "REGION_OF_BIRTH": [
                "RegionOfBirth", "region_of_birth", "Region_Of_Birth",
                "BirthRegion", "birth_region",
            ],
            "TOWN_OF_BIRTH": [
                "TownOfBirth", "town_of_birth", "Town_Of_Birth",
                "BirthTown", "birth_town", "CityOfBirth", "city_of_birth",
            ],
            "GUID": ["GUID", "guid", "GlobalUniqueIdentifier", "global_unique_identifier"],
            "ACTION_CODE": ["ActionCode", "action_code", "Action_Code"],
            "REASON_CODE": ["ReasonCode", "reason_code", "Reason_Code", "ActionReasonCode", "action_reason_code"],
            "CORRESPONDENCE_LANGUAGE": [
                "CorrespondenceLanguage", "correspondence_language",
                "Correspondence_Language", "CorresLang", "corres_lang",
            ],
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
            "PERSON_NUMBER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "PERSON_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date",
            },
            "START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "START_DATE (new record hire/start date) must be a valid date",
            },
            "EFFECTIVE_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_END_DATE must be a valid date",
            },
            "BLOOD_TYPE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "allowed_values": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                "error_msg": "BLOOD_TYPE must be a valid blood group (e.g. A+, O-, AB+)",
            },
            "PERSON_DUPLICATE_CHECK": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "PERSON_DUPLICATE_CHECK must be 1-240 chars",
            },
            "DATE_OF_BIRTH": {
                "required": False,
                "data_type": "date",
                "error_msg": "DATE_OF_BIRTH must be a valid date",
            },
            "DATE_OF_DEATH": {
                "required": False,
                "data_type": "date",
                "error_msg": "DATE_OF_DEATH must be a valid date",
            },
            "COUNTRY_OF_BIRTH": {
                "required": False,
                "min_length": 2,
                "max_length": 2,
                "regex": r"^[A-Z]{2}$",
                "error_msg": "COUNTRY_OF_BIRTH must be a 2-letter ISO country code (e.g. IN, US, GB)",
            },
            "REGION_OF_BIRTH": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "REGION_OF_BIRTH must be 1-30 chars",
            },
            "TOWN_OF_BIRTH": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "TOWN_OF_BIRTH must be 1-30 chars",
            },
            "GUID": {
                "required": False,
                "min_length": 1,
                "max_length": 64,
                "regex": r"^[A-Za-z0-9_\-]+$",
                "error_msg": "GUID must be alphanumeric with underscores/dashes, 1-64 chars",
            },
            "ACTION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ACTION_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "REASON_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "REASON_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "CORRESPONDENCE_LANGUAGE": {
                "required": False,
                "min_length": 2,
                "max_length": 30,
                "regex": r"^[A-Z]{2,3}$",
                "error_msg": "CORRESPONDENCE_LANGUAGE must be a valid 2-3 letter language code (e.g. EN, FR, HI)",
            },
        },
        default_source_system_owner="HCMQA-001",
        default_source_system_id="WORKER_{row_index}",
        output_filename_template="Worker.dat",
        output_header="METADATA|Worker|SourceSystemOwner|SourceSystemId|EffectiveStartDate|EffectiveEndDate|PersonNumber|StartDate|BloodType|PersonDuplicateCheck|DateOfBirth|DateOfDeath|CountryOfBirth|RegionOfBirth|TownOfBirth|GUID|ActionCode|ReasonCode|CorrespondenceLanguage",
        output_template=(
            "MERGE|Worker|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|"
            "{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}|"
            "{PERSON_NUMBER}|{START_DATE}|"
            "{BLOOD_TYPE}|{PERSON_DUPLICATE_CHECK}|"
            "{DATE_OF_BIRTH}|{DATE_OF_DEATH}|"
            "{COUNTRY_OF_BIRTH}|{REGION_OF_BIRTH}|{TOWN_OF_BIRTH}|"
            "{GUID}|{ACTION_CODE}|{REASON_CODE}|{CORRESPONDENCE_LANGUAGE}"
        ),
        description="Worker (Person) object migration file for Oracle Fusion HCM Workforce Structures.",
    ),

    "ExternalIdentifier": ObjectDefinition( # type: ignore
        name="ExternalIdentifier",
        aliases=["external_identifier", "externalidentifier", "ext_identifier", "external identifier"],
        required_columns=[
            "SOURCE_SYSTEM_OWNER",
            "SOURCE_SYSTEM_ID",
            "PERSON_NUMBER",
            "EXTERNAL_IDENTIFIER_SEQUENCE",
            "EXTERNAL_IDENTIFIER_NUMBER",
            "EXTERNAL_IDENTIFIER_TYPE",
            "DATE_FROM",
        ],
        optional_columns=[
            "GUID",
            "COMMENTS",
            "ASSIGNMENT_NUMBER",
            "DATE_TO",
        ],
        unique_columns=[
            "PERSON_NUMBER",
            "EXTERNAL_IDENTIFIER_SEQUENCE",
            "SOURCE_SYSTEM_ID",
        ],
        date_columns=[
            "DATE_FROM",
            "DATE_TO",
        ],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "PERSON_NUMBER": ["PersonNumber", "person_number", "Person_Number"],
            "EXTERNAL_IDENTIFIER_SEQUENCE": [
                "ExternalIdentifierSequence", "external_identifier_sequence",
                "External_Identifier_Sequence", "IdentifierSequence", "identifier_sequence",
            ],
            "EXTERNAL_IDENTIFIER_NUMBER": [
                "ExternalIdentifierNumber", "external_identifier_number",
                "External_Identifier_Number", "IdentifierNumber", "identifier_number",
            ],
            "EXTERNAL_IDENTIFIER_TYPE": [
                "ExternalIdentifierType", "external_identifier_type",
                "External_Identifier_Type", "IdentifierType", "identifier_type",
            ],
            "DATE_FROM": ["DateFrom", "date_from", "Date_From", "StartDate", "start_date", "EffectiveStartDate", "effective_start_date"],
            "DATE_TO": ["DateTo", "date_to", "Date_To", "EndDate", "end_date", "EffectiveEndDate", "effective_end_date"],
            "GUID": ["GUID", "guid", "GlobalUniqueIdentifier", "global_unique_identifier"],
            "COMMENTS": ["Comments", "comments", "Comment", "comment", "Notes", "notes"],
            "ASSIGNMENT_NUMBER": [
                "AssignmentNumber", "assignment_number", "Assignment_Number",
                "AssignmentNum", "assignment_num",
            ],
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
            "PERSON_NUMBER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "PERSON_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "EXTERNAL_IDENTIFIER_SEQUENCE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[0-9]+$",
                "error_msg": "EXTERNAL_IDENTIFIER_SEQUENCE must be a numeric value, 1-30 chars",
            },
            "EXTERNAL_IDENTIFIER_NUMBER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "EXTERNAL_IDENTIFIER_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "EXTERNAL_IDENTIFIER_TYPE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "EXTERNAL_IDENTIFIER_TYPE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "DATE_FROM": {
                "required": True,
                "data_type": "date",
                "error_msg": "DATE_FROM must be a valid date",
            },
            "DATE_TO": {
                "required": False,
                "data_type": "date",
                "error_msg": "DATE_TO must be a valid date",
            },
            "GUID": {
                "required": False,
                "min_length": 1,
                "max_length": 64,
                "regex": r"^[A-Za-z0-9_\-]+$",
                "error_msg": "GUID must be alphanumeric with underscores/dashes, 1-64 chars",
            },
            "COMMENTS": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "COMMENTS must be 1-240 chars",
            },
            "ASSIGNMENT_NUMBER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "ASSIGNMENT_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
        },
        default_source_system_owner="HCMQA-001",
        default_source_system_id="EXT_IDENTIFIER_{row_index}",
        output_filename_template="ExternalIdentifier.dat",
        output_header="METADATA|ExternalIdentifier|SourceSystemOwner|SourceSystemId|PersonNumber|ExternalIdentifierSequence|ExternalIdentifierNumber|ExternalIdentifierType|DateFrom|DateTo|GUID|Comments|AssignmentNumber",
        output_template=(
            "MERGE|ExternalIdentifier|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|"
            "{PERSON_NUMBER}|{EXTERNAL_IDENTIFIER_SEQUENCE}|"
            "{EXTERNAL_IDENTIFIER_NUMBER}|{EXTERNAL_IDENTIFIER_TYPE}|"
            "{DATE_FROM}|{DATE_TO}|"
            "{GUID}|{COMMENTS}|{ASSIGNMENT_NUMBER}"
        ),
        description="External Identifier object migration file for Oracle Fusion HCM Workforce Structures.",
    ),

    "PersonAddress": ObjectDefinition( # type: ignore
        name="PersonAddress",
        aliases=["person_address", "personaddress", "address", "addresses", "person address"],
        required_columns=[
            "SOURCE_SYSTEM_OWNER",
            "SOURCE_SYSTEM_ID",
            "PERSON_NUMBER",
            "ADDRESS_LINE1",
            "EFFECTIVE_START_DATE",
            "COUNTRY",
        ],
        optional_columns=[
            "ADDRESS_ID",
            "ADDRESS_TYPE",
            "LONGITUDE",
            "LATITUDE",
            "EFFECTIVE_END_DATE",
            "ADDRESS_LINE2",
            "ADDRESS_LINE3",
            "ADDRESS_LINE4",
            "BUILDING",
            "FLOOR_NUMBER",
            "TOWN_OR_CITY",
            "REGION1",
            "REGION2",
            "REGION3",
            "POSTAL_CODE",
            "LONG_POSTAL_CODE",
            "PRIMARY_FLAG",
            "GUID",
            "VALIDATION_STATUS_CODE",
            "PROVIDER",
        ],
        unique_columns=[
            "PERSON_NUMBER",
            "ADDRESS_ID",
            "SOURCE_SYSTEM_ID",
        ],
        date_columns=[
            "EFFECTIVE_START_DATE",
            "EFFECTIVE_END_DATE",
        ],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "PERSON_NUMBER": ["PersonNumber", "person_number", "Person_Number"],
            "ADDRESS_LINE1": [
                "AddressLine1", "address_line1", "Address_Line1",
                "AddressLine_1", "address_line_1",
            ],
            "EFFECTIVE_START_DATE": ["EffectiveStartDate", "effective_start_date", "StartDate", "start_date"],
            "EFFECTIVE_END_DATE": ["EffectiveEndDate", "effective_end_date", "EndDate", "end_date"],
            "COUNTRY": ["Country", "country", "CountryCode", "country_code"],
            "ADDRESS_ID": ["AddressId", "address_id", "Address_Id", "AddrId", "addr_id"],
            "ADDRESS_TYPE": [
                "AddressType", "address_type", "Address_Type",
                "AddrType", "addr_type",
            ],
            "LONGITUDE": ["Longitude", "longitude", "Long", "long"],
            "LATITUDE": ["Latitude", "latitude", "Lat", "lat"],
            "ADDRESS_LINE2": [
                "AddressLine2", "address_line2", "Address_Line2",
                "AddressLine_2", "address_line_2",
            ],
            "ADDRESS_LINE3": [
                "AddressLine3", "address_line3", "Address_Line3",
                "AddressLine_3", "address_line_3",
            ],
            "ADDRESS_LINE4": [
                "AddressLine4", "address_line4", "Address_Line4",
                "AddressLine_4", "address_line_4",
            ],
            "BUILDING": ["Building", "building", "BuildingName", "building_name"],
            "FLOOR_NUMBER": ["FloorNumber", "floor_number", "Floor_Number", "Floor", "floor"],
            "TOWN_OR_CITY": [
                "TownOrCity", "town_or_city", "Town_Or_City",
                "City", "city", "Town", "town",
            ],
            "REGION1": ["Region1", "region1", "Region_1", "State", "state", "Province", "province"],
            "REGION2": ["Region2", "region2", "Region_2", "County", "county", "District", "district"],
            "REGION3": ["Region3", "region3", "Region_3"],
            "POSTAL_CODE": [
                "PostalCode", "postal_code", "Postal_Code",
                "ZipCode", "zip_code", "Zip", "zip", "Pincode", "pincode",
            ],
            "LONG_POSTAL_CODE": [
                "LongPostalCode", "long_postal_code", "Long_Postal_Code",
                "ExtendedPostalCode", "extended_postal_code",
            ],
            "PRIMARY_FLAG": ["PrimaryFlag", "primary_flag", "Primary_Flag", "IsPrimary", "is_primary"],
            "GUID": ["GUID", "guid", "GlobalUniqueIdentifier", "global_unique_identifier"],
            "VALIDATION_STATUS_CODE": [
                "ValidationStatusCode", "validation_status_code",
                "Validation_Status_Code", "ValidationStatus", "validation_status",
            ],
            "PROVIDER": ["Provider", "provider", "AddressProvider", "address_provider"],
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
            "PERSON_NUMBER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "PERSON_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "ADDRESS_LINE1": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "ADDRESS_LINE1 must be 1-240 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date",
            },
            "COUNTRY": {
                "required": True,
                "min_length": 2,
                "max_length": 2,
                "regex": r"^[A-Z]{2}$",
                "error_msg": "COUNTRY must be a 2-letter ISO country code (e.g. IN, US, GB)",
            },
            "ADDRESS_ID": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "ADDRESS_ID must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "ADDRESS_TYPE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ADDRESS_TYPE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "LONGITUDE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^-?[0-9]{1,3}(\.[0-9]+)?$",
                "error_msg": "LONGITUDE must be a valid decimal number between -180 and 180",
            },
            "LATITUDE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^-?[0-9]{1,2}(\.[0-9]+)?$",
                "error_msg": "LATITUDE must be a valid decimal number between -90 and 90",
            },
            "EFFECTIVE_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_END_DATE must be a valid date",
            },
            "ADDRESS_LINE2": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "ADDRESS_LINE2 must be 1-240 chars",
            },
            "ADDRESS_LINE3": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "ADDRESS_LINE3 must be 1-240 chars",
            },
            "ADDRESS_LINE4": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "ADDRESS_LINE4 must be 1-240 chars",
            },
            "BUILDING": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "BUILDING must be 1-240 chars",
            },
            "FLOOR_NUMBER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "FLOOR_NUMBER must be 1-30 chars",
            },
            "TOWN_OR_CITY": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "TOWN_OR_CITY must be 1-30 chars",
            },
            "REGION1": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "REGION1 must be 1-30 chars",
            },
            "REGION2": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "REGION2 must be 1-30 chars",
            },
            "REGION3": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "REGION3 must be 1-30 chars",
            },
            "POSTAL_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "POSTAL_CODE must be 1-30 chars",
            },
            "LONG_POSTAL_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "LONG_POSTAL_CODE must be 1-30 chars",
            },
            "PRIMARY_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "PRIMARY_FLAG must be Y (Yes) or N (No)",
            },
            "GUID": {
                "required": False,
                "min_length": 1,
                "max_length": 64,
                "regex": r"^[A-Za-z0-9_\-]+$",
                "error_msg": "GUID must be alphanumeric with underscores/dashes, 1-64 chars",
            },
            "VALIDATION_STATUS_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "VALIDATION_STATUS_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "PROVIDER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "PROVIDER must be 1-30 chars",
            },
        },
        default_source_system_owner="HCMQA-001",
        default_source_system_id="PERSON_ADDRESS_{row_index}",
        output_filename_template="PersonAddress.dat",
        output_header="METADATA|PersonAddress|SourceSystemOwner|SourceSystemId|PersonNumber|AddressLine1|EffectiveStartDate|EffectiveEndDate|Country|AddressId|AddressType|Longitude|Latitude|AddressLine2|AddressLine3|AddressLine4|Building|FloorNumber|TownOrCity|Region1|Region2|Region3|PostalCode|LongPostalCode|PrimaryFlag|GUID|ValidationStatusCode|Provider",
        output_template=(
            "MERGE|PersonAddress|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|"
            "{PERSON_NUMBER}|{ADDRESS_LINE1}|"
            "{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}|"
            "{COUNTRY}|{ADDRESS_ID}|{ADDRESS_TYPE}|"
            "{LONGITUDE}|{LATITUDE}|"
            "{ADDRESS_LINE2}|{ADDRESS_LINE3}|{ADDRESS_LINE4}|"
            "{BUILDING}|{FLOOR_NUMBER}|"
            "{TOWN_OR_CITY}|{REGION1}|{REGION2}|{REGION3}|"
            "{POSTAL_CODE}|{LONG_POSTAL_CODE}|"
            "{PRIMARY_FLAG}|{GUID}|{VALIDATION_STATUS_CODE}|{PROVIDER}"
        ),
        description="Person Address object migration file for Oracle Fusion HCM Workforce Structures.",
    ),

    "PersonLegislativeData": ObjectDefinition( # type: ignore
        name="PersonLegislativeData",
        aliases=["person_legislative_data", "personlegislativedata", "legislative_data", "person legislative data"],
        required_columns=[
            "SOURCE_SYSTEM_OWNER",
            "SOURCE_SYSTEM_ID",
            "PERSON_NUMBER",
            "LEGISLATION_CODE",
        ],
        optional_columns=[
            "GUID",
            "EFFECTIVE_END_DATE",
            "HIGHEST_EDUCATION_LEVEL",
            "EFFECTIVE_START_DATE",
            "MARITAL_STATUS",
            "MARITAL_STATUS_DATE",
            "SEX",
        ],
        unique_columns=[
            "PERSON_NUMBER",
            "LEGISLATION_CODE",
            "SOURCE_SYSTEM_ID",
        ],
        date_columns=[
            "EFFECTIVE_START_DATE",
            "EFFECTIVE_END_DATE",
            "MARITAL_STATUS_DATE",
        ],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "PERSON_NUMBER": ["PersonNumber", "person_number", "Person_Number"],
            "LEGISLATION_CODE": [
                "LegislationCode", "legislation_code", "Legislation_Code",
                "LegCode", "leg_code",
            ],
            "GUID": ["GUID", "guid", "GlobalUniqueIdentifier", "global_unique_identifier"],
            "EFFECTIVE_START_DATE": ["EffectiveStartDate", "effective_start_date", "StartDate", "start_date"],
            "EFFECTIVE_END_DATE": ["EffectiveEndDate", "effective_end_date", "EndDate", "end_date"],
            "HIGHEST_EDUCATION_LEVEL": [
                "HighestEducationLevel", "highest_education_level",
                "Highest_Education_Level", "EducationLevel", "education_level",
            ],
            "MARITAL_STATUS": [
                "MaritalStatus", "marital_status", "Marital_Status",
                "MarStatus", "mar_status",
            ],
            "MARITAL_STATUS_DATE": [
                "MaritalStatusDate", "marital_status_date",
                "Marital_Status_Date", "MarStatusDate", "mar_status_date",
            ],
            "SEX": ["Sex", "sex", "Gender", "gender", "GenderCode", "gender_code"],
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
            "PERSON_NUMBER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "PERSON_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "LEGISLATION_CODE": {
                "required": True,
                "min_length": 2,
                "max_length": 2,
                "regex": r"^[A-Z]{2}$",
                "error_msg": "LEGISLATION_CODE must be a 2-letter ISO country code (e.g. IN, US, GB)",
            },
            "GUID": {
                "required": False,
                "min_length": 1,
                "max_length": 64,
                "regex": r"^[A-Za-z0-9_\-]+$",
                "error_msg": "GUID must be alphanumeric with underscores/dashes, 1-64 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date",
            },
            "EFFECTIVE_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_END_DATE must be a valid date",
            },
            "HIGHEST_EDUCATION_LEVEL": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "HIGHEST_EDUCATION_LEVEL must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "MARITAL_STATUS": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "MARITAL_STATUS must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "MARITAL_STATUS_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "MARITAL_STATUS_DATE must be a valid date",
            },
            "SEX": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "SEX must be uppercase alphanumeric/underscore, 1-30 chars (e.g. M, F, ORA_INTERSEX)",
            },
        },
        default_source_system_owner="HCMQA-001",
        default_source_system_id="PERSON_LEG_{row_index}",
        output_filename_template="PersonLegislativeData.dat",
        output_header="METADATA|PersonLegislativeData|SourceSystemOwner|SourceSystemId|PersonNumber|LegislationCode|EffectiveStartDate|EffectiveEndDate|GUID|HighestEducationLevel|MaritalStatus|MaritalStatusDate|Sex",
        output_template=(
            "MERGE|PersonLegislativeData|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|"
            "{PERSON_NUMBER}|{LEGISLATION_CODE}|"
            "{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}|"
            "{GUID}|{HIGHEST_EDUCATION_LEVEL}|"
            "{MARITAL_STATUS}|{MARITAL_STATUS_DATE}|"
            "{SEX}"
        ),
        description="Person Legislative Data object migration file for Oracle Fusion HCM Workforce Structures.",
    ),

    "PersonName": ObjectDefinition( # type: ignore
        name="PersonName",
        aliases=["person_name", "personname", "name", "person name"],
        required_columns=[
            "SOURCE_SYSTEM_OWNER",
            "SOURCE_SYSTEM_ID",
            "PERSON_NUMBER",
            "NAME_TYPE",
            "EFFECTIVE_START_DATE",
            "LAST_NAME",
            "LEGISLATION_CODE",
        ],
        optional_columns=[
            "GUID",
            "CHAR_SET_CONTEXT",
            "TITLE",
            "SUFFIX",
            "PREVIOUS_LAST_NAME",
            "MILITARY_RANK",
            "PRE_NAME_ADJUNCT",
            "KNOWN_AS",
            "HONORS",
            "MIDDLE_NAMES",
            "FIRST_NAME",
            "EFFECTIVE_END_DATE",
        ],
        unique_columns=[
            "PERSON_NUMBER",
            "NAME_TYPE",
            "SOURCE_SYSTEM_ID",
        ],
        date_columns=[
            "EFFECTIVE_START_DATE",
            "EFFECTIVE_END_DATE",
        ],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "PERSON_NUMBER": ["PersonNumber", "person_number", "Person_Number"],
            "NAME_TYPE": ["NameType", "name_type", "Name_Type", "NameTypCode", "name_type_code"],
            "EFFECTIVE_START_DATE": ["EffectiveStartDate", "effective_start_date", "StartDate", "start_date"],
            "EFFECTIVE_END_DATE": ["EffectiveEndDate", "effective_end_date", "EndDate", "end_date"],
            "LAST_NAME": [
                "LastName", "last_name", "Last_Name",
                "Surname", "surname", "FamilyName", "family_name",
            ],
            "LEGISLATION_CODE": [
                "LegislationCode", "legislation_code", "Legislation_Code",
                "LegCode", "leg_code",
            ],
            "GUID": ["GUID", "guid", "GlobalUniqueIdentifier", "global_unique_identifier"],
            "CHAR_SET_CONTEXT": [
                "CharSetContext", "char_set_context", "Char_Set_Context",
                "CharacterSetContext", "character_set_context",
            ],
            "TITLE": ["Title", "title", "Salutation", "salutation"],
            "SUFFIX": ["Suffix", "suffix", "NameSuffix", "name_suffix"],
            "PREVIOUS_LAST_NAME": [
                "PreviousLastName", "previous_last_name", "Previous_Last_Name",
                "MaidenName", "maiden_name", "PrevLastName", "prev_last_name",
            ],
            "MILITARY_RANK": [
                "MilitaryRank", "military_rank", "Military_Rank",
                "MilRank", "mil_rank",
            ],
            "PRE_NAME_ADJUNCT": [
                "PreNameAdjunct", "pre_name_adjunct", "Pre_Name_Adjunct",
                "PreName", "pre_name",
            ],
            "KNOWN_AS": ["KnownAs", "known_as", "Known_As", "PreferredName", "preferred_name"],
            "HONORS": ["Honors", "honors", "Honours", "honours", "Honour", "honor"],
            "MIDDLE_NAMES": [
                "MiddleNames", "middle_names", "Middle_Names",
                "MiddleName", "middle_name",
            ],
            "FIRST_NAME": [
                "FirstName", "first_name", "First_Name",
                "GivenName", "given_name",
            ],
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
            "PERSON_NUMBER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "PERSON_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "NAME_TYPE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "NAME_TYPE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date",
            },
            "LAST_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 150,
                "error_msg": "LAST_NAME must be 1-150 chars",
            },
            "LEGISLATION_CODE": {
                "required": True,
                "min_length": 2,
                "max_length": 2,
                "regex": r"^[A-Z]{2}$",
                "error_msg": "LEGISLATION_CODE must be a 2-letter ISO country code (e.g. IN, US, GB)",
            },
            "GUID": {
                "required": False,
                "min_length": 1,
                "max_length": 64,
                "regex": r"^[A-Za-z0-9_\-]+$",
                "error_msg": "GUID must be alphanumeric with underscores/dashes, 1-64 chars",
            },
            "CHAR_SET_CONTEXT": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "CHAR_SET_CONTEXT must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "TITLE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "TITLE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "SUFFIX": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SUFFIX must be 1-30 chars",
            },
            "PREVIOUS_LAST_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 150,
                "error_msg": "PREVIOUS_LAST_NAME must be 1-150 chars",
            },
            "MILITARY_RANK": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "MILITARY_RANK must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "PRE_NAME_ADJUNCT": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "PRE_NAME_ADJUNCT must be 1-30 chars",
            },
            "KNOWN_AS": {
                "required": False,
                "min_length": 1,
                "max_length": 80,
                "error_msg": "KNOWN_AS must be 1-80 chars",
            },
            "HONORS": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "HONORS must be 1-30 chars",
            },
            "MIDDLE_NAMES": {
                "required": False,
                "min_length": 1,
                "max_length": 60,
                "error_msg": "MIDDLE_NAMES must be 1-60 chars",
            },
            "FIRST_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 150,
                "error_msg": "FIRST_NAME must be 1-150 chars",
            },
            "EFFECTIVE_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_END_DATE must be a valid date",
            },
        },
        default_source_system_owner="HCMQA-001",
        default_source_system_id="PERSON_NAME_{row_index}",
        output_filename_template="PersonName.dat",
        output_header="METADATA|PersonName|SourceSystemOwner|SourceSystemId|PersonNumber|NameType|EffectiveStartDate|EffectiveEndDate|LastName|LegislationCode|GUID|CharSetContext|Title|Suffix|PreviousLastName|MilitaryRank|PreNameAdjunct|KnownAs|Honors|MiddleNames|FirstName",
        output_template=(
            "MERGE|PersonName|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|"
            "{PERSON_NUMBER}|{NAME_TYPE}|"
            "{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}|"
            "{LAST_NAME}|{LEGISLATION_CODE}|"
            "{GUID}|{CHAR_SET_CONTEXT}|"
            "{TITLE}|{SUFFIX}|{PREVIOUS_LAST_NAME}|"
            "{MILITARY_RANK}|{PRE_NAME_ADJUNCT}|"
            "{KNOWN_AS}|{HONORS}|{MIDDLE_NAMES}|{FIRST_NAME}"
        ),
        description="Person Name object migration file for Oracle Fusion HCM Workforce Structures.",
    ),

    "WorkRelationship": ObjectDefinition( # type: ignore
        name="WorkRelationship",
        aliases=["work_relationship", "workrelationship", "work relationship", "employment"],
        required_columns=[
            "SOURCE_SYSTEM_OWNER",
            "SOURCE_SYSTEM_ID",
            "PERSON_NUMBER",
            "DATE_START",
            "WORKER_TYPE",
            "LEGAL_EMPLOYER_NAME",
            "PRIMARY_FLAG",
        ],
        optional_columns=[
            "ACTION_CODE",
            "ACTUAL_TERMINATION_DATE",
            "CANCEL_WORK_RELATIONSHIP_FLAG",
            "COMMENTS",
            "CORRECT_TERMINATION_FLAG",
            "DATE_FOR_PRIMARY_FLAG_CHANGE",
            "DATE_OF_DEATH",
            "ENTERPRISE_SENIORITY_DATE",
            "GLOBAL_TRANSFER_FLAG",
            "HIDE_UNTIL_DATE",
            "LAST_WORKING_DATE",
            "LEGAL_EMPLOYER_SENIORITY_DATE",
            "NEW_START_DATE",
            "NOTIFIED_TERMINATION_DATE",
            "PROJECTED_TERMINATION_DATE",
            "READY_TO_CONVERT",
            "REASON_CODE",
            "REHIRE_AUTHORIZER_PERSON_ID",
            "REHIRE_AUTHORIZOR",
            "REHIRE_REASON",
            "REVERSE_TERMINATION_FLAG",
            "REVOKE_USER_ACCESS",
            "TERMINATE_WORK_RELATIONSHIP_FLAG",
            "WORKER_COMMENTS",
            "WORKER_NUMBER",
            "GUID",
        ],
        unique_columns=[
            "PERSON_NUMBER",
            "DATE_START",
            "SOURCE_SYSTEM_ID",
        ],
        date_columns=[
            "DATE_START",
            "ACTUAL_TERMINATION_DATE",
            "DATE_FOR_PRIMARY_FLAG_CHANGE",
            "DATE_OF_DEATH",
            "ENTERPRISE_SENIORITY_DATE",
            "HIDE_UNTIL_DATE",
            "LAST_WORKING_DATE",
            "LEGAL_EMPLOYER_SENIORITY_DATE",
            "NEW_START_DATE",
            "NOTIFIED_TERMINATION_DATE",
            "PROJECTED_TERMINATION_DATE",
        ],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "PERSON_NUMBER": ["PersonNumber", "person_number", "Person_Number"],
            "DATE_START": ["DateStart", "date_start", "Date_Start", "StartDate", "start_date", "HireDate", "hire_date"],
            "WORKER_TYPE": ["WorkerType", "worker_type", "Worker_Type", "EmployeeType", "employee_type"],
            "LEGAL_EMPLOYER_NAME": [
                "LegalEmployerName", "legal_employer_name", "Legal_Employer_Name",
                "LegalEmployer", "legal_employer",
            ],
            "PRIMARY_FLAG": ["PrimaryFlag", "primary_flag", "Primary_Flag", "IsPrimary", "is_primary"],
            "ACTION_CODE": ["ActionCode", "action_code", "Action_Code"],
            "ACTUAL_TERMINATION_DATE": [
                "ActualTerminationDate", "actual_termination_date",
                "Actual_Termination_Date", "TerminationDate", "termination_date",
            ],
            "CANCEL_WORK_RELATIONSHIP_FLAG": [
                "CancelWorkRelationshipFlag", "cancel_work_relationship_flag",
                "Cancel_Work_Relationship_Flag", "CancelFlag", "cancel_flag",
            ],
            "COMMENTS": ["Comments", "comments", "Comment", "comment", "Notes", "notes"],
            "CORRECT_TERMINATION_FLAG": [
                "CorrectTerminationFlag", "correct_termination_flag",
                "Correct_Termination_Flag", "CorrectTermFlag", "correct_term_flag",
            ],
            "DATE_FOR_PRIMARY_FLAG_CHANGE": [
                "DateForPrimaryFlagChange", "date_for_primary_flag_change",
                "Date_For_Primary_Flag_Change", "PrimaryFlagChangeDate", "primary_flag_change_date",
            ],
            "DATE_OF_DEATH": [
                "DateOfDeath", "date_of_death", "Date_Of_Death",
                "DOD", "dod", "DeathDate", "death_date",
            ],
            "ENTERPRISE_SENIORITY_DATE": [
                "EnterpriseSeniorityDate", "enterprise_seniority_date",
                "Enterprise_Seniority_Date", "SeniorityDate", "seniority_date",
            ],
            "GLOBAL_TRANSFER_FLAG": [
                "GlobalTransferFlag", "global_transfer_flag",
                "Global_Transfer_Flag", "GlobalTransfer", "global_transfer",
            ],
            "HIDE_UNTIL_DATE": [
                "HideUntilDate", "hide_until_date", "Hide_Until_Date",
                "HideDate", "hide_date",
            ],
            "LAST_WORKING_DATE": [
                "LastWorkingDate", "last_working_date", "Last_Working_Date",
                "LastDayWorked", "last_day_worked",
            ],
            "LEGAL_EMPLOYER_SENIORITY_DATE": [
                "LegalEmployerSeniorityDate", "legal_employer_seniority_date",
                "Legal_Employer_Seniority_Date", "LegalEmpSeniorityDate", "legal_emp_seniority_date",
            ],
            "NEW_START_DATE": [
                "NewStartDate", "new_start_date", "New_Start_Date",
                "RevisedStartDate", "revised_start_date",
            ],
            "NOTIFIED_TERMINATION_DATE": [
                "NotifiedTerminationDate", "notified_termination_date",
                "Notified_Termination_Date", "NoticeDate", "notice_date",
            ],
            "PROJECTED_TERMINATION_DATE": [
                "ProjectedTerminationDate", "projected_termination_date",
                "Projected_Termination_Date", "ProjectedTermDate", "projected_term_date",
            ],
            "READY_TO_CONVERT": [
                "ReadyToConvert", "ready_to_convert", "Ready_To_Convert",
                "ConvertFlag", "convert_flag",
            ],
            "REASON_CODE": ["ReasonCode", "reason_code", "Reason_Code", "ActionReasonCode", "action_reason_code"],
            "REHIRE_AUTHORIZER_PERSON_ID": [
                "RehireAuthorizerPersonId", "rehire_authorizer_person_id",
                "Rehire_Authorizer_Person_Id", "RehireAuthorizerId", "rehire_authorizer_id",
            ],
            "REHIRE_AUTHORIZOR": [
                "RehireAuthorizor", "rehire_authorizor", "Rehire_Authorizor",
                "RehireAuthorizer", "rehire_authorizer",
            ],
            "REHIRE_REASON": [
                "RehireReason", "rehire_reason", "Rehire_Reason",
                "RehireReasonCode", "rehire_reason_code",
            ],
            "REVERSE_TERMINATION_FLAG": [
                "ReverseTerminationFlag", "reverse_termination_flag",
                "Reverse_Termination_Flag", "ReverseTermFlag", "reverse_term_flag",
            ],
            "REVOKE_USER_ACCESS": [
                "RevokeUserAccess", "revoke_user_access", "Revoke_User_Access",
                "RevokeAccess", "revoke_access",
            ],
            "TERMINATE_WORK_RELATIONSHIP_FLAG": [
                "TerminateWorkRelationshipFlag", "terminate_work_relationship_flag",
                "Terminate_Work_Relationship_Flag", "TerminateFlag", "terminate_flag",
            ],
            "WORKER_COMMENTS": [
                "WorkerComments", "worker_comments", "Worker_Comments",
                "EmpComments", "emp_comments",
            ],
            "WORKER_NUMBER": [
                "WorkerNumber", "worker_number", "Worker_Number",
                "EmployeeNumber", "employee_number",
            ],
            "GUID": ["GUID", "guid", "GlobalUniqueIdentifier", "global_unique_identifier"],
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
            "PERSON_NUMBER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "PERSON_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "DATE_START": {
                "required": True,
                "data_type": "date",
                "error_msg": "DATE_START must be a valid date",
            },
            "WORKER_TYPE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "WORKER_TYPE must be uppercase alphanumeric/underscore, 1-30 chars (e.g. E for Employee, C for Contingent Worker)",
            },
            "LEGAL_EMPLOYER_NAME": {
                "required": True,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "LEGAL_EMPLOYER_NAME must be 1-240 chars",
            },
            "PRIMARY_FLAG": {
                "required": True,
                "regex": r"^[YN]$",
                "error_msg": "PRIMARY_FLAG must be Y (Yes) or N (No)",
            },
            "ACTION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ACTION_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "ACTUAL_TERMINATION_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "ACTUAL_TERMINATION_DATE must be a valid date",
            },
            "CANCEL_WORK_RELATIONSHIP_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "CANCEL_WORK_RELATIONSHIP_FLAG must be Y (Yes) or N (No)",
            },
            "COMMENTS": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "COMMENTS must be 1-240 chars",
            },
            "CORRECT_TERMINATION_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "CORRECT_TERMINATION_FLAG must be Y (Yes) or N (No)",
            },
            "DATE_FOR_PRIMARY_FLAG_CHANGE": {
                "required": False,
                "data_type": "date",
                "error_msg": "DATE_FOR_PRIMARY_FLAG_CHANGE must be a valid date",
            },
            "DATE_OF_DEATH": {
                "required": False,
                "data_type": "date",
                "error_msg": "DATE_OF_DEATH must be a valid date",
            },
            "ENTERPRISE_SENIORITY_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "ENTERPRISE_SENIORITY_DATE must be a valid date",
            },
            "GLOBAL_TRANSFER_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "GLOBAL_TRANSFER_FLAG must be Y (Yes) or N (No)",
            },
            "HIDE_UNTIL_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "HIDE_UNTIL_DATE must be a valid date",
            },
            "LAST_WORKING_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "LAST_WORKING_DATE must be a valid date",
            },
            "LEGAL_EMPLOYER_SENIORITY_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "LEGAL_EMPLOYER_SENIORITY_DATE must be a valid date",
            },
            "NEW_START_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "NEW_START_DATE must be a valid date",
            },
            "NOTIFIED_TERMINATION_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "NOTIFIED_TERMINATION_DATE must be a valid date",
            },
            "PROJECTED_TERMINATION_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "PROJECTED_TERMINATION_DATE must be a valid date",
            },
            "READY_TO_CONVERT": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "READY_TO_CONVERT must be Y (Yes) or N (No)",
            },
            "REASON_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "REASON_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "REHIRE_AUTHORIZER_PERSON_ID": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "REHIRE_AUTHORIZER_PERSON_ID must be 1-30 chars",
            },
            "REHIRE_AUTHORIZOR": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "REHIRE_AUTHORIZOR must be 1-240 chars",
            },
            "REHIRE_REASON": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "REHIRE_REASON must be 1-240 chars",
            },
            "REVERSE_TERMINATION_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "REVERSE_TERMINATION_FLAG must be Y (Yes) or N (No)",
            },
            "REVOKE_USER_ACCESS": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "REVOKE_USER_ACCESS must be Y (Yes) or N (No)",
            },
            "TERMINATE_WORK_RELATIONSHIP_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "TERMINATE_WORK_RELATIONSHIP_FLAG must be Y (Yes) or N (No)",
            },
            "WORKER_COMMENTS": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "WORKER_COMMENTS must be 1-240 chars",
            },
            "WORKER_NUMBER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "WORKER_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "GUID": {
                "required": False,
                "min_length": 1,
                "max_length": 64,
                "regex": r"^[A-Za-z0-9_\-]+$",
                "error_msg": "GUID must be alphanumeric with underscores/dashes, 1-64 chars",
            },
        },
        default_source_system_owner="HCMQA-001",
        default_source_system_id="WORK_REL_{row_index}",
        output_filename_template="WorkRelationship.dat",
        output_header="METADATA|WorkRelationship|SourceSystemOwner|SourceSystemId|PersonNumber|DateStart|WorkerType|LegalEmployerName|PrimaryFlag|ActionCode|ActualTerminationDate|CancelWorkRelationshipFlag|Comments|CorrectTerminationFlag|DateForPrimaryFlagChange|DateOfDeath|EnterpriseSeniorityDate|GlobalTransferFlag|HideUntilDate|LastWorkingDate|LegalEmployerSeniorityDate|NewStartDate|NotifiedTerminationDate|ProjectedTerminationDate|ReadyToConvert|ReasonCode|RehireAuthorizerPersonId|RehireAuthorizor|RehireReason|ReverseTerminationFlag|RevokeUserAccess|TerminateWorkRelationshipFlag|WorkerComments|WorkerNumber|GUID",
        output_template=(
            "MERGE|WorkRelationship|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|"
            "{PERSON_NUMBER}|{DATE_START}|{WORKER_TYPE}|{LEGAL_EMPLOYER_NAME}|{PRIMARY_FLAG}|"
            "{ACTION_CODE}|{ACTUAL_TERMINATION_DATE}|{CANCEL_WORK_RELATIONSHIP_FLAG}|"
            "{COMMENTS}|{CORRECT_TERMINATION_FLAG}|{DATE_FOR_PRIMARY_FLAG_CHANGE}|"
            "{DATE_OF_DEATH}|{ENTERPRISE_SENIORITY_DATE}|{GLOBAL_TRANSFER_FLAG}|"
            "{HIDE_UNTIL_DATE}|{LAST_WORKING_DATE}|{LEGAL_EMPLOYER_SENIORITY_DATE}|"
            "{NEW_START_DATE}|{NOTIFIED_TERMINATION_DATE}|{PROJECTED_TERMINATION_DATE}|"
            "{READY_TO_CONVERT}|{REASON_CODE}|{REHIRE_AUTHORIZER_PERSON_ID}|"
            "{REHIRE_AUTHORIZOR}|{REHIRE_REASON}|{REVERSE_TERMINATION_FLAG}|"
            "{REVOKE_USER_ACCESS}|{TERMINATE_WORK_RELATIONSHIP_FLAG}|"
            "{WORKER_COMMENTS}|{WORKER_NUMBER}|{GUID}"
        ),
        description="Work Relationship object migration file for Oracle Fusion HCM Workforce Structures.",
    ),

    "Assignment": ObjectDefinition( # type: ignore
        name="Assignment",
        aliases=["assignment", "assignments", "work_assignment", "employee_assignment"],
        required_columns=[
            "SOURCE_SYSTEM_OWNER",
            "SOURCE_SYSTEM_ID",
            "ASSIGNMENT_NUMBER",
            "WORK_TERMS_NUMBER",
            "EFFECTIVE_LATEST_CHANGE",
            "EFFECTIVE_SEQUENCE",
            "EFFECTIVE_START_DATE",
            "ASSIGNMENT_STATUS_TYPE_CODE",
            "ASSIGNMENT_TYPE",
            "BUSINESS_UNIT_SHORT_CODE",
            "PRIMARY_FLAG",
            "PERSON_NUMBER",
        ],
        optional_columns=[
            "ACTION_CODE",
            "EFFECTIVE_END_DATE",
            "ASSIGNMENT_NAME",
            "BARGAINING_UNIT_CODE",
            "BILLING_TITLE",
            "COLLECTIVE_AGREEMENT_ID_CODE",
            "CONTRACT_ID",
            "DATE_PROBATION_END",
            "REPORTING_ESTABLISHMENT",
            "LEGAL_EMPLOYER_NAME",
            "GRADE_CODE",
            "GRADE_LADDER_PGM_NAME",
            "HOURLY_SALARIED_CODE",
            "INTERNAL_BUILDING",
            "INTERNAL_FLOOR",
            "INTERNAL_LOCATION",
            "INTERNAL_MAILSTOP",
            "INTERNAL_OFFICE_NUMBER",
            "JOB_CODE",
            "LABOUR_UNION_MEMBER_FLAG",
            "LOCATION_CODE",
            "MANAGER_FLAG",
            "NORMAL_HOURS",
            "NOTICE_PERIOD",
            "DEPARTMENT_NAME",
            "DATE_START",
            "PERSON_TYPE_CODE",
            "SYSTEM_PERSON_TYPE",
            "POSITION_CODE",
            "POSITION_OVERRIDE_FLAG",
            "PRIMARY_ASSIGNMENT_FLAG",
            "PROBATION_PERIOD",
            "PROJECT_TITLE",
            "PROJECTED_END_DATE",
            "PROJECTED_START_DATE",
            "PROPOSED_USER_PERSON_TYPE",
            "PROPOSED_WORKER_TYPE",
            "REASON_CODE",
            "RETIREMENT_AGE",
            "RETIREMENT_DATE",
            "SPECIAL_CEILING_STEP",
            "TAX_ADDRESS_ID",
            "END_TIME",
            "START_TIME",
            "WORK_AT_HOME_FLAG",
            "FREEZE_START_DATE",
            "FREEZE_UNTIL_DATE",
            "GUID",
            "PEOPLE_GROUP",
            "GSP_ELIGIBILITY_FLAG",
            "DEFAULT_EXPENSE_ACCOUNT",
            "UNION_ID",
            "UNION_NAME",
            "OVERTIME_PERIOD_NAME",
            "SOURCE_ASSIGNMENT_NUMBER",
            "TAX_REPORTING_UNIT",
            "CONTRACT_NUMBER",
            "TERMINATION_DATE",
            "NOTIFICATION_DATE",
            "LAST_WORKING_DATE",
            "REHIRE_AUTHORIZER_PERSON_NUMBER",
            "TERMINATE_ASSIGNMENT_FLAG",
            "CORRECT_ASSIGNMENT_TERMINATION_FLAG",
            "REVERSE_ASSIGNMENT_TERMINATION_FLAG",
            "REQUISITION_NUMBER",
            "CANDIDATE_NUMBER",
            "ADJUSTED_FTE",
            "ANNUAL_WORKING_DURATION",
            "ANNUAL_WORKING_DURATION_UNITS",
            "ANNUAL_WORKING_RATIO",
            "STANDARD_HOURS",
            "STD_ANNUAL_WORKING_DURATION",
            "NOTES",
        ],
        unique_columns=[
            "ASSIGNMENT_NUMBER",
            "PERSON_NUMBER",
            "EFFECTIVE_START_DATE",
            "SOURCE_SYSTEM_ID",
        ],
        date_columns=[
            "EFFECTIVE_START_DATE",
            "EFFECTIVE_END_DATE",
            "DATE_PROBATION_END",
            "DATE_START",
            "PROJECTED_END_DATE",
            "PROJECTED_START_DATE",
            "RETIREMENT_DATE",
            "FREEZE_START_DATE",
            "FREEZE_UNTIL_DATE",
            "TERMINATION_DATE",
            "NOTIFICATION_DATE",
            "LAST_WORKING_DATE",
        ],
        column_aliases={
            "SOURCE_SYSTEM_OWNER": ["SourceSystemOwner", "source_system_owner"],
            "SOURCE_SYSTEM_ID": ["SourceSystemId", "source_system_id"],
            "ASSIGNMENT_NUMBER": [
                "AssignmentNumber", "assignment_number", "Assignment_Number",
                "AssignmentNum", "assignment_num",
            ],
            "WORK_TERMS_NUMBER": [
                "WorkTermsNumber", "work_terms_number", "Work_Terms_Number",
                "WorkTermsNum", "work_terms_num",
            ],
            "EFFECTIVE_LATEST_CHANGE": [
                "EffectiveLatestChange", "effective_latest_change",
                "Effective_Latest_Change", "LatestChange", "latest_change",
            ],
            "EFFECTIVE_SEQUENCE": [
                "EffectiveSequence", "effective_sequence",
                "Effective_Sequence", "EffSeq", "eff_seq",
            ],
            "EFFECTIVE_START_DATE": ["EffectiveStartDate", "effective_start_date", "StartDate", "start_date"],
            "EFFECTIVE_END_DATE": ["EffectiveEndDate", "effective_end_date", "EndDate", "end_date"],
            "ASSIGNMENT_STATUS_TYPE_CODE": [
                "AssignmentStatusTypeCode", "assignment_status_type_code",
                "Assignment_Status_Type_Code", "AssignmentStatusCode", "assignment_status_code",
            ],
            "ASSIGNMENT_TYPE": [
                "AssignmentType", "assignment_type", "Assignment_Type",
                "AssignType", "assign_type",
            ],
            "BUSINESS_UNIT_SHORT_CODE": [
                "BusinessUnitShortCode", "business_unit_short_code",
                "Business_Unit_Short_Code", "BUShortCode", "bu_short_code",
            ],
            "PRIMARY_FLAG": ["PrimaryFlag", "primary_flag", "Primary_Flag", "IsPrimary", "is_primary"],
            "PERSON_NUMBER": ["PersonNumber", "person_number", "Person_Number"],
            "ACTION_CODE": ["ActionCode", "action_code", "Action_Code"],
            "ASSIGNMENT_NAME": [
                "AssignmentName", "assignment_name", "Assignment_Name",
                "AssignName", "assign_name",
            ],
            "BARGAINING_UNIT_CODE": [
                "BargainingUnitCode", "bargaining_unit_code",
                "Bargaining_Unit_Code", "BargUnitCode", "barg_unit_code",
            ],
            "BILLING_TITLE": ["BillingTitle", "billing_title", "Billing_Title"],
            "COLLECTIVE_AGREEMENT_ID_CODE": [
                "CollectiveAgreementIdCode", "collective_agreement_id_code",
                "Collective_Agreement_Id_Code", "CollAgmtIdCode", "coll_agmt_id_code",
            ],
            "CONTRACT_ID": ["ContractId", "contract_id", "Contract_Id", "ContractID", "contract_ID"],
            "DATE_PROBATION_END": [
                "DateProbationEnd", "date_probation_end", "Date_Probation_End",
                "ProbationEndDate", "probation_end_date",
            ],
            "REPORTING_ESTABLISHMENT": [
                "ReportingEstablishment", "reporting_establishment",
                "Reporting_Establishment", "ReportEstablishment", "report_establishment",
            ],
            "LEGAL_EMPLOYER_NAME": [
                "LegalEmployerName", "legal_employer_name", "Legal_Employer_Name",
                "LegalEmployer", "legal_employer",
            ],
            "GRADE_CODE": ["GradeCode", "grade_code", "Grade_Code", "Grade", "grade"],
            "GRADE_LADDER_PGM_NAME": [
                "GradeLadderPgmName", "grade_ladder_pgm_name",
                "Grade_Ladder_Pgm_Name", "GradeLadderName", "grade_ladder_name",
            ],
            "HOURLY_SALARIED_CODE": [
                "HourlySalariedCode", "hourly_salaried_code",
                "Hourly_Salaried_Code", "HrlySalCode", "hrly_sal_code",
            ],
            "INTERNAL_BUILDING": [
                "InternalBuilding", "internal_building",
                "Internal_Building", "IntBuilding", "int_building",
            ],
            "INTERNAL_FLOOR": [
                "InternalFloor", "internal_floor", "Internal_Floor",
                "IntFloor", "int_floor",
            ],
            "INTERNAL_LOCATION": [
                "InternalLocation", "internal_location", "Internal_Location",
                "IntLocation", "int_location",
            ],
            "INTERNAL_MAILSTOP": [
                "InternalMailstop", "internal_mailstop", "Internal_Mailstop",
                "InternalMailStop", "internal_mail_stop", "MailStop", "mail_stop",
            ],
            "INTERNAL_OFFICE_NUMBER": [
                "InternalOfficeNumber", "internal_office_number",
                "Internal_Office_Number", "OfficeNumber", "office_number",
            ],
            "JOB_CODE": ["JobCode", "job_code", "Job_Code", "Job", "job"],
            "LABOUR_UNION_MEMBER_FLAG": [
                "LabourUnionMemberFlag", "labour_union_member_flag",
                "Labour_Union_Member_Flag", "LaborUnionMemberFlag", "labor_union_member_flag",
                "UnionMemberFlag", "union_member_flag",
            ],
            "LOCATION_CODE": ["LocationCode", "location_code", "Location_Code", "Location", "location"],
            "MANAGER_FLAG": ["ManagerFlag", "manager_flag", "Manager_Flag", "IsManager", "is_manager"],
            "NORMAL_HOURS": ["NormalHours", "normal_hours", "Normal_Hours", "StdHours", "std_hours"],
            "NOTICE_PERIOD": ["NoticePeriod", "notice_period", "Notice_Period"],
            "DEPARTMENT_NAME": [
                "DepartmentName", "department_name", "Department_Name",
                "DeptName", "dept_name",
            ],
            "DATE_START": ["DateStart", "date_start", "Date_Start", "HireDate", "hire_date"],
            "PERSON_TYPE_CODE": [
                "PersonTypeCode", "person_type_code", "Person_Type_Code",
                "PersonType", "person_type",
            ],
            "SYSTEM_PERSON_TYPE": [
                "SystemPersonType", "system_person_type", "System_Person_Type",
                "SysPersonType", "sys_person_type",
            ],
            "POSITION_CODE": ["PositionCode", "position_code", "Position_Code", "Position", "position"],
            "POSITION_OVERRIDE_FLAG": [
                "PositionOverrideFlag", "position_override_flag",
                "Position_Override_Flag", "PosOverrideFlag", "pos_override_flag",
            ],
            "PRIMARY_ASSIGNMENT_FLAG": [
                "PrimaryAssignmentFlag", "primary_assignment_flag",
                "Primary_Assignment_Flag", "PrimaryAssignFlag", "primary_assign_flag",
            ],
            "PROBATION_PERIOD": ["ProbationPeriod", "probation_period", "Probation_Period"],
            "PROJECT_TITLE": ["ProjectTitle", "project_title", "Project_Title", "ProjTitle", "proj_title"],
            "PROJECTED_END_DATE": [
                "ProjectedEndDate", "projected_end_date", "Projected_End_Date",
                "ProjEndDate", "proj_end_date",
            ],
            "PROJECTED_START_DATE": [
                "ProjectedStartDate", "projected_start_date", "Projected_Start_Date",
                "ProjStartDate", "proj_start_date",
            ],
            "PROPOSED_USER_PERSON_TYPE": [
                "ProposedUserPersonType", "proposed_user_person_type",
                "Proposed_User_Person_Type", "PropUserPersonType", "prop_user_person_type",
            ],
            "PROPOSED_WORKER_TYPE": [
                "ProposedWorkerType", "proposed_worker_type",
                "Proposed_Worker_Type", "PropWorkerType", "prop_worker_type",
            ],
            "REASON_CODE": ["ReasonCode", "reason_code", "Reason_Code", "ActionReasonCode", "action_reason_code"],
            "RETIREMENT_AGE": ["RetirementAge", "retirement_age", "Retirement_Age", "RetireAge", "retire_age"],
            "RETIREMENT_DATE": ["RetirementDate", "retirement_date", "Retirement_Date", "RetireDate", "retire_date"],
            "SPECIAL_CEILING_STEP": [
                "SpecialCeilingStep", "special_ceiling_step",
                "Special_Ceiling_Step", "CeilingStep", "ceiling_step",
            ],
            "TAX_ADDRESS_ID": [
                "TaxAddressId", "tax_address_id", "Tax_Address_Id",
                "TaxAddrId", "tax_addr_id",
            ],
            "END_TIME": ["EndTime", "end_time", "End_Time"],
            "START_TIME": ["StartTime", "start_time", "Start_Time"],
            "WORK_AT_HOME_FLAG": [
                "WorkAtHomeFlag", "work_at_home_flag", "Work_At_Home_Flag",
                "WFHFlag", "wfh_flag", "RemoteFlag", "remote_flag",
            ],
            "FREEZE_START_DATE": [
                "FreezeStartDate", "freeze_start_date", "Freeze_Start_Date",
                "FreezeFrom", "freeze_from",
            ],
            "FREEZE_UNTIL_DATE": [
                "FreezeUntilDate", "freeze_until_date", "Freeze_Until_Date",
                "FreezeTo", "freeze_to",
            ],
            "GUID": ["GUID", "guid", "GlobalUniqueIdentifier", "global_unique_identifier"],
            "PEOPLE_GROUP": ["PeopleGroup", "people_group", "People_Group", "PplGroup", "ppl_group"],
            "GSP_ELIGIBILITY_FLAG": [
                "GspEligibilityFlag", "gsp_eligibility_flag", "GSP_Eligibility_Flag",
                "GspFlag", "gsp_flag",
            ],
            "DEFAULT_EXPENSE_ACCOUNT": [
                "DefaultExpenseAccount", "default_expense_account",
                "Default_Expense_Account", "ExpenseAccount", "expense_account",
            ],
            "UNION_ID": ["UnionId", "union_id", "Union_Id", "UnionID", "union_ID"],
            "UNION_NAME": ["UnionName", "union_name", "Union_Name", "Union", "union"],
            "OVERTIME_PERIOD_NAME": [
                "OvertimePeriodName", "overtime_period_name",
                "Overtime_Period_Name", "OTPeriodName", "ot_period_name",
            ],
            "SOURCE_ASSIGNMENT_NUMBER": [
                "SourceAssignmentNumber", "source_assignment_number",
                "Source_Assignment_Number", "SrcAssignmentNum", "src_assignment_num",
            ],
            "TAX_REPORTING_UNIT": [
                "TaxReportingUnit", "tax_reporting_unit", "Tax_Reporting_Unit",
                "TRU", "tru",
            ],
            "CONTRACT_NUMBER": [
                "ContractNumber", "contract_number", "Contract_Number",
                "ContractNum", "contract_num",
            ],
            "TERMINATION_DATE": [
                "TerminationDate", "termination_date", "Termination_Date",
                "TermDate", "term_date",
            ],
            "NOTIFICATION_DATE": [
                "NotificationDate", "notification_date", "Notification_Date",
                "NoticeDate", "notice_date",
            ],
            "LAST_WORKING_DATE": [
                "LastWorkingDate", "last_working_date", "Last_Working_Date",
                "LastDayWorked", "last_day_worked",
            ],
            "REHIRE_AUTHORIZER_PERSON_NUMBER": [
                "RehireAuthorizerPersonNumber", "rehire_authorizer_person_number",
                "Rehire_Authorizer_Person_Number", "RehireAuthorizerNum", "rehire_authorizer_num",
            ],
            "TERMINATE_ASSIGNMENT_FLAG": [
                "TerminateAssignmentFlag", "terminate_assignment_flag",
                "Terminate_Assignment_Flag", "TermAssignFlag", "term_assign_flag",
            ],
            "CORRECT_ASSIGNMENT_TERMINATION_FLAG": [
                "CorrectAssignmentTerminationFlag", "correct_assignment_termination_flag",
                "Correct_Assignment_Termination_Flag", "CorrectTermFlag", "correct_term_flag",
            ],
            "REVERSE_ASSIGNMENT_TERMINATION_FLAG": [
                "ReverseAssignmentTerminationFlag", "reverse_assignment_termination_flag",
                "Reverse_Assignment_Termination_Flag", "ReverseTermFlag", "reverse_term_flag",
            ],
            "REQUISITION_NUMBER": [
                "RequisitionNumber", "requisition_number", "Requisition_Number",
                "ReqNumber", "req_number", "ReqNum", "req_num",
            ],
            "CANDIDATE_NUMBER": [
                "CandidateNumber", "candidate_number", "Candidate_Number",
                "CandidateNum", "candidate_num",
            ],
            "ADJUSTED_FTE": ["AdjustedFte", "adjusted_fte", "Adjusted_Fte", "AdjFTE", "adj_fte"],
            "ANNUAL_WORKING_DURATION": [
                "AnnualWorkingDuration", "annual_working_duration",
                "Annual_Working_Duration", "AnnWorkDuration", "ann_work_duration",
            ],
            "ANNUAL_WORKING_DURATION_UNITS": [
                "AnnualWorkingDurationUnits", "annual_working_duration_units",
                "Annual_Working_Duration_Units", "AnnWorkDurationUnits", "ann_work_duration_units",
            ],
            "ANNUAL_WORKING_RATIO": [
                "AnnualWorkingRatio", "annual_working_ratio",
                "Annual_Working_Ratio", "AnnWorkRatio", "ann_work_ratio",
            ],
            "STANDARD_HOURS": [
                "StandardHours", "standard_hours", "Standard_Hours",
                "StdHours", "std_hours",
            ],
            "STD_ANNUAL_WORKING_DURATION": [
                "StdAnnualWorkingDuration", "std_annual_working_duration",
                "Std_Annual_Working_Duration", "StdAnnWorkDuration", "std_ann_work_duration",
            ],
            "NOTES": ["Notes", "notes", "Note", "note", "Comments", "comments"],
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
            "ASSIGNMENT_NUMBER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "ASSIGNMENT_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "WORK_TERMS_NUMBER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "WORK_TERMS_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "EFFECTIVE_LATEST_CHANGE": {
                "required": True,
                "regex": r"^[YN]$",
                "error_msg": "EFFECTIVE_LATEST_CHANGE must be Y (Yes) or N (No)",
            },
            "EFFECTIVE_SEQUENCE": {
                "required": True,
                "min_length": 1,
                "max_length": 10,
                "regex": r"^[0-9]+$",
                "error_msg": "EFFECTIVE_SEQUENCE must be a numeric value, 1-10 chars",
            },
            "EFFECTIVE_START_DATE": {
                "required": True,
                "data_type": "date",
                "error_msg": "EFFECTIVE_START_DATE must be a valid date",
            },
            "ASSIGNMENT_STATUS_TYPE_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 80,
                "error_msg": "ASSIGNMENT_STATUS_TYPE_CODE must be 1-80 chars",
            },
            "ASSIGNMENT_TYPE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ASSIGNMENT_TYPE must be uppercase alphanumeric/underscore, 1-30 chars (e.g. E for Employee, C for Contingent Worker)",
            },
            "BUSINESS_UNIT_SHORT_CODE": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "BUSINESS_UNIT_SHORT_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "PRIMARY_FLAG": {
                "required": True,
                "regex": r"^[YN]$",
                "error_msg": "PRIMARY_FLAG must be Y (Yes) or N (No)",
            },
            "PERSON_NUMBER": {
                "required": True,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "PERSON_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "ACTION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ACTION_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "EFFECTIVE_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "EFFECTIVE_END_DATE must be a valid date",
            },
            "ASSIGNMENT_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 80,
                "error_msg": "ASSIGNMENT_NAME must be 1-80 chars",
            },
            "BARGAINING_UNIT_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "BARGAINING_UNIT_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "BILLING_TITLE": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "BILLING_TITLE must be 1-240 chars",
            },
            "COLLECTIVE_AGREEMENT_ID_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 80,
                "error_msg": "COLLECTIVE_AGREEMENT_ID_CODE must be 1-80 chars",
            },
            "CONTRACT_ID": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[0-9]+$",
                "error_msg": "CONTRACT_ID must be a numeric value, 1-30 chars",
            },
            "DATE_PROBATION_END": {
                "required": False,
                "data_type": "date",
                "error_msg": "DATE_PROBATION_END must be a valid date",
            },
            "REPORTING_ESTABLISHMENT": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "REPORTING_ESTABLISHMENT must be 1-240 chars",
            },
            "LEGAL_EMPLOYER_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "LEGAL_EMPLOYER_NAME must be 1-240 chars",
            },
            "GRADE_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "GRADE_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "GRADE_LADDER_PGM_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "GRADE_LADDER_PGM_NAME must be 1-240 chars",
            },
            "HOURLY_SALARIED_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "HOURLY_SALARIED_CODE must be uppercase alphanumeric/underscore, 1-30 chars (e.g. HOURLY, SALARIED)",
            },
            "INTERNAL_BUILDING": {
                "required": False,
                "min_length": 1,
                "max_length": 45,
                "error_msg": "INTERNAL_BUILDING must be 1-45 chars",
            },
            "INTERNAL_FLOOR": {
                "required": False,
                "min_length": 1,
                "max_length": 45,
                "error_msg": "INTERNAL_FLOOR must be 1-45 chars",
            },
            "INTERNAL_LOCATION": {
                "required": False,
                "min_length": 1,
                "max_length": 45,
                "error_msg": "INTERNAL_LOCATION must be 1-45 chars",
            },
            "INTERNAL_MAILSTOP": {
                "required": False,
                "min_length": 1,
                "max_length": 45,
                "error_msg": "INTERNAL_MAILSTOP must be 1-45 chars",
            },
            "INTERNAL_OFFICE_NUMBER": {
                "required": False,
                "min_length": 1,
                "max_length": 45,
                "error_msg": "INTERNAL_OFFICE_NUMBER must be 1-45 chars",
            },
            "JOB_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "JOB_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "LABOUR_UNION_MEMBER_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "LABOUR_UNION_MEMBER_FLAG must be Y (Yes) or N (No)",
            },
            "LOCATION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 60,
                "error_msg": "LOCATION_CODE must be 1-60 chars",
            },
            "MANAGER_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "MANAGER_FLAG must be Y (Yes) or N (No)",
            },
            "NORMAL_HOURS": {
                "required": False,
                "min_length": 1,
                "max_length": 10,
                "regex": r"^[0-9]+(\.[0-9]+)?$",
                "error_msg": "NORMAL_HOURS must be a valid numeric value, 1-10 chars",
            },
            "NOTICE_PERIOD": {
                "required": False,
                "min_length": 1,
                "max_length": 10,
                "regex": r"^[0-9]+$",
                "error_msg": "NOTICE_PERIOD must be a numeric value, 1-10 chars",
            },
            "DEPARTMENT_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "DEPARTMENT_NAME must be 1-240 chars",
            },
            "DATE_START": {
                "required": False,
                "data_type": "date",
                "error_msg": "DATE_START must be a valid date",
            },
            "PERSON_TYPE_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "PERSON_TYPE_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "SYSTEM_PERSON_TYPE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "SYSTEM_PERSON_TYPE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "POSITION_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "POSITION_CODE must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "POSITION_OVERRIDE_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "POSITION_OVERRIDE_FLAG must be Y (Yes) or N (No)",
            },
            "PRIMARY_ASSIGNMENT_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "PRIMARY_ASSIGNMENT_FLAG must be Y (Yes) or N (No)",
            },
            "PROBATION_PERIOD": {
                "required": False,
                "min_length": 1,
                "max_length": 10,
                "regex": r"^[0-9]+$",
                "error_msg": "PROBATION_PERIOD must be a numeric value, 1-10 chars",
            },
            "PROJECT_TITLE": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "PROJECT_TITLE must be 1-240 chars",
            },
            "PROJECTED_END_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "PROJECTED_END_DATE must be a valid date",
            },
            "PROJECTED_START_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "PROJECTED_START_DATE must be a valid date",
            },
            "PROPOSED_USER_PERSON_TYPE": {
                "required": False,
                "min_length": 1,
                "max_length": 80,
                "error_msg": "PROPOSED_USER_PERSON_TYPE must be 1-80 chars",
            },
            "PROPOSED_WORKER_TYPE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "PROPOSED_WORKER_TYPE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "REASON_CODE": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "REASON_CODE must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "RETIREMENT_AGE": {
                "required": False,
                "min_length": 1,
                "max_length": 3,
                "regex": r"^[0-9]+$",
                "error_msg": "RETIREMENT_AGE must be a numeric value, 1-3 chars",
            },
            "RETIREMENT_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "RETIREMENT_DATE must be a valid date",
            },
            "SPECIAL_CEILING_STEP": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "error_msg": "SPECIAL_CEILING_STEP must be 1-30 chars",
            },
            "TAX_ADDRESS_ID": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[0-9]+$",
                "error_msg": "TAX_ADDRESS_ID must be a numeric value, 1-30 chars",
            },
            "END_TIME": {
                "required": False,
                "min_length": 1,
                "max_length": 10,
                "regex": r"^([01]\d|2[0-3]):[0-5]\d$",
                "error_msg": "END_TIME must be a valid time in HH:MM format",
            },
            "START_TIME": {
                "required": False,
                "min_length": 1,
                "max_length": 10,
                "regex": r"^([01]\d|2[0-3]):[0-5]\d$",
                "error_msg": "START_TIME must be a valid time in HH:MM format",
            },
            "WORK_AT_HOME_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "WORK_AT_HOME_FLAG must be Y (Yes) or N (No)",
            },
            "FREEZE_START_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "FREEZE_START_DATE must be a valid date",
            },
            "FREEZE_UNTIL_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "FREEZE_UNTIL_DATE must be a valid date",
            },
            "GUID": {
                "required": False,
                "min_length": 1,
                "max_length": 64,
                "regex": r"^[A-Za-z0-9_\-]+$",
                "error_msg": "GUID must be alphanumeric with underscores/dashes, 1-64 chars",
            },
            "PEOPLE_GROUP": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "PEOPLE_GROUP must be 1-240 chars",
            },
            "GSP_ELIGIBILITY_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "GSP_ELIGIBILITY_FLAG must be Y (Yes) or N (No)",
            },
            "DEFAULT_EXPENSE_ACCOUNT": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "DEFAULT_EXPENSE_ACCOUNT must be 1-240 chars",
            },
            "UNION_ID": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[0-9]+$",
                "error_msg": "UNION_ID must be a numeric value, 1-30 chars",
            },
            "UNION_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "UNION_NAME must be 1-240 chars",
            },
            "OVERTIME_PERIOD_NAME": {
                "required": False,
                "min_length": 1,
                "max_length": 80,
                "error_msg": "OVERTIME_PERIOD_NAME must be 1-80 chars",
            },
            "SOURCE_ASSIGNMENT_NUMBER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "SOURCE_ASSIGNMENT_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "TAX_REPORTING_UNIT": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "TAX_REPORTING_UNIT must be 1-240 chars",
            },
            "CONTRACT_NUMBER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "CONTRACT_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "TERMINATION_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "TERMINATION_DATE must be a valid date",
            },
            "NOTIFICATION_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "NOTIFICATION_DATE must be a valid date",
            },
            "LAST_WORKING_DATE": {
                "required": False,
                "data_type": "date",
                "error_msg": "LAST_WORKING_DATE must be a valid date",
            },
            "REHIRE_AUTHORIZER_PERSON_NUMBER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "REHIRE_AUTHORIZER_PERSON_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "TERMINATE_ASSIGNMENT_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "TERMINATE_ASSIGNMENT_FLAG must be Y (Yes) or N (No)",
            },
            "CORRECT_ASSIGNMENT_TERMINATION_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "CORRECT_ASSIGNMENT_TERMINATION_FLAG must be Y (Yes) or N (No)",
            },
            "REVERSE_ASSIGNMENT_TERMINATION_FLAG": {
                "required": False,
                "regex": r"^[YN]$",
                "error_msg": "REVERSE_ASSIGNMENT_TERMINATION_FLAG must be Y (Yes) or N (No)",
            },
            "REQUISITION_NUMBER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "REQUISITION_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "CANDIDATE_NUMBER": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_-]+$",
                "error_msg": "CANDIDATE_NUMBER must be alphanumeric with underscores/dashes, 1-30 chars",
            },
            "ADJUSTED_FTE": {
                "required": False,
                "min_length": 1,
                "max_length": 10,
                "regex": r"^[0-9]+(\.[0-9]+)?$",
                "error_msg": "ADJUSTED_FTE must be a valid numeric value, 1-10 chars",
            },
            "ANNUAL_WORKING_DURATION": {
                "required": False,
                "min_length": 1,
                "max_length": 10,
                "regex": r"^[0-9]+(\.[0-9]+)?$",
                "error_msg": "ANNUAL_WORKING_DURATION must be a valid numeric value, 1-10 chars",
            },
            "ANNUAL_WORKING_DURATION_UNITS": {
                "required": False,
                "min_length": 1,
                "max_length": 30,
                "regex": r"^[A-Z0-9_]+$",
                "error_msg": "ANNUAL_WORKING_DURATION_UNITS must be uppercase alphanumeric/underscore, 1-30 chars",
            },
            "ANNUAL_WORKING_RATIO": {
                "required": False,
                "min_length": 1,
                "max_length": 10,
                "regex": r"^[0-9]+(\.[0-9]+)?$",
                "error_msg": "ANNUAL_WORKING_RATIO must be a valid numeric value, 1-10 chars",
            },
            "STANDARD_HOURS": {
                "required": False,
                "min_length": 1,
                "max_length": 10,
                "regex": r"^[0-9]+(\.[0-9]+)?$",
                "error_msg": "STANDARD_HOURS must be a valid numeric value, 1-10 chars",
            },
            "STD_ANNUAL_WORKING_DURATION": {
                "required": False,
                "min_length": 1,
                "max_length": 10,
                "regex": r"^[0-9]+(\.[0-9]+)?$",
                "error_msg": "STD_ANNUAL_WORKING_DURATION must be a valid numeric value, 1-10 chars",
            },
            "NOTES": {
                "required": False,
                "min_length": 1,
                "max_length": 240,
                "error_msg": "NOTES must be 1-240 chars",
            },
        },
        default_source_system_owner="HCMQA-001",
        default_source_system_id="ASSIGNMENT_{row_index}",
        output_filename_template="Assignment.dat",
        output_header="METADATA|Assignment|SourceSystemOwner|SourceSystemId|AssignmentNumber|WorkTermsNumber|EffectiveLatestChange|EffectiveSequence|EffectiveStartDate|EffectiveEndDate|AssignmentStatusTypeCode|AssignmentType|BusinessUnitShortCode|PrimaryFlag|PersonNumber|ActionCode|AssignmentName|BargainingUnitCode|BillingTitle|CollectiveAgreementIdCode|ContractId|DateProbationEnd|ReportingEstablishment|LegalEmployerName|GradeCode|GradeLadderPgmName|HourlySalariedCode|InternalBuilding|InternalFloor|InternalLocation|InternalMailstop|InternalOfficeNumber|JobCode|LabourUnionMemberFlag|LocationCode|ManagerFlag|NormalHours|NoticePeriod|DepartmentName|DateStart|PersonTypeCode|SystemPersonType|PositionCode|PositionOverrideFlag|PrimaryAssignmentFlag|ProbationPeriod|ProjectTitle|ProjectedEndDate|ProjectedStartDate|ProposedUserPersonType|ProposedWorkerType|ReasonCode|RetirementAge|RetirementDate|SpecialCeilingStep|TaxAddressId|EndTime|StartTime|WorkAtHomeFlag|FreezeStartDate|FreezeUntilDate|GUID|PeopleGroup|GspEligibilityFlag|DefaultExpenseAccount|UnionId|UnionName|OvertimePeriodName|SourceAssignmentNumber|TaxReportingUnit|ContractNumber|TerminationDate|NotificationDate|LastWorkingDate|RehireAuthorizerPersonNumber|TerminateAssignmentFlag|CorrectAssignmentTerminationFlag|ReverseAssignmentTerminationFlag|RequisitionNumber|CandidateNumber|AdjustedFte|AnnualWorkingDuration|AnnualWorkingDurationUnits|AnnualWorkingRatio|StandardHours|StdAnnualWorkingDuration|Notes",
        output_template=(
            "MERGE|Assignment|{SOURCE_SYSTEM_OWNER}|{SOURCE_SYSTEM_ID}|"
            "{ASSIGNMENT_NUMBER}|{WORK_TERMS_NUMBER}|"
            "{EFFECTIVE_LATEST_CHANGE}|{EFFECTIVE_SEQUENCE}|"
            "{EFFECTIVE_START_DATE}|{EFFECTIVE_END_DATE}|"
            "{ASSIGNMENT_STATUS_TYPE_CODE}|{ASSIGNMENT_TYPE}|"
            "{BUSINESS_UNIT_SHORT_CODE}|{PRIMARY_FLAG}|{PERSON_NUMBER}|"
            "{ACTION_CODE}|{ASSIGNMENT_NAME}|{BARGAINING_UNIT_CODE}|"
            "{BILLING_TITLE}|{COLLECTIVE_AGREEMENT_ID_CODE}|{CONTRACT_ID}|"
            "{DATE_PROBATION_END}|{REPORTING_ESTABLISHMENT}|{LEGAL_EMPLOYER_NAME}|"
            "{GRADE_CODE}|{GRADE_LADDER_PGM_NAME}|{HOURLY_SALARIED_CODE}|"
            "{INTERNAL_BUILDING}|{INTERNAL_FLOOR}|{INTERNAL_LOCATION}|"
            "{INTERNAL_MAILSTOP}|{INTERNAL_OFFICE_NUMBER}|{JOB_CODE}|"
            "{LABOUR_UNION_MEMBER_FLAG}|{LOCATION_CODE}|{MANAGER_FLAG}|"
            "{NORMAL_HOURS}|{NOTICE_PERIOD}|{DEPARTMENT_NAME}|{DATE_START}|"
            "{PERSON_TYPE_CODE}|{SYSTEM_PERSON_TYPE}|{POSITION_CODE}|"
            "{POSITION_OVERRIDE_FLAG}|{PRIMARY_ASSIGNMENT_FLAG}|{PROBATION_PERIOD}|"
            "{PROJECT_TITLE}|{PROJECTED_END_DATE}|{PROJECTED_START_DATE}|"
            "{PROPOSED_USER_PERSON_TYPE}|{PROPOSED_WORKER_TYPE}|{REASON_CODE}|"
            "{RETIREMENT_AGE}|{RETIREMENT_DATE}|{SPECIAL_CEILING_STEP}|{TAX_ADDRESS_ID}|"
            "{END_TIME}|{START_TIME}|{WORK_AT_HOME_FLAG}|"
            "{FREEZE_START_DATE}|{FREEZE_UNTIL_DATE}|{GUID}|{PEOPLE_GROUP}|"
            "{GSP_ELIGIBILITY_FLAG}|{DEFAULT_EXPENSE_ACCOUNT}|{UNION_ID}|{UNION_NAME}|"
            "{OVERTIME_PERIOD_NAME}|{SOURCE_ASSIGNMENT_NUMBER}|{TAX_REPORTING_UNIT}|"
            "{CONTRACT_NUMBER}|{TERMINATION_DATE}|{NOTIFICATION_DATE}|{LAST_WORKING_DATE}|"
            "{REHIRE_AUTHORIZER_PERSON_NUMBER}|{TERMINATE_ASSIGNMENT_FLAG}|"
            "{CORRECT_ASSIGNMENT_TERMINATION_FLAG}|{REVERSE_ASSIGNMENT_TERMINATION_FLAG}|"
            "{REQUISITION_NUMBER}|{CANDIDATE_NUMBER}|{ADJUSTED_FTE}|"
            "{ANNUAL_WORKING_DURATION}|{ANNUAL_WORKING_DURATION_UNITS}|{ANNUAL_WORKING_RATIO}|"
            "{STANDARD_HOURS}|{STD_ANNUAL_WORKING_DURATION}|{NOTES}"
        ),
        description="Assignment object migration file for Oracle Fusion HCM Workforce Structures.",
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