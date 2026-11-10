from django.conf import settings
import calendar
from datetime import date, datetime, time, timedelta
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Task, Event, Goal, Notice
from .forms import TaskForm, EventForm, GoalForm, NoticeForm
KINDS = {"tarefas": (Task, TaskForm, "Tarefas"), "compromissos": (Event, EventForm, "Compromissos"), "metas": (Goal, GoalForm, "Metas"), "comunicados": (Notice, NoticeForm, "Comunicados")}
def spec(kind):
    if kind not in KINDS:
        raise Http404
    return KINDS[kind]
def editable(user, obj):
    if getattr(settings, "DEMO_MODE", False):
        return False
    if user.is_superuser:
        return True
    if isinstance(obj, Notice):
        return False
    return user.pk in (obj.created_by_id, getattr(obj, "assignee_id", None), getattr(obj, "owner_id", None))
@login_required
def dashboard(request):
    tasks = Task.objects.filter(assignee=request.user).exclude(status="done")
    return render(request, "dashboard.html", {"tasks": tasks[:5], "task_count": tasks.count(), "late_count": tasks.filter(due_date__lt=timezone.localdate()).count(), "events": Event.objects.filter(end__gte=timezone.now())[:5], "goals": Goal.objects.filter(owner=request.user)[:5], "notices": Notice.objects.all()[:3]})
@login_required
def list_view(request, kind):
    model, _, title = spec(kind)
    items = model.objects.all()
    if kind == "tarefas":
        items = items.select_related("assignee")
        selected = request.GET.get("f", "all")
        if selected in ("mine", "mine_late"): items = items.filter(assignee=request.user)
        if selected in ("late", "mine_late"): items = items.filter(due_date__lt=timezone.localdate()).exclude(status="done")
        if selected == "done": items = items.filter(status="done")
    if kind == "metas": items = items.select_related("owner")
    if kind == "compromissos": items = items.prefetch_related("participants")
    page = Paginator(items, 30).get_page(request.GET.get("page"))
    for obj in page: obj.can_edit = editable(request.user, obj)
    return render(request, "list.html", {"kind": kind, "title": title, "page": page, "can_create": not getattr(settings, "DEMO_MODE", False) and (kind != "comunicados" or request.user.is_superuser)})
@login_required
def edit_view(request, kind, pk=None):
    model, form_cls, title = spec(kind)
    obj = get_object_or_404(model, pk=pk) if pk else None
    if (obj and not editable(request.user, obj)) or (kind == "comunicados" and not request.user.is_superuser):
        raise PermissionDenied
    form = form_cls(request.POST if request.method == "POST" else None, instance=obj)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        if not obj: item.created_by = request.user
        item.save()
        form.save_m2m()
        return redirect("list", kind=kind)
    return render(request, "form.html", {"form": form, "title": ("Editar • " if obj else "Novo • ") + title})
@login_required
def delete_view(request, kind, pk):
    model, _, _ = spec(kind)
    obj = get_object_or_404(model, pk=pk)
    if not editable(request.user, obj): raise PermissionDenied
    if request.method == "POST":
        obj.delete()
        return redirect("list", kind=kind)
    return render(request, "delete.html", {"item": obj})
@login_required
def calendar_view(request):
    today = timezone.localdate()
    try:
        first = date.fromisoformat(request.GET.get("mes", today.replace(day=1).isoformat())).replace(day=1)
        if not 2000 <= first.year <= 2100: raise ValueError
    except ValueError: first = today.replace(day=1)
    last = (first.replace(day=28) + timedelta(days=4)).replace(day=1)
    grid = calendar.Calendar().monthdatescalendar(first.year, first.month)
    begin = timezone.make_aware(datetime.combine(grid[0][0], time.min))
    end = timezone.make_aware(datetime.combine(grid[-1][-1] + timedelta(days=1), time.min))
    events = list(Event.objects.filter(start__lt=end, end__gt=begin))
    weeks = []
    for week in grid:
        cells = []
        for day in week:
            day_start = timezone.make_aware(datetime.combine(day, time.min))
            day_end = timezone.make_aware(datetime.combine(day + timedelta(days=1), time.min))
            cells.append({"date": day, "in_month": day.month == first.month, "events": [e for e in events if e.start < day_end and e.end > day_start]})
        weeks.append(cells)
    return render(request, "calendar.html", {"weeks": weeks, "month": first, "previous": (first-timedelta(days=1)).replace(day=1).isoformat(), "next": last.isoformat()})
