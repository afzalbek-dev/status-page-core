# Status Page Core

Xizmatlar salomatligi (uptime monitoring), kechikish (latency ms), davriy SLA foizi hisoboti va insidentlar (incident response) boshqaruvini ta'minlovchi modulli backend tizim.

## Xususiyatlari
- **Avtomatlashtirilgan Salomatlik Nazorati (Prober)**: HTTP va API endpointlarini davriy tekshirish va javob tezligini o'lchash.
- **SLA Uptime Foizi**: Tarixiy loglar asosida 24 soatlik va oylik ishonchlilik (masalan: 99.9%) ko'rsatkichini hisoblash.
- **Insidentlar Boshqaruvi**: Xatolik darajasi (Minor, Major, Critical) bo'yicha hodisalarni qayd etish, holatini yangilash va hal qilish.
- **SQLite Saqlash**: Barcha loglar va statistika yengil lokal ma'lumotlar bazasida saqlanadi.

## Foydalanish (Python)
```python
from status_page import StatusStorage, ServiceProber

storage = StatusStorage("status.db")
storage.add_service("backend", "Production API", "https://api.myproject.uz/health")

prober = ServiceProber(storage)
results = prober.run_check_all()
print(results)
```

## CLI
```bash
status-page add --id web --name "Frontend Web" --url "https://myproject.uz"
status-page probe
status-page incident --title "Kesh xizmati uzilishi" --severity minor --desc "Redis qayta yuklanmoqda"
status-page summary
```

## Testlar
```bash
pytest tests/ -v
```

## Litsenziya
MIT
