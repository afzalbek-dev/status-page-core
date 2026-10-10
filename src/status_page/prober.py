import time
import urllib.request
from typing import Dict, Any, Tuple
from .models import ServiceStatus
from .storage import StatusStorage


class ServiceProber:
    """Xizmatlarning salomatligini HTTP orqali tekshiruvchi modul."""

    def __init__(self, storage: StatusStorage, timeout: float = 3.0):
        self.storage = storage
        self.timeout = timeout

    def probe_url(self, url: str) -> Tuple[str, float]:
        start = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "StatusPageProber/1.0"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                latency = round((time.time() - start) * 1000, 2)
                if 200 <= resp.status < 400:
                    status = ServiceStatus.OPERATIONAL if latency < 1500 else ServiceStatus.DEGRADED
                    return status, latency
                else:
                    return ServiceStatus.DEGRADED, latency
        except Exception:
            latency = round((time.time() - start) * 1000, 2)
            return ServiceStatus.MAJOR_OUTAGE, latency

    def run_check_all(self) -> Dict[str, Any]:
        services = self.storage.get_services()
        results = {}
        for s in services:
            status, latency = self.probe_url(s.url)
            self.storage.record_probe(s.id, status, latency)
            uptime = self.storage.calculate_uptime_percentage(s.id)
            results[s.id] = {
                "name": s.name,
                "status": status,
                "latency_ms": latency,
                "uptime_percent": uptime,
            }
        return results
