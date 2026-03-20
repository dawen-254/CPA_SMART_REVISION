from django.contrib import admin
from .models import StudyTask

@admin.register(StudyTask)
class StudyTaskAdmin(admin.ModelAdmin):
    list_display = ("student", "topic", "scheduled_date", "task_type", "is_completed")
    list_filter = ("student", "scheduled_date", "task_type", "is_completed")
    search_fields = ("student__full_name", "student__email", "topic__title")
    ordering = ("-scheduled_date",)
