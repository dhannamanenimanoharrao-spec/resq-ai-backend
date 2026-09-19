from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


AmbulanceStatus = Literal[
    "available",
    "dispatched",
    "busy",
    "offline",
]

EmergencyStatus = Literal[
    "pending",
    "assigned",
    "in_transit",
    "at_hospital",
    "completed",
    "cancelled",
]

SeverityLevel = Literal[
    "low",
    "medium",
    "high",
    "critical",
]


class Ambulance(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    status: AmbulanceStatus = "available"
    ambulance_type: str = "basic"
    current_emergency_id: Optional[str] = None


class Hospital(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    available_beds: int = Field(default=0, ge=0)
    emergency_capable: bool = True


class Emergency(BaseModel):
    id: str
    latitude: float
    longitude: float
    emergency_type: str
    severity: SeverityLevel
    status: EmergencyStatus = "pending"
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_ambulance_id: Optional[str] = None