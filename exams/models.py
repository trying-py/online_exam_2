from django.db import models
from django.conf import settings
from django.utils import timezone


class ExamQuerySet(models.QuerySet):
    def by_instructor(self, instructor):
        return self.filter(instructor=instructor)

    def upcoming(self):
        return self.filter(start_time__gte=timezone.now()).order_by('start_time')

    def past(self):
        return self.filter(start_time__lt=timezone.now()).order_by('-start_time')


class ExamManager(models.Manager):
    def get_queryset(self):
        return ExamQuerySet(self.model, using=self._db)

    def by_instructor(self, instructor):
        return self.get_queryset().by_instructor(instructor)

    def upcoming(self):
        return self.get_queryset().upcoming()

    def past(self):
        return self.get_queryset().past()


class Exam(models.Model):
    title = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    total_score = models.IntegerField()
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField()

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exams_created'
    )

    objects = ExamManager()

    def __str__(self):
        return self.title
