"""Define member-detail workflow contracts."""
from pydantic import BaseModel, Field
class GapCloseRequest(BaseModel): reason: str = Field(min_length=2,max_length=500)
class OutreachRequest(BaseModel): channel: str; outcome: str; notes: str = Field(min_length=1,max_length=1000)
class GoalUpdateRequest(BaseModel): status: str
class MemberDetail(BaseModel): member_id: str; name: str; dob: str; sex: str; phone: str; address: str; plan: str; pcp: str; risk_level: str; ssn: str; mbi: str; gaps: list[dict[str,str]]
