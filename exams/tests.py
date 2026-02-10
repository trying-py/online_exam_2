from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from .models import Exam


class ExamPermissionTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='inst',
            password='StrongPass123!@#',
            role='instructor',
            is_active=True,
            is_email_verified=True,
        )
        self.student = User.objects.create_user(
            username='stud',
            password='StrongPass123!@#',
            role='student',
            is_active=True,
            is_email_verified=True,
        )

    def test_instructor_can_access_exam_create(self):
        self.client.login(username='inst', password='StrongPass123!@#')
        resp = self.client.get(reverse('exams:exam_create'))
        self.assertEqual(resp.status_code, 200)

    def test_student_cannot_access_exam_create(self):
        self.client.login(username='stud', password='StrongPass123!@#')
        resp = self.client.get(reverse('exams:exam_create'))
        self.assertEqual(resp.status_code, 302)

    def test_exam_manager_by_instructor(self):
        Exam.objects.create(
            title='E1', subject='S', total_score=10,
            start_time=timezone.now(), duration_minutes=30,
            instructor=self.instructor
        )
        Exam.objects.create(
            title='E2', subject='S', total_score=10,
            start_time=timezone.now(), duration_minutes=30,
            instructor=self.student
        )
        self.assertEqual(Exam.objects.by_instructor(self.instructor).count(), 1)
