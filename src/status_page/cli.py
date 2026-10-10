import argparse
import sys
import json
from .storage import StatusStorage
from .prober import ServiceProber


def main():
    parser = argparse.ArgumentParser(description="Status Page Core - Xizmatlar monitoringi va insidentlar CLI")
    parser.add_argument("--db", default="/tmp/status_page.db", help="SQLite ma'lumotlar bazasi fayli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_p = subparsers.add_parser("add", help="Yangi servis qo'shish")
    add_p.add_argument("--id", required=True)
    add_p.add_argument("--name", required=True)
    add_p.add_argument("--url", required=True)

    probe_p = subparsers.add_parser("probe", help="Barcha servislarni tekshirish")

    incident_p = subparsers.add_parser("incident", help="Yangi insident ochish")
    incident_p.add_argument("--title", required=True)
    incident_p.add_argument("--severity", choices=["minor", "major", "critical"], default="minor")
    incident_p.add_argument("--desc", required=True)

    resolve_p = subparsers.add_parser("resolve", help="Insidentni hal qilish")
    resolve_p.add_argument("id", type=int)

    summary_p = subparsers.add_parser("summary", help="Umumiy holat hisoboti")

    args = parser.parse_args()
    storage = StatusStorage(args.db)
    prober = ServiceProber(storage)

    if args.command == "add":
        storage.add_service(args.id, args.name, args.url)
        print(f"✅ Servis qo'shildi: {args.name} -> {args.url}")
    elif args.command == "probe":
        results = prober.run_check_all()
        print(json.dumps(results, indent=2))
    elif args.command == "incident":
        iid = storage.create_incident(args.title, args.severity, args.desc)
        print(f"🚨 Insident ochildi! ID: #{iid}")
    elif args.command == "resolve":
        ok = storage.resolve_incident(args.id)
        if ok:
            print(f"✅ Insident #{args.id} hal qilindi.")
        else:
            print(f"Topilmadi: #{args.id}", file=sys.stderr)
    elif args.command == "summary":
        services = storage.get_services()
        incidents = storage.list_incidents(active_only=True)
        print("=== STATUS PAGE SUMMARY ===")
        print(f"Faol insidentlar: {len(incidents)} ta")
        for inc in incidents:
            print(f"  🚨 [#{inc.id}] [{inc.severity.upper()}] {inc.title}")
        print("\nXizmatlar holati:")
        for s in services:
            uptime = storage.calculate_uptime_percentage(s.id)
            print(f"  • {s.name}: {s.status.upper()} | Latency: {s.latency_ms:.1f}ms | Uptime: {uptime}%")


if __name__ == "__main__":
    main()
