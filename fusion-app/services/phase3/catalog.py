from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .utils import canonical_column_name


@dataclass(frozen=True)
class ObjectDefinition:
    name: str
    aliases: List[str]
    required_columns: List[str]
    optional_columns: List[str] = field(default_factory=list)
    unique_columns: List[str] = field(default_factory=list)
    date_columns: List[str] = field(default_factory=list)
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
        required_columns=["EmployeeNumber", "FirstName", "LastName", "HireDate"],
        optional_columns=["Email", "BusinessUnit", "Department", "Location", "Nationality"],
        unique_columns=["EmployeeNumber"],
        date_columns=["HireDate"],
        output_header="METADATA|Worker|PersonNumber|FirstName|LastName|StartDate|Email|BusinessUnit|Department|Location|Nationality",
        output_template=(
            "MERGE|Worker|{EmployeeNumber}|{FirstName}|{LastName}|{HireDate}|"
            "{Email}|{BusinessUnit}|{Department}|{Location}|{Nationality}"
        ),
        description="Worker object migration file.",
    ),
    "Location": ObjectDefinition(
        name="Location",
        aliases=["location", "locations", "site", "office"],
        required_columns=["LocationCode", "LocationName", "EffectiveStartDate"],
        optional_columns=["Country", "City", "State", "Status"],
        unique_columns=["LocationCode"],
        date_columns=["EffectiveStartDate"],
        output_header="METADATA|Location|LocationCode|LocationName|EffectiveStartDate|Country|City|State|Status",
        output_template=(
            "MERGE|Location|{LocationCode}|{LocationName}|{EffectiveStartDate}|"
            "{Country}|{City}|{State}|{Status}"
        ),
        description="Location object migration file.",
    ),
    "Department": ObjectDefinition(
        name="Department",
        aliases=["department", "dept", "departments"],
        required_columns=["DepartmentCode", "DepartmentName", "EffectiveStartDate"],
        optional_columns=["Manager", "BusinessUnit", "Status"],
        unique_columns=["DepartmentCode"],
        date_columns=["EffectiveStartDate"],
        output_header="METADATA|Department|DepartmentCode|DepartmentName|EffectiveStartDate|Manager|BusinessUnit|Status",
        output_template=(
            "MERGE|Department|{DepartmentCode}|{DepartmentName}|{EffectiveStartDate}|"
            "{Manager}|{BusinessUnit}|{Status}"
        ),
        description="Department object migration file.",
    ),
}


def get_object_catalog() -> Dict[str, ObjectDefinition]:
    return OBJECT_CATALOG
