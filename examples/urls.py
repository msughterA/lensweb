from django.urls import path
from . import views


urlpatterns = [
    path("examples", views.UserView.as_view(), name="examples"),
    path("deletequestion", views.DeleteQuestionView.as_view()),
]
