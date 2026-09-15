"""Define relational entities for Meridian's synthetic care-management data."""

from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Coordinator(Base):
    """Represent an authenticated staff member and their role."""

    __tablename__ = "coordinators"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    coordinator_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    members: Mapped[list["Member"]] = relationship(back_populates="coordinator", lazy="selectin")


class Member(Base):
    """Represent a synthetic plan member assigned to a coordinator."""

    __tablename__ = "members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    dob: Mapped[date] = mapped_column(Date)
    sex: Mapped[str] = mapped_column(String(20))
    phone: Mapped[str] = mapped_column(String(30))
    address: Mapped[str] = mapped_column(String(255))
    ssn: Mapped[str] = mapped_column(String(16))
    mbi: Mapped[str] = mapped_column(String(20))
    plan: Mapped[str] = mapped_column(String(100))
    pcp_name: Mapped[str] = mapped_column(String(120))
    risk_level: Mapped[str] = mapped_column(String(20))
    coordinator_id: Mapped[str] = mapped_column(ForeignKey("coordinators.coordinator_id"), index=True)
    coordinator: Mapped[Coordinator] = relationship(back_populates="members", lazy="selectin")
    care_gaps: Mapped[list["CareGap"]] = relationship(back_populates="member", lazy="selectin")


class CareGap(Base):
    """Represent an actionable screening or visit gap."""

    __tablename__ = "care_gaps"
    __table_args__ = (Index("ix_care_gaps_member_id", "member_id"), Index("ix_care_gaps_status", "status"))
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gap_id: Mapped[str] = mapped_column(String(32), unique=True)
    member_id: Mapped[str] = mapped_column(ForeignKey("members.member_id"))
    type: Mapped[str] = mapped_column(String(120))
    due_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="open")
    closed_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    closed_by: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    member: Mapped[Member] = relationship(back_populates="care_gaps", lazy="selectin")


class Outreach(Base):
    """Represent a documented member contact attempt."""

    __tablename__ = "outreach"
    __table_args__ = (Index("ix_outreach_member_id", "member_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    outreach_id: Mapped[str] = mapped_column(String(32), unique=True)
    member_id: Mapped[str] = mapped_column(ForeignKey("members.member_id"))
    coordinator_id: Mapped[str] = mapped_column(ForeignKey("coordinators.coordinator_id"))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    channel: Mapped[str] = mapped_column(String(20))
    outcome: Mapped[str] = mapped_column(String(30))
    notes: Mapped[str] = mapped_column(Text)


class CarePlanGoal(Base):
    """Represent a care-plan goal or intervention row."""

    __tablename__ = "care_plan_goals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[str] = mapped_column(ForeignKey("members.member_id"))
    text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="not-started")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AuditLog(Base):
    """Represent a non-sensitive member-record access audit event."""

    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(32))
    member_id: Mapped[str] = mapped_column(String(32))
    action: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
