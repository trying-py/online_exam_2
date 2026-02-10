from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from exams.models import Exam
from .models import Question


class QuestionAndTakeExamTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='inst2', password='StrongPass123!@#', role='instructor',
            is_active=True, is_email_verified=True,
        )
        self.student = User.objects.create_user(
            username='stud2', password='StrongPass123!@#', role='student',
            is_active=True, is_email_verified=True,
        )
        self.exam = Exam.objects.create(
            title='Exam', subject='Math', total_score=10,
            start_time=timezone.now(), duration_minutes=10,
            instructor=self.instructor
        )
        self.q = Question.objects.create(
            exam=self.exam, text='Q1', question_type='short', score=1
        )

    def test_student_can_take_exam(self):
        self.client.login(username='stud2', password='StrongPass123!@#')
        resp = self.client.get(reverse('questions:take_exam', kwargs={'exam_id': self.exam.id}))
        self.assertEqual(resp.status_code, 200)

    def test_instructor_cannot_take_exam(self):
        self.client.login(username='inst2', password='StrongPass123!@#')
        resp = self.client.get(reverse('questions:take_exam', kwargs={'exam_id': self.exam.id}))
        self.assertEqual(resp.status_code, 302)

    def test_question_manager_for_exam(self):
        self.assertEqual(Question.objects.for_exam(self.exam).count(), 1)
