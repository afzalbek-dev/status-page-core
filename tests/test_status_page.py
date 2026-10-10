import pytest
from status_page.models import ServiceStatus, IncidentSeverity
from status_page.storage import StatusStorage
from status_page.prober import ServiceProber


def test_service_storage_and_uptime(tmp_path):
    db_file = str(tmp_path / "status_test.db")
    storage = StatusStorage(db_file)

    storage.add_service("api", "Core API", "https://api.example.com")
    services = storage.get_services()
    assert len(services) == 1
    assert services[0].id == "api"

    # 3 ta probe yozish (2 ta up, 1 ta down)
    storage.record_probe("api", ServiceStatus.OPERATIONAL, 45.0)
    storage.record_probe("api", ServiceStatus.OPERATIONAL, 50.0)
    storage.record_probe("api", ServiceStatus.MAJOR_OUTAGE, 3000.0)

    uptime = storage.calculate_uptime_percentage("api")
    # 2/3 = 66.67%
    assert uptime == 66.67

    # Insident ochish va yopish
    inc_id = storage.create_incident("API DB Bog'lanish Uzilishi", IncidentSeverity.CRITICAL, "Postgres server javob bermayapti")
    assert inc_id == 1

    active = storage.list_incidents(active_only=True)
    assert len(active) == 1
    assert active[0].status == "investigating"

    assert storage.resolve_incident(inc_id) is True
    assert len(storage.list_incidents(active_only=True)) == 0
    storage.close()


def test_prober_mock_url():
    storage = StatusStorage(":memory:")
    prober = ServiceProber(storage)

    # Noto'g'ri / mavjud bo'lmagan manzil tekshiruvi (Outage qaytarishi shart)
    status, latency = prober.probe_url("http://127.0.0.1:54321/non-existent-probe-test")
    assert status == ServiceStatus.MAJOR_OUTAGE
    assert latency >= 0.0
