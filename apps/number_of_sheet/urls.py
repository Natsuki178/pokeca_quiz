from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("question_image/", views.question_image, name="question_image"),
]
