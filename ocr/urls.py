from django.urls import path
from . import views

urlpatterns = [path("", views.OCRView.as_view(), name="ocr")]
