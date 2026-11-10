from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import path
from core import views
urlpatterns = [
    path("admin/", admin.site.urls),
    path("entrar/", auth.LoginView.as_view(template_name="login.html"), name="login"),
    path("sair/", auth.LogoutView.as_view(), name="logout"),
    path("senha/", auth.PasswordChangeView.as_view(template_name="form.html", success_url="/senha/ok/"), name="password_change"),
    path("senha/ok/", auth.PasswordChangeDoneView.as_view(template_name="password_done.html"), name="password_change_done"),
    path("", views.dashboard, name="dashboard"),
    path("calendario/", views.calendar_view, name="calendar"),
    path("<str:kind>/", views.list_view, name="list"),
    path("<str:kind>/novo/", views.edit_view, name="new"),
    path("<str:kind>/<int:pk>/editar/", views.edit_view, name="edit"),
    path("<str:kind>/<int:pk>/excluir/", views.delete_view, name="delete"),
]

if getattr(settings, "DEMO_MODE", False):
    from core import demo
    urlpatterns = [
        path("demo/entrar/", demo.enter_demo, name="demo_enter"),
        path("robots.txt", demo.robots),
    ] + urlpatterns
