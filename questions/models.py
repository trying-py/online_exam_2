from django.db import models
from django.conf import settings
from exams.models import Exam


class QuestionQuerySet(models.QuerySet):
    def for_exam(self, exam):
        return self.filter(exam=exam)

    def mcq(self):
        return self.filter(question_type='mcq')

    def short(self):
        return self.filter(question_type='short')

    def file(self):
        return self.filter(question_type='file')


class QuestionManager(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def for_exam(self, exam):
        return self.get_queryset().for_exam(exam)

    def mcq(self):
        return self.get_queryset().mcq()


class AnswerQuerySet(models.QuerySet):
    def for_student(self, student):
        return self.filter(student=student)

    def for_exam(self, exam):
        return self.filter(question__exam=exam)


class AnswerManager(models.Manager):
    def get_queryset(self):
        return AnswerQuerySet(self.model, using=self._db)

    def for_student(self, student):
        return self.get_queryset().for_student(student)

    def for_exam(self, exam):
        return self.get_queryset().for_exam(exam)


class Question(models.Model):
    QUESTION_TYPES = [
        ('short', 'پاسخ کوتاه'),
        ('mcq', 'چندگزینه‌ای'),
        ('file', 'فایل‌دار'),
    ]

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    score = models.IntegerField(default=1)

    objects = QuestionManager()

    def __str__(self):
        return self.text[:50]


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    text = models.TextField(blank=True, null=True)

    file_upload = models.FileField(
        upload_to='answers/',
        blank=True,
        null=True
    )

    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='answers'
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    objects = AnswerManager()

    class Meta:
        unique_together = ('question', 'student')

    def __str__(self):
        return f"{self.student.username} → سؤال #{self.question_id}"

    @property
    def auto_score(self) -> int:
        """Auto grading for MCQ questions only."""
        if self.question.question_type == 'mcq' and self.selected_choice:
            return self.question.score if self.selected_choice.is_correct else 0
        return 0

    def clean(self):
        from django.core.exceptions import ValidationError

        qtype = self.question.question_type

        if qtype == 'mcq':
            if not self.selected_choice:
                raise ValidationError(
                    "برای سؤال چندگزینه‌ای باید یک گزینه انتخاب شود.")
        elif qtype == 'short':
            if not self.text:
                raise ValidationError(
                    "برای سؤال کوتاه باید متن پاسخ وارد شود.")
        elif qtype == 'file':
            if not self.file_upload:
                raise ValidationError(
                    "برای سؤال فایل‌دار باید فایل بارگذاری شود.")
