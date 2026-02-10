from django.shortcuts import render, redirect, get_object_or_404
from .models import Question, Choice, Answer
from .forms import QuestionForm
from exams.models import Exam
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import instructor_required, student_required, email_verified_required
import logging


logger = logging.getLogger("app")


def question_list(request):
    questions = Question.objects.select_related(
        'exam').prefetch_related('choices').all().order_by('id')
    return render(request, 'questions/question_list.html', {'questions': questions})


def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    choices = question.choices.all()
    return render(request, 'questions/question_detail.html', {'question': question, 'choices': choices})


@login_required
@email_verified_required
@instructor_required
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, user=request.user)
        if form.is_valid():
            q = form.save()
            messages.success(request, 'سؤال ذخیره شد.')
            return redirect('questions:question_detail', question_id=q.id)
    else:
        form = QuestionForm(user=request.user)
    return render(request, 'questions/question_form.html', {'form': form})


@login_required
@email_verified_required
@instructor_required
def question_create_for_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, instructor=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST, user=request.user)
        # force exam
        if form.is_valid():
            q = form.save(commit=False)
            q.exam = exam
            q.save()
            messages.success(request, 'سؤال ذخیره شد.')
            return redirect('exams:exam_detail', exam_id=exam.id)
    else:
        form = QuestionForm(user=request.user, initial={'exam': exam})
    return render(request, 'questions/question_form.html', {'form': form})


@login_required
@email_verified_required
@student_required
def take_exam(request, exam_id):
    logger.info("take_exam accessed exam_id=%s by user=%s",
                exam_id, request.user.username)
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all().order_by('id')

    if request.method == 'POST':
        for question in questions:
            field_name = f"question_{question.id}"

            if question.question_type == 'mcq':
                selected_choice_id = request.POST.get(field_name)
                if selected_choice_id:
                    try:
                        choice = Choice.objects.get(
                            id=selected_choice_id, question=question)
                    except Choice.DoesNotExist:
                        choice = None
                else:
                    choice = None

                Answer.objects.update_or_create(
                    question=question,
                    student=request.user,
                    defaults={'selected_choice': choice,
                              'text': '', 'file_upload': None}
                )

            elif question.question_type == 'short':
                text_answer = request.POST.get(field_name, '').strip()
                if text_answer:
                    Answer.objects.update_or_create(
                        question=question,
                        student=request.user,
                        defaults={'text': text_answer,
                                  'selected_choice': None, 'file_upload': None}
                    )

            elif question.question_type == 'file':
                file_answer = request.FILES.get(field_name)
                if file_answer:
                    Answer.objects.update_or_create(
                        question=question,
                        student=request.user,
                        defaults={'file_upload': file_answer,
                                  'text': '', 'selected_choice': None}
                    )

        messages.success(request, 'پاسخ‌ها ارسال شد.')
        return render(request, 'questions/exam_submitted.html', {'exam': exam})

    return render(request, 'questions/take_exam.html', {'exam': exam, 'questions': questions})
