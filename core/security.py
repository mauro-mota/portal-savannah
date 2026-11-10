from ipaddress import ip_address
from django.conf import settings

def client_ip(request):
    # Em produção, somente Caddy expõe uma porta pública e substitui X-Forwarded-For.
    raw = request.META.get('REMOTE_ADDR', '127.0.0.1')
    if settings.PRODUCTION:
        raw = request.META.get('HTTP_X_FORWARDED_FOR', raw).split(',')[-1].strip()
    try:
        return str(ip_address(raw))
    except ValueError:
        return None
