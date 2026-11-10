"""Create deterministic fictional records; never reset or touch real records."""
from datetime import datetime, time, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from core.models import User, Task, Event, Goal, Notice


class Command(BaseCommand):
    help = "Prepara dados fictícios na base SQLite exclusiva da demonstração."

    @transaction.atomic
    def handle(self, *args, **options):
        if not getattr(settings, "DEMO_MODE", False):
            raise CommandError("seed_demo exige config.demo_settings. Produção não foi alterada.")
        db = settings.DATABASES["default"]
        if db["ENGINE"] != "django.db.backends.sqlite3":
            raise CommandError("A demonstração exige a base SQLite isolada.")
        usernames = {settings.DEMO_USERNAME, "demo-lia", "demo-caio"}
        if User.objects.exclude(username__in=usernames).exists():
            raise CommandError("Base com usuários não reconhecidos. Nada foi modificado.")
        for model in (Task, Event, Goal, Notice):
            if model.objects.exclude(title__startswith="[Demo] ").exists():
                raise CommandError("Base com registros não reconhecidos. Nada foi modificado.")

        users = {}
        for username, name in (
            (settings.DEMO_USERNAME, "Visitante"),
            ("demo-lia", "Lia"),
            ("demo-caio", "Caio"),
        ):
            user, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    "first_name": name, "last_name": "Exemplo",
                    "email": "", "is_active": True,
                    "is_staff": False, "is_superuser": False,
                },
            )
            user.set_unusable_password()
            user.save(update_fields=["password"])
            users[username] = user
        visitor = users[settings.DEMO_USERNAME]
        today = timezone.localdate()
        for title, assignee, offset, status, priority in (
            ("Revisar briefing da campanha", visitor, -1, "doing", "high"),
            ("Preparar proposta visual", visitor, 2, "todo", "normal"),
            ("Organizar calendário editorial", users["demo-lia"], 3, "doing", "normal"),
            ("Conferir publicação de exemplo", visitor, -2, "done", "normal"),
            ("Revisar checklist de entrega", users["demo-caio"], 5, "todo", "high"),
        ):
            Task.objects.update_or_create(
                title="[Demo] " + title,
                defaults={
                    "created_by": visitor, "assignee": assignee,
                    "due_date": today + timedelta(days=offset),
                    "status": status, "priority": priority,
                    "description": "Exemplo fictício para demonstrar organização de trabalho.",
                    "notes": "Dados de demonstração. Não representa uma entrega ou cliente real.",
                },
            )
        for title, offset, hour in (
            ("Alinhamento da semana", 1, 10),
            ("Revisão das entregas", 3, 14),
        ):
            start = timezone.make_aware(datetime.combine(today + timedelta(days=offset), time(hour)))
            event, _ = Event.objects.update_or_create(
                title="[Demo] " + title,
                defaults={
                    "created_by": visitor, "description": "Reunião fictícia.",
                    "start": start, "end": start + timedelta(minutes=45),
                    "location": "Sala de demonstração", "meeting_url": "",
                },
            )
            event.participants.set(users.values())
        Goal.objects.update_or_create(
            title="[Demo] Entregas do ciclo",
            defaults={
                "created_by": visitor, "owner": visitor, "target": 10,
                "current": 6, "unit": "entregas",
                "description": "Progresso fictício usado para demonstrar o cálculo percentual.",
                "due_date": today + timedelta(days=14),
            },
        )
        for title, description in (
            ("Bem-vindo à demonstração", "Todos os nomes e registros deste ambiente são fictícios. A navegação é somente leitura."),
            ("Como explorar", "Veja as tarefas, use os filtros, confira a agenda e acompanhe o progresso da meta."),
        ):
            Notice.objects.update_or_create(
                title="[Demo] " + title,
                defaults={"created_by": visitor, "description": description},
            )
        self.stdout.write(self.style.SUCCESS("Demonstração preparada: 3 pessoas fictícias, 5 tarefas, 2 compromissos, 1 meta e 2 comunicados."))
