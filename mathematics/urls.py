from django.urls import path
from . import views

urlpatterns=[
    path('mathematics',views.MathView.as_view,name='mathematics')
]