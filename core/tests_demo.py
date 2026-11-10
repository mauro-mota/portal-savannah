"""Regressions for the isolated public demonstration."""
from io import StringIO
from unittest import skipUnless
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase, override_settings
from core.models import User, Task, Event, Goal, Notice

TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@skipUnless(getattr(settings, "DEMO_MODE", False), "Requires config.demo_settings")
@override_settings(STORAGES=TEST_STORAGES)
class DemoTests(TestCase):
    def setUp(self):
        call_command("seed_demo", stdout=StringIO())
        self.visitor = User.objects.get(username=settings.DEMO_USERNAME)

    def enter(self):
        return self.client.post("/demo/entrar/")

    def test_seed_is_idempotent_and_accounts_have_no_privileges_or_passwords(self):
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual([m.objects.count() for m in (User, Task, Event, Goal, Notice)], [3, 5, 2, 1, 2])
        for user in User.objects.all():
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)
            self.assertFalse(user.has_usable_password())
            self.assertEqual(user.email, "")

    @override_settings(DEMO_MODE=False)
    def test_seed_refuses_non_demo_configuration(self):
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())

    def test_seed_refuses_unknown_users_without_changing_records(self):
        User.objects.create_user("someone-real")
        before = list(Task.objects.values())
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.assertEqual(before, list(Task.objects.values()))

    def test_seed_refuses_unrecognized_records_without_changing_accounts(self):
        Task.objects.filter(pk=Task.objects.first().pk).update(title="Unrecognized record")
        old_password = self.visitor.password
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.visitor.refresh_from_db()
        self.assertEqual(old_password, self.visitor.password)

    def test_password_free_entry_has_fixed_local_destination(self):
        response = self.client.post("/demo/entrar/?next=https://example.com/")
        self.assertRedirects(response, "/")
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.visitor.pk)

    def test_entry_is_post_only_and_csrf_protected(self):
        self.assertEqual(self.client.get("/demo/entrar/").status_code, 405)
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post("/demo/entrar/").status_code, 403)
        client.get("/entrar/")
        token = client.cookies[settings.CSRF_COOKIE_NAME].value
        self.assertEqual(client.post("/demo/entrar/", {"csrfmiddlewaretoken": token}).status_code, 302)

    def test_entry_refuses_privileged_or_password_enabled_account(self):
        for field in ("is_staff", "is_superuser"):
            User.objects.filter(pk=self.visitor.pk).update(**{field: True})
            self.assertEqual(self.enter().status_code, 403)
            User.objects.filter(pk=self.visitor.pk).update(**{field: False})
        self.visitor.set_password("OnlyForThisDisposableTest123!")
        self.visitor.save()
        self.assertEqual(self.enter().status_code, 403)

    def test_all_readonly_pages_render_and_have_demo_banner(self):
        self.enter()
        for path in ("/", "/tarefas/", "/compromissos/", "/calendario/", "/metas/", "/comunicados/"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertContains(response, "Dados fictícios")
            self.assertContains(response, "somente leitura")
            self.assertNotContains(response, 'href="/senha/"')
            self.assertNotContains(response, "/editar/")
            self.assertNotContains(response, "/novo/")
            self.assertNotContains(response, "/excluir/")

    def test_mutations_and_account_changes_are_blocked_with_unchanged_data(self):
        self.enter()
        before = {m.__name__: list(m.objects.order_by("pk").values()) for m in (User, Task, Event, Goal, Notice)}
        for kind, model in (("tarefas", Task), ("compromissos", Event), ("metas", Goal), ("comunicados", Notice)):
            obj = model.objects.first()
            for path in (f"/{kind}/novo/", f"/{kind}/{obj.pk}/editar/", f"/{kind}/{obj.pk}/excluir/"):
                for method in (self.client.get, self.client.post):
                    self.assertEqual(method(path).status_code, 403, path)
        for path in ("/senha/", "/senha/ok/", "/admin/", "/entrar/"):
            self.assertEqual(self.client.post(path, {"new_password1": "ChangedPassword123!"}).status_code, 403)
        after = {m.__name__: list(m.objects.order_by("pk").values()) for m in (User, Task, Event, Goal, Notice)}
        self.assertEqual(before, after)

    def test_other_unsafe_methods_are_blocked(self):
        self.enter()
        for method in ("PUT", "PATCH", "DELETE", "TRACE"):
            self.assertEqual(self.client.generic(method, "/tarefas/").status_code, 403)
            self.assertEqual(self.client.generic(method, "/demo/entrar/").status_code, 403)

    def test_logout_clears_visitor_session(self):
        self.enter()
        self.assertEqual(self.client.get("/sair/").status_code, 405)
        self.assertEqual(self.client.post("/sair/").status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_has_no_shared_password_form(self):
        response = self.client.get("/entrar/")
        self.assertContains(response, "Explorar demonstração")
        self.assertNotContains(response, 'name="password"')
        self.assertNotContains(response, 'name="username"')

    def test_robots_discourages_indexing(self):
        self.assertContains(self.client.get("/robots.txt"), "Disallow: /")
