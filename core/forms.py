from django import forms
from .models import Task, Event, Goal, Notice, User
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "assignee", "due_date", "priority", "status", "notes"]
        widgets = {"due_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})}
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "start", "end", "participants", "location", "meeting_url"]
        widgets = {x: forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}) for x in ("start", "end")}
        widgets["participants"] = forms.CheckboxSelectMultiple()
class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["title", "description", "owner", "due_date", "target", "current", "unit"]
        widgets = {"due_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})}
class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ["title", "description"]
