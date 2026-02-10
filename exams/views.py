from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import instructor_required, email_verified_required
from .models import Exam
from .forms import ExamForm
import logging


logger = logging.getLogger("app")


@login_required
@email_verified_required
@instructor_required
def exam_create(request):

    if request.method == 'POST':
        logger.info("exam_create POST by user=%s", request.user.username)
        form = ExamForm(request.POST)

        if form.is_valid():
            exam = form.save(commit=False)
            exam.instructor = request.user
            exam.save()
            return redirect('exams:exam_list')
    else:
        form = ExamForm()
    return render(request, 'exams/exam_form.html', {'form': form})


def exam_list(request):
    exams = Exam.objects.all().order_by('-start_time')
    logger.info("exam_list viewed by user=%s",
                request.user if request.user.is_authenticated else "anonymous")
    return render(request, 'exams/exam_list.html', {'exams': exams})


def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    questions = exam.questions.all().order_by('id')
    return render(request, 'exams/exam_detail.html', {'exam': exam, 'questions': questions})
