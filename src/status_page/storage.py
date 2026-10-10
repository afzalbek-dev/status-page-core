import sqlite3
import time
from typing import Optional, List, Dict, Any
from .models import Service, Incident, ServiceStatus


class StatusStorage:
    """Xizmatlar, insidentlar va monitoring natijalarini SQLite bazasida saqlash."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS services (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    status TEXT NOT NULL,
                    latency_ms REAL DEFAULT 0,
                    last_checked REAL DEFAULT 0
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS probe_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY(service_id) REFERENCES services(id)
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    resolved_at REAL
                )
                """
            )

    def add_service(self, service_id: str, name: str, url: str):
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO services (id, name, url, status, latency_ms, last_checked)
                VALUES (?, ?, ?, ?, 0, ?)
                """,
                (service_id, name, url, ServiceStatus.OPERATIONAL, time.time()),
            )

    def record_probe(self, service_id: str, status: str, latency_ms: float):
        now = time.time()
        with self._conn:
            self._conn.execute(
                "UPDATE services SET status = ?, latency_ms = ?, last_checked = ? WHERE id = ?",
                (status, latency_ms, now, service_id),
            )
            self._conn.execute(
                "INSERT INTO probe_logs (service_id, status, latency_ms, timestamp) VALUES (?, ?, ?, ?)",
                (service_id, status, latency_ms, now),
            )

    def get_services(self) -> List[Service]:
        cur = self._conn.cursor()
        cur.execute("SELECT id, name, url, status, latency_ms, last_checked FROM services")
        return [Service(*r) for r in cur.fetchall()]

    def calculate_uptime_percentage(self, service_id: str) -> float:
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM probe_logs WHERE service_id = ?", (service_id,))
        total = cur.fetchone()[0]
        if total == 0:
            return 100.0

        cur.execute("SELECT COUNT(*) FROM probe_logs WHERE service_id = ? AND status = ?", (service_id, ServiceStatus.OPERATIONAL))
        up = cur.fetchone()[0]
        return round((up / total) * 100, 2)

    def create_incident(self, title: str, severity: str, description: str) -> int:
        with self._conn:
            cur = self._conn.execute(
                """
                INSERT INTO incidents (title, severity, status, description, created_at, resolved_at)
                VALUES (?, ?, 'investigating', ?, ?, NULL)
                """,
                (title, severity, description, time.time()),
            )
            return cur.lastrowid

    def resolve_incident(self, incident_id: int) -> bool:
        with self._conn:
            cur = self._conn.execute(
                "UPDATE incidents SET status = 'resolved', resolved_at = ? WHERE id = ?",
                (time.time(), incident_id),
            )
            return cur.rowcount > 0

    def list_incidents(self, active_only: bool = False) -> List[Incident]:
        cur = self._conn.cursor()
        if active_only:
            cur.execute("SELECT id, title, severity, status, description, created_at, resolved_at FROM incidents WHERE status != 'resolved' ORDER BY id DESC")
        else:
            cur.execute("SELECT id, title, severity, status, description, created_at, resolved_at FROM incidents ORDER BY id DESC")
        return [Incident(*r) for r in cur.fetchall()]

    def close(self):
        self._conn.close()
