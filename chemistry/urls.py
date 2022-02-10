from django.urls import path
from . import views

urlpatterns=[
    path('chemistry',views.ChemistryView.as_view(),name='chemistry')
]