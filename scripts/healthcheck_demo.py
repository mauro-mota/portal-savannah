"""Loopback-only HTTP healthcheck, including production proxy settings."""
import os
import urllib.request

host = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")[0].strip()
headers = {"Host": host}
if os.environ.get("PRODUCTION") == "1":
    headers["X-Forwarded-Proto"] = "https"
request = urllib.request.Request("http://127.0.0.1:8000/entrar/", headers=headers)
with urllib.request.urlopen(request, timeout=5) as response:
    if response.status != 200:
        raise SystemExit(1)
