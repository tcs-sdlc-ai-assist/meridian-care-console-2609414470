"""Define member list contracts."""
from pydantic import BaseModel
class MemberRow(BaseModel): member_id: str; name: str; dob: str; plan: str; pcp: str; risk_level: str; open_gaps: int; coordinator_id: str
class MemberList(BaseModel): items: list[MemberRow]; total: int
