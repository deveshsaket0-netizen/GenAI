from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate/', views.generate, name='generate'),
    path('quiz/', views.quiz, name='quiz'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('revision-plan/', views.revision_plan, name='revision_plan'),
]