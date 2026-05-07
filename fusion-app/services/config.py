# services/config.py
# Configurable rules for validation

REQUIRED_COLUMNS = ['EmployeeNumber', 'FirstName', 'LastName', 'HireDate']

VALIDATION_RULES = {
    "EmployeeNumber": {"required": True, "unique": True},
    "FirstName": {"required": True},
    "LastName": {"required": True},
    "HireDate": {"required": True, "type": "date"}
}