from django.conf import settings


def portfolio(request):
    return {"demo_mode": getattr(settings, "DEMO_MODE", False)}
