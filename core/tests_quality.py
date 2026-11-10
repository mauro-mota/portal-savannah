"""Focused regressions for the application independent of demonstration mode."""
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings, Client
from django.utils import timezone
from core.forms import EventForm, GoalForm
from core.models import User, Task, Event, Goal

TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(STORAGES=TEST_STORAGES)
class QualityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user("owner", password="LocalTestPassword123!")
        cls.other = User.objects.create_user("other", password="AnotherTestPassword123!")

    def setUp(self):
        self.client.force_login(self.owner)

    def test_empty_post_is_bound_and_displays_required_errors(self):
        response = self.client.post("/tarefas/novo/", {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].is_bound)
        self.assertIn("title", response.context["form"].errors)
        self.assertEqual(Task.objects.count(), 0)

    def test_calendar_includes_visible_adjacent_day(self):
        # November 2026 starts on a Sunday; Monday Oct 26 is displayed.
        start = timezone.make_aware(datetime(2026, 10, 26, 10))
        event = Event.objects.create(title="Adjacent day", created_by=self.owner, start=start, end=start + timedelta(hours=1))
        response = self.client.get("/calendario/?mes=2026-11-01")
        cell = next(c for week in response.context["weeks"] for c in week if c["date"].isoformat() == "2026-10-26")
        self.assertIn(event, cell["events"])

    def test_calendar_end_at_midnight_does_not_leak_to_next_day(self):
        start = timezone.make_aware(datetime(2026, 11, 4, 23))
        event = Event.objects.create(title="Ends at midnight", created_by=self.owner, start=start, end=start + timedelta(hours=1))
        response = self.client.get("/calendario/?mes=2026-11-01")
        cell = next(c for week in response.context["weeks"] for c in week if c["date"].isoformat() == "2026-11-05")
        self.assertNotIn(event, cell["events"])

    def test_event_list_prefetches_participants(self):
        now = timezone.now()
        for i in range(5):
            event = Event.objects.create(title=f"Meeting {i}", created_by=self.owner, start=now, end=now + timedelta(hours=1))
            event.participants.add(self.other)
        response = self.client.get("/compromissos/")
        with self.assertNumQueries(0):
            for event in response.context["page"]:
                self.assertEqual(list(event.participants.all()), [self.other])

    def test_html_is_escaped(self):
        Task.objects.create(title="<script>alert(1)</script>", description="<b>Example</b>", created_by=self.owner, assignee=self.owner, due_date=timezone.localdate())
        response = self.client.get("/tarefas/")
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_event_rejects_equal_times_and_javascript_url(self):
        now = timezone.now()
        equal = EventForm({"title": "Equal", "start": now, "end": now})
        self.assertFalse(equal.is_valid())
        unsafe = EventForm({"title": "Unsafe", "start": now, "end": now + timedelta(hours=1), "meeting_url": "javascript:alert(1)"})
        self.assertFalse(unsafe.is_valid())
        self.assertIn("meeting_url", unsafe.errors)

    def test_goal_rejects_nonpositive_target_and_negative_progress(self):
        payload = {"title": "Goal", "owner": self.owner.pk, "due_date": str(timezone.localdate()), "unit": "entregas"}
        for target, current, field in ((0, 0, "target"), (-1, 0, "target"), (10, -1, "current")):
            form = GoalForm({**payload, "target": target, "current": current})
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

    def test_late_mine_filter_excludes_done_and_others(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        mine = Task.objects.create(title="Mine", created_by=self.owner, assignee=self.owner, due_date=yesterday)
        Task.objects.create(title="Done", created_by=self.owner, assignee=self.owner, due_date=yesterday, status="done")
        Task.objects.create(title="Other", created_by=self.owner, assignee=self.other, due_date=yesterday)
        response = self.client.get("/tarefas/?f=mine_late")
        self.assertEqual(list(response.context["page"]), [mine])

    def test_participant_cannot_edit_event_created_by_someone_else(self):
        now = timezone.now()
        event = Event.objects.create(title="Other creator", created_by=self.other, start=now, end=now + timedelta(hours=1))
        event.participants.add(self.owner)
        self.assertEqual(self.client.post(f"/compromissos/{event.pk}/editar/", {}).status_code, 403)

    def test_csrf_is_required_for_creation_and_editing(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        task = Task.objects.create(title="Task", created_by=self.owner, assignee=self.owner, due_date=timezone.localdate())
        for path in ("/tarefas/novo/", f"/tarefas/{task.pk}/editar/", "/senha/"):
            self.assertEqual(client.post(path, {}).status_code, 403)

    def test_demo_entry_does_not_exist_in_normal_configuration(self):
        self.assertEqual(self.client.post("/demo/entrar/").status_code, 404)
        with self.assertRaises(CommandError):
            call_command("seed_demo")

    def test_login_rejects_external_next_destination(self):
        self.client.logout()
        response = self.client.post("/entrar/?next=https://example.com/", {"username": "owner", "password": "LocalTestPassword123!"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")
