from django.urls import path
from . import views


urlpatterns=[
    path('gst',views.GstView.as_view(),name='gst')
]