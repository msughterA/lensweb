from django.urls import path
from . import  views


urlpatterns = [
   path('summarize',views.SummarizerView.as_view(),name='summarize')
]