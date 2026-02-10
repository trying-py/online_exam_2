from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('create/', views.exam_create, name='exam_create'),
    path('<int:exam_id>/', views.exam_detail, name='exam_detail'),
]
