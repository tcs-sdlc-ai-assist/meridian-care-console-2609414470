"""Define typed contracts for protected member-care workflows."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


OutreachChannel = Literal["phone", "SMS", "mail", "member portal"]
OutreachOutcome = Literal["reached", "left message", "no answer", "wrong number"]
GoalStatus = Literal["not-started", "in-progress", "met"]


class GapCloseRequest(BaseModel):
    """Capture the required attribution for a gap closure."""

    reason: str = Field(min_length=2, max_length=500)


class OutreachRequest(BaseModel):
    """Capture a constrained outreach event."""

    channel: OutreachChannel
    outcome: OutreachOutcome
    notes: str = Field(min_length=1, max_length=1000)


class GoalUpdateRequest(BaseModel):
    """Allow an authorized staff member to change a goal's workflow status."""

    status: GoalStatus


class AssignmentRequest(BaseModel):
    """Identify the coordinator to whom a supervisor assigns a member."""

    coordinator_id: str = Field(min_length=1, max_length=32)


class CareGapDetail(BaseModel):
    gap_id: str
    type: str
    status: str
    closed_reason: str | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None


class OutreachDetail(BaseModel):
    outreach_id: str
    coordinator_id: str
    date: datetime
    channel: OutreachChannel
    outcome: OutreachOutcome
    notes: str


class CarePlanGoalDetail(BaseModel):
    goal_id: int
    text: str
    status: GoalStatus
    updated_at: datetime


class MemberDetail(BaseModel):
    member_id: str
    name: str
    dob: str
    sex: str
    phone: str
    address: str
    plan: str
    pcp: str
    risk_level: str
    coordinator_id: str
    ssn: str
    mbi: str
    gaps: list[CareGapDetail]
    care_plan: list[CarePlanGoalDetail]
    outreach: list[OutreachDetail]
