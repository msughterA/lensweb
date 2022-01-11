from django.urls import path
from . import  views


urlpatterns = [
    path('',views.index,name='index'),
    path('adminlogin',views.adminLogin,name='adminlogin'),
    path('adminupload',views.adminUpload,name='adminupload'),
    path('examples',views.UserView.as_view(),name='examples')
]