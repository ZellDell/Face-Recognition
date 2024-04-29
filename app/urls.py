from django.urls import path

from . import views

urlpatterns = [
   
    path('', views.home, name='home'),
    path('students/', views.students, name='students'),
    path('delete_student/', views.delete_student, name='delete_student'),
    path('get_student_info/', views.get_student_info, name='get_student_info'),



    path('professors/', views.professors, name='professors'),
    path('add_subject/', views.add_subject, name='add_subject'),
    path('delete_professor/', views.delete_professor, name='delete_professor'),


    path('attendance/', views.attendance, name='attendance'),
    path('check_attendance/', views.check_attendance, name='check_attendance'),

    path('process_frame/', views.process_frame, name='process_frame'),

    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
]