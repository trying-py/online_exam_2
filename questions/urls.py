from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('create/', views.question_create, name='question_create'),
    path('create/<int:exam_id>/', views.question_create_for_exam, name='question_create_for_exam'),
    path('take/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('detail/<int:question_id>/', views.question_detail, name='question_detail'),
]
