from django.urls import path
from . import views

app_name = "planner"

urlpatterns = [
    path("dashboard/", views.planner_dashboard, name="dashboard"),
    path("set-exam-date/", views.set_exam_date, name="set_exam_date"),
    path("regenerate/", views.regenerate_schedule, name="regenerate"),
    path("toggle-task/<int:task_id>/", views.toggle_task, name="toggle_task"),
]
