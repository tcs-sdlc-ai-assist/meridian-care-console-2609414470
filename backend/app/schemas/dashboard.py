"""Define dashboard response contracts."""
from pydantic import BaseModel
class Metric(BaseModel): label: str; value: int | float
class DashboardResponse(BaseModel): metrics: list[Metric]; attention: list[str]; activity: list[str]; chart: list[int]
