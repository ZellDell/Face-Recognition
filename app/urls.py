from django.urls import path

from . import views

urlpatterns = [
   
    path('', views.home, name='home'),

    path('process_frame/', views.process_frame, name='process_frame'),

    path('login/', views.user_login, name='login'),
    
]