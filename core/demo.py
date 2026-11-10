"""A password-free visitor session for a completely separate demo database."""
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


class ReadOnlyDemoMiddleware:
    """Fail closed for every unsafe request except visitor entry and logout."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, "DEMO_MODE", False):
            blocked_page = (
                request.path.startswith(("/admin/", "/senha/"))
                or request.path.rstrip("/").endswith(("/novo", "/editar", "/excluir"))
            )
            unsafe = request.method not in ("GET", "HEAD", "OPTIONS")
            allowed_post = request.method == "POST" and request.path in (
                "/demo/entrar/", "/sair/"
            )
            if blocked_page or (unsafe and not allowed_post):
                return render(request, "demo/readonly.html", status=403)
        return self.get_response(request)


@require_POST
def enter_demo(request):
    if not getattr(settings, "DEMO_MODE", False):
        raise Http404
    visitor = get_user_model().objects.filter(
        username=settings.DEMO_USERNAME,
        is_active=True,
        is_staff=False,
        is_superuser=False,
    ).first()
    if visitor is None or visitor.has_usable_password():
        raise PermissionDenied("A demonstração ainda não está preparada.")
    login(request, visitor, backend="django.contrib.auth.backends.ModelBackend")
    # Ignore next: the visitor always lands inside this demo.
    return redirect("dashboard")


def robots(request):
    return HttpResponse("User-agent: *\nDisallow: /\n", content_type="text/plain")
