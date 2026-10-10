from dataclasses import dataclass
from typing import Optional, List


class ServiceStatus:
    OPERATIONAL = "operational"      # 🟢 Ishlamoqda
    DEGRADED = "degraded"            # 🟡 Sekinlashgan
    MAJOR_OUTAGE = "major_outage"    # 🔴 To'xtagan


class IncidentSeverity:
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


@dataclass
class Service:
    id: str
    name: str
    url: str
    status: str
    latency_ms: float
    last_checked: float


@dataclass
class Incident:
    id: int
    title: str
    severity: str
    status: str  # 'investigating', 'identified', 'monitoring', 'resolved'
    description: str
    created_at: float
    resolved_at: Optional[float]
