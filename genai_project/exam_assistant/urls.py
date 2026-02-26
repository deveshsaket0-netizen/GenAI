from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("profile-settings/", views.profile_settings, name="profile_settings"),
    path("generate/", views.generate, name="generate"),
    path("quiz/<int:session_id>/", views.quiz, name="quiz"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("mind-map/", views.mind_map, name="mind_map"),
    path("revision-plan/", views.revision_plan, name="revision_plan"),
]
