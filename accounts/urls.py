from django.urls import path
from . import  views


urlpatterns = [
   path('create',views.AccountView.as_view(),name='create'),
   path('login',views.LoginView.as_view(),name='login')
]