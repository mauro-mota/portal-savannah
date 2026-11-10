from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
class User(AbstractUser):
    def __str__(self):
        return self.get_full_name() or self.username
class Record(models.Model):
    title = models.CharField("Título", max_length=180)
    description = models.TextField("Descrição / informações", blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="%(class)s_created", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True
        ordering = ["-created_at"]
    def __str__(self):
        return self.title
class Task(Record):
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Responsável", on_delete=models.PROTECT)
    due_date = models.DateField("Prazo")
    status = models.CharField("Situação", max_length=12, choices=[("todo", "A fazer"), ("doing", "Em andamento"), ("done", "Concluída")], default="todo")
    priority = models.CharField("Prioridade", max_length=8, choices=[("normal", "Normal"), ("high", "Alta")], default="normal")
    notes = models.TextField("Atualizações / andamento", blank=True)
    class Meta:
        ordering = ["due_date", "pk"]
        verbose_name = "tarefa"
class Event(Record):
    start = models.DateTimeField("Começa em")
    end = models.DateTimeField("Termina em")
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name="Participantes", blank=True)
    location = models.CharField("Local", max_length=180, blank=True)
    meeting_url = models.URLField("Link da reunião (https://...)", blank=True)
    def clean(self):
        if self.start and self.end and self.end <= self.start:
            raise ValidationError("O fim precisa ser depois do início.")
    class Meta:
        ordering = ["start"]
        verbose_name = "compromisso"
class Goal(Record):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Responsável", on_delete=models.PROTECT)
    due_date = models.DateField("Prazo")
    target = models.DecimalField("Valor da meta", max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    current = models.DecimalField("Valor atingido", max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    unit = models.CharField("Unidade (vendas, R$, entregas...)", max_length=30, default="entregas")
    @property
    def percent(self):
        return round(self.current / self.target * 100) if self.target else 0
    class Meta:
        ordering = ["due_date"]
        verbose_name = "meta"
class Notice(Record):
    class Meta:
        verbose_name = "comunicado"
        ordering = ["-created_at"]
