from django.contrib import admin
from .models import Exam

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'total_score', 'start_time', 'duration_minutes', 'instructor')
    search_fields = ('title', 'subject', 'instructor__username')
    list_filter = ('subject',)