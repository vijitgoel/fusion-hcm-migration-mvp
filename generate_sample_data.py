import pandas as pd
from datetime import datetime, timedelta

# Function to generate sample data for Location
location_metadata = "METADATA|Location|SetCode|ActiveStatus|EffectiveStartDate|EffectiveEndDate|ShipToSiteFlag|BillToSiteFlag|OfficeSiteFlag|ReceivingSiteFlag|ShipToLocationCode|ShipToLocationSetCode|InventoryOrganizationName|LocationCode|LocationName|AddressLine1|AddressLine2|AddressLine3|Country|PostalCode|TownOrCity|MainphoneSubscriberNumber|OtherphoneSubscriberNumber|Description|Region1|Region2|Region3|SourceSystemOwner|SourceSystemId"
location_columns = location_metadata.split('|')[2:]  # Skip METADATA|Location

# Sample data for Location (8 rows)
location_data = [
    ["COMMON", "A", "1901/01/01", "4712/12/31", "Y", "Y", "Y", "Y", "", "", "", "00002", "New Delhi", "", "Janakpuri", "New Delhi India", "IN", "234432", "Delhi", "", "", "Delhi", "", "", "", "EBS", "HCM_LOCATION_00002_XXTEST"],
    ["COMMON", "A", "1901/01/01", "4712/12/31", "Y", "N", "N", "Y", "", "", "", "00003", "Mumbai", "", "Bandra", "Mumbai India", "IN", "400050", "Mumbai", "", "", "Maharashtra", "", "", "", "EBS", "HCM_LOCATION_00003_XXTEST"],
    ["COMMON", "A", "1901/01/01", "4712/12/31", "N", "Y", "Y", "N", "", "", "", "00004", "Bangalore", "", "Koramangala", "Bangalore India", "IN", "560034", "Bangalore", "", "", "Karnataka", "", "", "", "EBS", "HCM_LOCATION_00004_XXTEST"],
    ["COMMON", "A", "1901/01/01", "4712/12/31", "Y", "Y", "N", "Y", "", "", "", "00005", "Chennai", "", "T Nagar", "Chennai India", "IN", "600017", "Chennai", "", "", "Tamil Nadu", "", "", "", "EBS", "HCM_LOCATION_00005_XXTEST"],
    ["COMMON", "A", "1901/01/01", "4712/12/31", "N", "N", "Y", "Y", "", "", "", "00006", "Hyderabad", "", "Hitech City", "Hyderabad India", "IN", "500081", "Hyderabad", "", "", "Telangana", "", "", "", "EBS", "HCM_LOCATION_00006_XXTEST"],
    ["COMMON", "A", "1901/01/01", "4712/12/31", "Y", "Y", "Y", "N", "", "", "", "00007", "Pune", "", "Hinjewadi", "Pune India", "IN", "411057", "Pune", "", "", "Maharashtra", "", "", "", "EBS", "HCM_LOCATION_00007_XXTEST"],
    ["COMMON", "A", "1901/01/01", "4712/12/31", "N", "Y", "N", "Y", "", "", "", "00008", "Kolkata", "", "Salt Lake", "Kolkata India", "IN", "700091", "Kolkata", "", "", "West Bengal", "", "", "", "EBS", "HCM_LOCATION_00008_XXTEST"],
    ["COMMON", "A", "1901/01/01", "4712/12/31", "Y", "N", "Y", "Y", "", "", "", "00009", "Ahmedabad", "", "Navrangpura", "Ahmedabad India", "IN", "380009", "Ahmedabad", "", "", "Gujarat", "", "", "", "EBS", "HCM_LOCATION_00009_XXTEST"]
]

df_location = pd.DataFrame(location_data, columns=location_columns)

# Department - Multiple sheets: Organization, OrgInformation, OrgUnitClassification
# Organization
org_metadata = "METADATA|Organization|SourceSystemOwner|SourceSystemId|EffectiveStartDate|EffectiveEndDate|Name|ClassificationCode"
org_columns = org_metadata.split('|')[2:]

org_data = [
    ["SOURCE_SYSTEM_OWNER", "PU1", "01/01/0001", "", "My Project Unit Name", "PRJ_PROJECT_UNIT"],
    ["SOURCE_SYSTEM_OWNER", "PU2", "01/01/0001", "", "Finance Department", "FIN_DEPT"],
    ["SOURCE_SYSTEM_OWNER", "PU3", "01/01/0001", "", "HR Department", "HR_DEPT"],
    ["SOURCE_SYSTEM_OWNER", "PU4", "01/01/0001", "", "IT Department", "IT_DEPT"],
    ["SOURCE_SYSTEM_OWNER", "PU5", "01/01/0001", "", "Sales Department", "SALES_DEPT"],
    ["SOURCE_SYSTEM_OWNER", "PU6", "01/01/0001", "", "Marketing Department", "MKTG_DEPT"],
    ["SOURCE_SYSTEM_OWNER", "PU7", "01/01/0001", "", "Operations Department", "OPS_DEPT"],
    ["SOURCE_SYSTEM_OWNER", "PU8", "01/01/0001", "", "Legal Department", "LEGAL_DEPT"]
]

df_org = pd.DataFrame(org_data, columns=org_columns)

# OrgInformation
orginfo_metadata = "METADATA|OrgInformation|SourceSystemOwner|SourceSystemId|EffectiveStartDate|EffectiveEndDate|OrganizationId(SourceSystemId)|FLEX:PER_ORGANIZATION_INFORMATION_EFF|EFF_CATEGORY_CODE|OrgInformationContext|projectUnitCode(PER_ORGANIZATION_INFORMATION_EFF=PRJ_PU_ATTRIBUTES)"
orginfo_columns = orginfo_metadata.split('|')[2:]

orginfo_data = [
    ["SOURCE_SYSTEM_OWNER", "PU1_INFO", "01/01/0001", "", "PU1", "PRJ_PU_ATTRIBUTES", "PRJ_PU_ATTRIBUTES", "PRJ_PROJECT_UNIT", "PU1_CODE"],
    ["SOURCE_SYSTEM_OWNER", "PU2_INFO", "01/01/0001", "", "PU2", "FIN_INFO", "FIN_INFO", "FIN_DEPT", "PU2_CODE"],
    ["SOURCE_SYSTEM_OWNER", "PU3_INFO", "01/01/0001", "", "PU3", "HR_INFO", "HR_INFO", "HR_DEPT", "PU3_CODE"],
    ["SOURCE_SYSTEM_OWNER", "PU4_INFO", "01/01/0001", "", "PU4", "IT_INFO", "IT_INFO", "IT_DEPT", "PU4_CODE"],
    ["SOURCE_SYSTEM_OWNER", "PU5_INFO", "01/01/0001", "", "PU5", "SALES_INFO", "SALES_INFO", "SALES_DEPT", "PU5_CODE"],
    ["SOURCE_SYSTEM_OWNER", "PU6_INFO", "01/01/0001", "", "PU6", "MKTG_INFO", "MKTG_INFO", "MKTG_DEPT", "PU6_CODE"],
    ["SOURCE_SYSTEM_OWNER", "PU7_INFO", "01/01/0001", "", "PU7", "OPS_INFO", "OPS_INFO", "OPS_DEPT", "PU7_CODE"],
    ["SOURCE_SYSTEM_OWNER", "PU8_INFO", "01/01/0001", "", "PU8", "LEGAL_INFO", "LEGAL_INFO", "LEGAL_DEPT", "PU8_CODE"]
]

df_orginfo = pd.DataFrame(orginfo_data, columns=orginfo_columns)

# OrgUnitClassification
orgunit_metadata = "METADATA|OrgUnitClassification|SourceSystemOwner|SourceSystemId|EffectiveStartDate|EffectiveEndDate|OrganizationId(SourceSystemId)|ClassificationCode|SetCode|Status"
orgunit_columns = orgunit_metadata.split('|')[2:]

orgunit_data = [
    ["SOURCE_SYSTEM_OWNER", "PU1_CLASS", "01/01/0001", "", "PU1", "PRJ_PROJECT_UNIT", "COMMON", "A"],
    ["SOURCE_SYSTEM_OWNER", "PU2_CLASS", "01/01/0001", "", "PU2", "FIN_DEPT", "COMMON", "A"],
    ["SOURCE_SYSTEM_OWNER", "PU3_CLASS", "01/01/0001", "", "PU3", "HR_DEPT", "COMMON", "A"],
    ["SOURCE_SYSTEM_OWNER", "PU4_CLASS", "01/01/0001", "", "PU4", "IT_DEPT", "COMMON", "A"],
    ["SOURCE_SYSTEM_OWNER", "PU5_CLASS", "01/01/0001", "", "PU5", "SALES_DEPT", "COMMON", "A"],
    ["SOURCE_SYSTEM_OWNER", "PU6_CLASS", "01/01/0001", "", "PU6", "MKTG_DEPT", "COMMON", "A"],
    ["SOURCE_SYSTEM_OWNER", "PU7_CLASS", "01/01/0001", "", "PU7", "OPS_DEPT", "COMMON", "A"],
    ["SOURCE_SYSTEM_OWNER", "PU8_CLASS", "01/01/0001", "", "PU8", "LEGAL_DEPT", "COMMON", "A"]
]

df_orgunit = pd.DataFrame(orgunit_data, columns=orgunit_columns)

# Employee - Inferred basic structure (8 rows)
employee_columns = ["EmployeeNumber", "FirstName", "LastName", "Email", "DepartmentCode", "HireDate", "SourceSystemOwner", "SourceSystemId"]

employee_data = [
    ["EMP001", "John", "Doe", "john.doe@company.com", "PU1", "2023-01-15", "EBS", "HCM_EMP_001"],
    ["EMP002", "Jane", "Smith", "jane.smith@company.com", "PU2", "2023-02-20", "EBS", "HCM_EMP_002"],
    ["EMP003", "Mike", "Johnson", "mike.johnson@company.com", "PU3", "2023-03-10", "EBS", "HCM_EMP_003"],
    ["EMP004", "Sarah", "Wilson", "sarah.wilson@company.com", "PU4", "2023-04-05", "EBS", "HCM_EMP_004"],
    ["EMP005", "David", "Brown", "david.brown@company.com", "PU5", "2023-05-12", "EBS", "HCM_EMP_005"],
    ["EMP006", "Emily", "Davis", "emily.davis@company.com", "PU6", "2023-06-18", "EBS", "HCM_EMP_006"],
    ["EMP007", "Robert", "Taylor", "robert.taylor@company.com", "PU7", "2023-07-22", "EBS", "HCM_EMP_007"],
    ["EMP008", "Lisa", "Anderson", "lisa.anderson@company.com", "PU8", "2023-08-30", "EBS", "HCM_EMP_008"]
]

df_employee = pd.DataFrame(employee_data, columns=employee_columns)

# Write to Excel files
# Location.xlsx
with pd.ExcelWriter('InputData/Location/Location.xlsx', engine='openpyxl') as writer:
    df_location.to_excel(writer, sheet_name='Location', index=False)

# Department.xlsx with multiple sheets
with pd.ExcelWriter('InputData/Department/Department.xlsx', engine='openpyxl') as writer:
    df_org.to_excel(writer, sheet_name='Organization', index=False)
    df_orginfo.to_excel(writer, sheet_name='OrgInformation', index=False)
    df_orgunit.to_excel(writer, sheet_name='OrgUnitClassification', index=False)

# Employee.xlsx
with pd.ExcelWriter('InputData/Employee/Employee.xlsx', engine='openpyxl') as writer:
    df_employee.to_excel(writer, sheet_name='Employee', index=False)

print("Sample Excel files generated successfully.")